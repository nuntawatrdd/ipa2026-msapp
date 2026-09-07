import os
from datetime import datetime, timezone
from pymongo import MongoClient

def save_router_interfaces(router_ip, interfaces):
    mongo_uri = os.environ.get("MONGO_URI")
    db_name = os.environ.get("DB_NAME", "IPA_2026_S3")

    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db["Router_Interfaces"]

    record = {
        "ip": router_ip,
        "interfaces": interfaces,
        "timestamp": datetime.now(timezone.utc)
    }

    collection.update_one(
        {"ip": router_ip},
        {"$set": record},
        upsert=True
    )
