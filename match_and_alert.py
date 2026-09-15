import sys, json, datetime
import psycopg2
import paho.mqtt.publish as publish
from rapidfuzz import fuzz

def normalize(p):
    return "".join(ch for ch in p.upper() if ch.isalnum())

read_plate = sys.argv[1] if len(sys.argv) > 1 else "GJ18TT448"
camera = sys.argv[2] if len(sys.argv) > 2 else "cam1"

conn = psycopg2.connect(host="localhost", port=5432, dbname="sentinel", user="sentinel", password="sentinel")
cur = conn.cursor()
cur.execute("SELECT plate, reason, source FROM watchlist")
rows = cur.fetchall()
cur.close(); conn.close()

p = normalize(read_plate)
best, best_score = None, 0
for row in rows:
    s = fuzz.ratio(p, normalize(row[0]))
    if s > best_score:
        best_score, best = s, row

print("Read plate:", read_plate, "| best match:", best[0] if best else None, "| score:", round(best_score, 1))

if best and best_score >= 75:
    alert = {
        "type": "WATCHLIST_HIT",
        "read_plate": read_plate,
        "matched_plate": best[0],
        "reason": best[1],
        "source": best[2],
        "score": round(best_score, 1),
        "camera": camera,
        "time": datetime.datetime.now().isoformat(),
    }
    publish.single("sentinel/alerts", json.dumps(alert), hostname="localhost", port=1883)
    print("ALERT PUBLISHED")
else:
    print("No match above threshold.")
