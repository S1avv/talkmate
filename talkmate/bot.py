from talkmate.config.settings import TOKEN
from talkmate.keyboards.builder import main_kb, leave_chat
from talkmate.middlewares.create_user import create_new_user

import asyncio
import logging
import firebase_admin
from firebase_admin import credentials, firestore

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram import F

bot = Bot(TOKEN, parse_mode="HTML")

dp = Dispatcher()

cred = credentials.Certificate("talkmate/config/firebase.json")

firebase_admin.initialize_app(cred)

db = firestore.client()

logging.basicConfig(level=logging.INFO)



@dp.message(F.text == "/start")
async def start_message(message: Message) -> None:
    await message.answer(
        f"👋 Привет! Добро пожаловать в TalkMate!\n\n"
        f"🤝 Здесь ты можешь общаться с интересными людьми со всего мира.\n\n"
        f"🌐 Не стесняйся обсуждать различные темы. Это место, где можно делиться идеями, находить новых друзей и просто хорошо проводить время.\n\n"
        f"Если у тебя есть вопросы или нужна помощь, введи команду /help. Приятного общения! 🚀", reply_markup=main_kb)
    
    users_collection = db.collection("users")

    user_doc_ref = users_collection.document(str(message.from_user.id))
    user_doc = user_doc_ref.get()

    if not user_doc.exists:
        await create_new_user(user_id=str(message.from_user.id), db=db)
    else:
        if user_doc.get("interlocutor") == "None":
            pass
        else:
            user_doc_ref.update(
            {
                "interlocutor": "None"
            }
        )
            user_doc_ref = db.collection("users").document(user_doc.get("interlocutor"))
            user_doc = user_doc_ref.get()
            user_doc_ref.update(
            {
                "interlocutor": "None"
            }
        )
            await message.answer(f"✅ TalkMate | Вы успешно завершили диалог", reply_markup=main_kb)
        
            await bot.send_message(chat_id=user_doc.get("interlocutor"), text=f"✅ TalkMate | Собеседник завершил диалог", reply_markup=main_kb)



@dp.message(F.text == "🔍 Начать поиск")
async def start_message(message: Message) -> None:
    await message.answer(f"⌛ TalkMate | Поиск собеседника")
    await asyncio.sleep(2)
    
    db.document("search_interlocutor/users_list").update({str(message.from_user.id): ""})

    users_list_document = db.document("search_interlocutor/users_list")
    users_list_data = users_list_document.get().to_dict()

    if len(users_list_data) == 1:
        while True:
            users_list_data = users_list_document.get().to_dict()
            if len(users_list_data) == 1:
                await asyncio.sleep(4)
            else:
                break
    

    user_doc_ref = db.collection("users").document(str(message.from_user.id))
    
    if str(message.from_user.id) == list(users_list_data.keys())[0]:
        id_interlocutor = list(users_list_data.keys())[1]
        user_doc_ref.update(
        {
            "interlocutor": id_interlocutor
        }
    )
    else:
        user_doc_ref.update(
            {
                "interlocutor": list(users_list_data.keys())[0]
            }
        )
    user_doc = user_doc_ref.get().to_dict()
    user_doc_ref = db.collection("users").document(user_doc.get("interlocutor"))

    user_doc_ref.update(
        {
            "interlocutor": str(message.from_user.id)
        }
    )

    user_doc_ref = db.collection("search_interlocutor").document("users_list")
    user_doc_ref.update({str(message.from_user.id): firestore.DELETE_FIELD})
    user_doc_ref.update({user_doc.get("interlocutor"): firestore.DELETE_FIELD})

    await message.answer(f"✅ TalkMate | Собеседник успешно найден", reply_markup=leave_chat)
    await bot.send_message(chat_id=user_doc.get("interlocutor"), text=f"✅ TalkMate | Собеседник успешно найден", reply_markup=main_kb)


@dp.message(F.text == "🚫 Закончить диалог")
async def leave_ch(message: Message):
    user_doc_ref = db.collection("users").document(str(message.from_user.id))

    user_doc = user_doc_ref.get()

    if user_doc.get("interlocutor") == "None":
        await message.delete()
    else:
        user_doc_ref.update(
        {
            "interlocutor": "None"
        }
    )
        user_doc_ref = db.collection("users").document(user_doc.get("interlocutor"))
        user_doc = user_doc_ref.get()
        user_doc_ref.update(
        {
            "interlocutor": "None"
        }
    )
        await message.answer(f"✅ TalkMate | Вы успешно завершили диалог", reply_markup=main_kb)
        
        user_doc_ref = db.collection("users").document(str(message.from_user.id))
        user_doc = user_doc_ref.get()

        await bot.send_message(chat_id=user_doc.get("interlocutor"), text=f"✅ TalkMate | Собеседник завершил диалог", reply_markup=main_kb)

@dp.message()
async def send_message(message: Message) -> None:
    user_doc_ref = db.collection("users").document(str(message.from_user.id))

    user_doc = user_doc_ref.get()

    if user_doc.get("interlocutor") == "None":
        await message.delete()
    else:
        await bot.send_message(chat_id=user_doc.get("interlocutor"), text=message.text)

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
