import psycopg2
conn = psycopg2.connect(host="localhost", port=5432, dbname="sentinel", user="sentinel", password="sentinel")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS cameras (id TEXT PRIMARY KEY, name TEXT, lat DOUBLE PRECISION, lon DOUBLE PRECISION, rtsp_url TEXT)")
cur.execute("ALTER TABLE cameras ADD COLUMN IF NOT EXISTS rtsp_url TEXT")
cur.execute("TRUNCATE cameras")
cams = [
    ("cam1", "Sector 18, Gandhinagar (SCRB)", 23.2230, 72.6500, "rtsp://localhost:8554/cam1"),
    ("cam2", "Gandhinagar Central", 23.2156, 72.6369, "rtsp://localhost:8554/cam2"),
    ("cam3", "Ahmedabad - CG Road", 23.0300, 72.5600, "rtsp://localhost:8554/cam3"),
    ("cam4", "Ahmedabad - Airport Circle", 23.0770, 72.6340, "rtsp://localhost:8554/cam4"),
    ("cam5", "Adalaj Circle", 23.1650, 72.5810, "rtsp://localhost:8554/cam5"),
]
for c in cams:
    cur.execute("INSERT INTO cameras (id, name, lat, lon, rtsp_url) VALUES (%s,%s,%s,%s,%s)", c)
conn.commit()
cur.execute("SELECT * FROM cameras")
for r in cur.fetchall(): print(r)
cur.close(); conn.close()
