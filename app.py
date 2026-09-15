import threading, json, csv, io, datetime, math
from collections import deque
from contextlib import contextmanager
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import paho.mqtt.client as mqtt
import psycopg2
from qdrant_client import QdrantClient
from clip_embed import embed_text
from auth import verify_login, create_session, get_session, destroy_session

app = FastAPI()
alerts = deque(maxlen=100)
qdrant = QdrantClient(host="localhost", port=6333)
camera_last_seen = {}
HEARTBEAT_STALE_SECONDS = 20
SESSION_COOKIE = "sentinel_session"
PUBLIC_PATHS = {"/login.html", "/login"}
MAX_LIMIT = 500

def db():
    return psycopg2.connect(host="localhost", port=5432, dbname="sentinel", user="sentinel", password="sentinel")

@contextmanager
def db_cursor(commit=False):
    """Always closes the connection, even if the query raises - avoids leaking
    Postgres connections on bad input or query errors."""
    conn = db()
    try:
        cur = conn.cursor()
        yield cur
        if commit:
            conn.commit()
    finally:
        conn.close()

def log_audit(username, action, details=""):
    with db_cursor(commit=True) as cur:
        cur.execute("INSERT INTO audit_log (username, action, details) VALUES (%s,%s,%s)", (username, action, details))

def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))

def bearing_deg(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)
    x = math.sin(dlambda) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dlambda)
    return math.degrees(math.atan2(x, y)) % 360

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in PUBLIC_PATHS:
            return await call_next(request)
        session = get_session(request.cookies.get(SESSION_COOKIE))
        if not session:
            if path == "/" or path.endswith(".html"):
                return RedirectResponse("/login.html")
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        request.state.user = session
        return await call_next(request)

app.add_middleware(AuthMiddleware)

def load_camera_positions():
    with db_cursor() as cur:
        cur.execute("SELECT id, lat, lon FROM cameras")
        rows = cur.fetchall()
    return {r[0]: (float(r[1]), float(r[2])) for r in rows}

camera_positions = load_camera_positions()

def save_event(alert):
    lat, lon = camera_positions.get(alert.get("camera"), (None, None))
    subject = alert.get("matched_plate") or alert.get("matched_name")
    with db_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO events (plate, camera, lat, lon, reason, source, score, time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (subject, alert.get("camera"), lat, lon,
             alert.get("reason"), alert.get("source"), alert.get("score"), alert.get("time")),
        )

def on_connect(client, userdata, flags, reason_code, properties=None):
    client.subscribe("sentinel/alerts")
    client.subscribe("sentinel/heartbeat")

def on_message(client, userdata, msg):
    try:
        if msg.topic == "sentinel/heartbeat":
            hb = json.loads(msg.payload.decode())
            camera_last_seen[hb["camera"]] = hb["time"]
            return
        alert = json.loads(msg.payload.decode())
        alerts.appendleft(alert)
        save_event(alert)
    except Exception as e:
        print("bad message:", e)

def mqtt_thread():
    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    c.on_connect = on_connect
    c.on_message = on_message
    c.connect("localhost", 1883, 60)
    c.loop_forever()

threading.Thread(target=mqtt_thread, daemon=True).start()

@app.post("/login")
async def login(request: Request):
    body = await request.json()
    username = body.get("username", "")
    password = body.get("password", "")
    role = verify_login(username, password)
    if not role:
        log_audit(username, "login_failed")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_session(username, role)
    log_audit(username, "login")
    response = JSONResponse({"username": username, "role": role})
    response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax", max_age=8 * 60 * 60)
    return response

@app.post("/logout")
def logout(request: Request):
    user = getattr(request.state, "user", None)
    if user:
        log_audit(user["username"], "logout")
    destroy_session(request.cookies.get(SESSION_COOKIE))
    response = JSONResponse({"ok": True})
    response.delete_cookie(SESSION_COOKIE)
    return response

@app.get("/me")
def me(request: Request):
    user = request.state.user
    return {"username": user["username"], "role": user["role"]}

@app.get("/audit")
def get_audit(request: Request, limit: int = 200):
    if request.state.user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    with db_cursor() as cur:
        cur.execute("SELECT username, action, details, time FROM audit_log ORDER BY time DESC LIMIT %s", (min(limit, MAX_LIMIT),))
        rows = cur.fetchall()
    return [{"username": r[0], "action": r[1], "details": r[2], "time": r[3].isoformat()} for r in rows]

@app.get("/cameras")
def cameras():
    with db_cursor() as cur:
        cur.execute("SELECT id, name, lat, lon, rtsp_url FROM cameras")
        rows = cur.fetchall()
    now = datetime.datetime.now()
    out = []
    for r in rows:
        cam_id = r[0]
        last_seen = camera_last_seen.get(cam_id)
        online = False
        if last_seen:
            age = (now - datetime.datetime.fromisoformat(last_seen)).total_seconds()
            online = age <= HEARTBEAT_STALE_SECONDS
        out.append({
            "id": cam_id, "name": r[1], "lat": float(r[2]), "lon": float(r[3]),
            "rtsp_url": r[4], "status": "online" if online else "offline",
            "last_seen": last_seen,
        })
    return out

@app.post("/cameras/upload")
def upload_cameras(request: Request, file: UploadFile = File(...)):
    if request.state.user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    content = file.file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    required = {"id", "name", "lat", "lon"}
    count = 0
    errors = []
    with db_cursor(commit=True) as cur:
        for i, row in enumerate(reader, start=2):  # row 1 is the header
            missing = required - row.keys()
            if missing or not row.get("id") or not row.get("name"):
                errors.append(f"row {i}: missing/empty required column(s) {missing or {'id/name'}}")
                continue
            try:
                lat, lon = float(row["lat"]), float(row["lon"])
            except (TypeError, ValueError):
                errors.append(f"row {i}: lat/lon is not a number")
                continue
            cur.execute(
                """INSERT INTO cameras (id, name, lat, lon, rtsp_url) VALUES (%s,%s,%s,%s,%s)
                   ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, lat=EXCLUDED.lat,
                   lon=EXCLUDED.lon, rtsp_url=EXCLUDED.rtsp_url""",
                (row["id"], row["name"], lat, lon, row.get("rtsp_url") or None),
            )
            count += 1
    global camera_positions
    camera_positions = load_camera_positions()
    log_audit(request.state.user["username"], "cameras_upload", f"{count} rows, {len(errors)} skipped")
    return {"inserted_or_updated": count, "skipped": len(errors), "errors": errors}

@app.get("/alerts")
def get_alerts():
    return list(alerts)

@app.get("/events")
def get_events(plate: str | None = None, limit: int = 200):
    limit = min(limit, MAX_LIMIT)
    with db_cursor() as cur:
        if plate:
            cur.execute(
                "SELECT plate, camera, lat, lon, reason, source, score, time FROM events WHERE plate = %s ORDER BY time DESC LIMIT %s",
                (plate, limit),
            )
        else:
            cur.execute(
                "SELECT plate, camera, lat, lon, reason, source, score, time FROM events ORDER BY time DESC LIMIT %s",
                (limit,),
            )
        rows = cur.fetchall()
    return [
        {"plate": r[0], "camera": r[1], "lat": r[2], "lon": r[3], "reason": r[4],
         "source": r[5], "score": r[6], "time": r[7].isoformat()}
        for r in rows
    ]

@app.get("/search")
def search(q: str, limit: int = 12, camera: str | None = None):
    limit = min(limit, 50)
    vector = embed_text(q)
    query_filter = None
    if camera:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        query_filter = Filter(must=[FieldCondition(key="camera", match=MatchValue(value=camera))])
    hits = qdrant.query_points(
        collection_name="detections", query=vector, limit=limit, query_filter=query_filter
    ).points
    return [
        {"score": round(h.score, 3), "camera": h.payload.get("camera"),
         "class": h.payload.get("class"), "time": h.payload.get("time"),
         "thumb": h.payload.get("thumb")}
        for h in hits
    ]

@app.get("/predict")
def predict(plate: str, limit: int = 2):
    limit = min(limit, 20)
    with db_cursor() as cur:
        cur.execute(
            """SELECT camera, lat, lon, time FROM events
               WHERE plate = %s AND lat IS NOT NULL AND lon IS NOT NULL ORDER BY time ASC""",
            (plate,),
        )
        sightings = cur.fetchall()
        cur.execute("SELECT id, name, lat, lon FROM cameras")
        cam_rows = cur.fetchall()

    path = [{"camera": r[0], "lat": float(r[1]), "lon": float(r[2]), "time": r[3].isoformat()} for r in sightings]
    all_cameras = [{"id": r[0], "name": r[1], "lat": float(r[2]), "lon": float(r[3])} for r in cam_rows]
    if not path:
        return {"predicted": [], "path": []}

    visited = {p["camera"] for p in path}
    last = path[-1]
    candidates = [c for c in all_cameras if c["id"] not in visited]
    have_direction = len(path) >= 2

    scored = []
    for c in candidates:
        dist_km = haversine_km(last["lat"], last["lon"], c["lat"], c["lon"])
        closeness = 1 / (1 + dist_km)
        if have_direction:
            prev = path[-2]
            travel_bearing = bearing_deg(prev["lat"], prev["lon"], last["lat"], last["lon"])
            cam_bearing = bearing_deg(last["lat"], last["lon"], c["lat"], c["lon"])
            # cosine similarity of the two bearings, rescaled 0..1 (1 = straight ahead)
            alignment = (math.cos(math.radians(cam_bearing - travel_bearing)) + 1) / 2
            score = 0.6 * alignment + 0.4 * closeness
        else:
            score = closeness  # no direction yet - just favor the nearest camera
        eta_min = dist_km / 40 * 60  # assume ~40 km/h average city traffic speed
        scored.append({
            "camera_id": c["id"], "name": c["name"], "lat": c["lat"], "lon": c["lon"],
            "score": round(score, 3), "eta_min": round(eta_min, 1),
        })
    scored.sort(key=lambda x: -x["score"])
    return {"predicted": scored[:limit], "path": path}

@app.post("/dispatch")
async def dispatch_drone(request: Request):
    body = await request.json()
    target = body.get("target", "")
    log_audit(request.state.user["username"], "drone_dispatch", target)
    return {"ok": True}

app.mount("/", StaticFiles(directory="static", html=True), name="static")
