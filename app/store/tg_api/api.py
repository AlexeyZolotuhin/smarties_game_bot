from typing import Optional

import aiohttp

from app.store.tg_api.dataclasses import GetUpdatesResponse, SendMessageResponse
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove


class TgClient:
    def __init__(self, token: str = ''):
        self.token = token

    def get_url(self, method: str):
        return f"https://api.telegram.org/bot{self.token}/{method}"

    async def get_me(self) -> dict:
        url = self.get_url("getMe")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()

    async def get_updates(self, offset: Optional[int] = None, timeout: int = 0) -> dict:
        url = self.get_url("getUpdates")
        params = {}
        if offset:
            params['offset'] = offset
        if timeout:
            params['timeout'] = timeout
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                return await resp.json()

    async def get_updates_in_objects(self, offset: Optional[int] = None, timeout: int = 0) -> GetUpdatesResponse:
        res = await self.get_updates(offset=offset, timeout=timeout)
        result = GetUpdatesResponse.Schema().load(res)
        return result

    async def send_message(self, chat_id: int, text: str,
                           reply_markup=None) -> SendMessageResponse:
        url = self.get_url("sendMessage")
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup.to_json()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                res_dict = await resp.json()
                return SendMessageResponse.Schema().load(res_dict)

    async def delete_message(self, chat_id: int, message_id: int):
        url = self.get_url("deleteMessage")
        payload = {
            'chat_id': chat_id,
            'message_id': message_id
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                res_dict = await resp.json()
                return res_dict

    async def edit_message_text(self, chat_id: int, message_id: int, text: str, reply_markup=None):
        url = self.get_url("editMessageText")
        payload = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup.to_json()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                res_dict = await resp.json()
                return res_dict

    async def raw_send_message(self, chat_id: int, text: str,
                               reply_markup=None):
        url = self.get_url("sendMessage")
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup.to_json()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                res_dict = await resp.json()
                return res_dict
