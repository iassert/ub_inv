import re
import os
import logging

from pyrogram       import Client, filters, types
from pyrogram.types import Message, ChatMember, Dialog

from typing import Callable, Union, Optional, AsyncGenerator

logging.basicConfig(level = logging.INFO)


class Config:
    API_ID: int
    API_HASH: str


class Client_:
    def __init__(self, name: str, api_id: int, apit_hash: str) -> None:
        self.__app: Client = Client(self.path(name), api_id, apit_hash)

    def run(self,
        coroutine = None
    ):
        self.__app.run(coroutine)


    @staticmethod
    def path(name: str) -> str:
        dir_ = os.path.dirname(os.path.realpath(__file__))
        session_dir = os.path.join(dir_, "session")

        if not os.path.exists(session_dir):
            os.mkdir(session_dir)

        return os.path.join(session_dir, name)
    

    def on_message(self,
        filters = None,
        group: int = 0
    ) -> Callable:
        return self.__app.on_message(filters, group)
    
    async def get_chat_join_requests(self,
        chat_id: Union[int, str],
        limit: int = 0,
        query: str = ""
    ) -> Optional[AsyncGenerator[types.ChatJoiner, None]]:
        try:
            async for member in self.__app.get_chat_join_requests(chat_id, limit, query):
                member: ChatMember
                yield member
        except Exception as ex:
            logging.error(f"{ex.__class__.__name__}: {ex}")

    async def approve_chat_join_request(self,
        chat_id: Union[int, str],
        user_id: int,
    ) -> bool:
        try:
            return await self.__app.approve_chat_join_request(chat_id, user_id)
        except Exception as ex:
            logging.error(f"{ex.__class__.__name__}: {ex}")
        return False
    
    async def get_dialogs(self,
        limit: int = 0
    ):
        try:
            async for dialog in self.__app.get_dialogs(limit):
                dialog: Dialog

                yield dialog
        except Exception as ex:
            logging.error(f"{ex.__class__.__name__}: {ex}")


    async def leave_chat(self,
        chat_id: Union[int, str],
        delete: bool = False
    ):
        try:
            await self.__app.leave_chat(chat_id, delete)
        except Exception as ex:
            logging.error(f"{ex.__class__.__name__}: {ex}")

    async def join_chat(self,
        chat_id: Union[int, str]
    ):
        try:
            await self.__app.join_chat(chat_id)
        except Exception as ex:
            logging.error(f"{ex.__class__.__name__}: {ex}")


class Message_:
    def __init__(self, message: Message):
        self.__message: Message = message

    async def delete(self):
        try:
            await self.__message.delete()
        except Exception as ex:
            logging.error(f"{ex.__class__.__name__}: {ex}")


app: Client_ = Client_("_", Config.API_ID, Config.API_HASH)

@app.on_message(filters.command("inv") & (filters.group | filters.channel))
async def invite(client: Client, message: Message):
    await Message_(message).delete()
    
    chat_id = message.chat.id
    async for member in app.get_chat_join_requests(chat_id):
        member: ChatMember

        await app.approve_chat_join_request(chat_id, member.user.id)

@app.on_message(filters.command("left") & filters.private)
async def left(client: Client, message: Message):
    await Message_(message).delete()

    async for dialog in app.get_dialogs():
        dialog: Dialog

        await app.leave_chat(dialog.chat.id)

@app.on_message(filters.command("join") & filters.regex(r'https://t\.me/\+(\S+)') & filters.private)
async def join_(client: Client, message: Message):
    await Message_(message).delete()

    chat_link = re.search(r'https://t\.me/\+(\S+)', message.text).group(0)
    await app.join_chat(chat_link)

app.run()
