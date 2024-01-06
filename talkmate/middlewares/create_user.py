import asyncio
import firebase_admin
from firebase_admin import credentials, firestore

async def create_new_user(user_id: str, db: str) -> None:
    doc_ref = db.document("users/{}".format(user_id))

    set_data = {
        "acess": True,
        "interlocutor": "None"
    }

    doc_ref.set(set_data)