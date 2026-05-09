from datetime import datetime, timezone
from typing import Any

import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from config import settings


class MongoLibrary:
    def __init__(self, phone_number: str) -> None:
        self.phone_number = phone_number
        self.client = MongoClient(settings.mongo_uri, server_api=ServerApi('1'))
        self.user_id: str | None = self.get_user_id()
        return


    def get_user_id(self) -> None:
        return None

    def initialize_client(self):
        self.client = MongoClient(settings.mongo_uri, server_api=ServerApi('1'))
        return

    def get_database(self):
        return self.client.get_database(settings.mongo_database)

    def get_messages_collection(self):
        return self.get_database().get_collection(self.phone_number)

    def get_profiles_collection(self):
        return self.get_database().get_collection("user_profiles")

    def get_events_collection(self):
        return self.get_database().get_collection("events")

    def get_or_create_user_profile(self):
        profiles = self.get_profiles_collection()
        profile = profiles.find_one({"phone_number": self.phone_number})
        if profile:
            return profile

        now = datetime.now(timezone.utc).timestamp()
        profile = {
            "user_id": self.phone_number,
            "phone_number": self.phone_number,
            "timezone": "UTC",
            "preferences": {
                "summary_style": "adaptive",
                "daily_prompt_enabled": True,
            },
            "created_at": now,
            "updated_at": now,
        }
        profiles.insert_one(profile)
        return profile

    def update_user_profile(self, updates: dict[str, Any]):
        now = datetime.now(timezone.utc).timestamp()
        profiles = self.get_profiles_collection()
        profiles.update_one(
            {"phone_number": self.phone_number},
            {"$set": {**updates, "updated_at": now}},
            upsert=True,
        )
        return profiles.find_one({"phone_number": self.phone_number})

    def insert_event(
        self,
        event_type: str,
        payload: dict[str, Any],
        source: str = "sms",
        confidence: float = 1.0,
        tags: list[str] | None = None,
        idempotency_key: str | None = None,
    ):
        event_timestamp = datetime.now(timezone.utc).timestamp()
        event_doc = {
            "user_id": self.phone_number,
            "phone_number": self.phone_number,
            "event_type": event_type,
            "payload": payload,
            "source": source,
            "confidence": confidence,
            "timestamp": event_timestamp,
            "tags": tags or [],
        }

        events = self.get_events_collection()
        if idempotency_key:
            event_doc["idempotency_key"] = idempotency_key
            existing = events.find_one(
                {
                    "user_id": self.phone_number,
                    "idempotency_key": idempotency_key,
                }
            )
            if existing:
                return existing

        result = events.insert_one(event_doc)
        return events.find_one({"_id": result.inserted_id})

    def fetch_events_in_window(
        self,
        start_timestamp: float,
        end_timestamp: float,
        event_types: list[str] | None = None,
        limit: int = 500,
    ):
        query: dict[str, Any] = {
            "user_id": self.phone_number,
            "timestamp": {"$gte": start_timestamp, "$lte": end_timestamp},
        }
        if event_types:
            query["event_type"] = {"$in": event_types}

        events = self.get_events_collection()
        cursor = events.find(query).sort("timestamp", pymongo.ASCENDING).limit(limit)
        return list(cursor)

    def aggregate_events_weekly(self, end_timestamp: float | None = None):
        week_end = end_timestamp or datetime.now(timezone.utc).timestamp()
        week_start = week_end - (7 * 24 * 60 * 60)
        events = self.get_events_collection()

        pipeline = [
            {
                "$match": {
                    "user_id": self.phone_number,
                    "timestamp": {"$gte": week_start, "$lte": week_end},
                }
            },
            {
                "$group": {
                    "_id": "$event_type",
                    "count": {"$sum": 1},
                    "average_confidence": {"$avg": "$confidence"},
                    "latest_timestamp": {"$max": "$timestamp"},
                }
            },
            {"$sort": {"count": -1}},
        ]
        grouped = list(events.aggregate(pipeline))
        total_events = sum(item.get("count", 0) for item in grouped)

        return {
            "user_id": self.phone_number,
            "window_start": week_start,
            "window_end": week_end,
            "total_events": total_events,
            "event_type_breakdown": grouped,
        }

    def fetch_all_chats(self):
        collection = self.get_messages_collection()
        chats = list(collection.find({}))
        return chats

    def fetch_last_k(self, k: int = 10 ):
        collection = self.get_messages_collection()
        chats = list(collection.find({}).sort('timestamp', pymongo.DESCENDING).limit(k))
        return chats
    
    def upload_message(self, message: str, role: str):
        collection = None
        db = self.get_database()
        collection = db.get_collection(self.phone_number) if self.phone_number in db.list_collection_names() else db.create_collection(self.phone_number)
        utc_timestamp = datetime.now(timezone.utc).timestamp()
        print(f"Uploading message {message} to time {utc_timestamp}")
        collection.insert_one({"message": message, "timestamp": utc_timestamp, "role": role})
        return