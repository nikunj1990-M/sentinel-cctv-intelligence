import psycopg2

conn = psycopg2.connect(host="localhost", port=5432, dbname="sentinel", user="sentinel", password="sentinel")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS watchlist (id SERIAL PRIMARY KEY, plate TEXT, reason TEXT, source TEXT)")
cur.execute("""CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    plate TEXT,
    camera TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    reason TEXT,
    source TEXT,
    score REAL,
    time TIMESTAMPTZ DEFAULT now()
)""")
cur.execute("""CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    username TEXT,
    action TEXT,
    details TEXT,
    time TIMESTAMPTZ DEFAULT now()
)""")
cur.execute("TRUNCATE watchlist")
vehicles = [
    ("GJ18BT7448", "Stolen vehicle", "VAHAN"),
    ("GJ01AB1234", "Wanted suspect vehicle", "eGujCop"),
    ("MH12XY9999", "Blacklisted vehicle", "VAHAN"),
]
for plate, reason, source in vehicles:
    cur.execute("INSERT INTO watchlist (plate, reason, source) VALUES (%s, %s, %s)", (plate, reason, source))
conn.commit()
cur.execute("SELECT plate, reason, source FROM watchlist")
print("Watchlist seeded:")
for r in cur.fetchall():
    print("  ", r)
cur.close(); conn.close()
