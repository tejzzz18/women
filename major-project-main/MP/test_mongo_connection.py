# test_mongo_connection.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DBNAME", "mahila_reports")

print("🔍 Checking MongoDB Connection...")
if not MONGO_URI:
    print("❌ MONGO_URI not set in .env")
    raise SystemExit(1)

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    info = client.server_info()
    print("✅ Connected. MongoDB version:", info.get("version"))
    db = client[DB_NAME]
    count = db.reports.count_documents({})
    print(f"📁 Database '{DB_NAME}' reachable. reports collection count: {count}")
except Exception as e:
    print("❌ Connection failed:", str(e))
