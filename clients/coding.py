import asyncio
import json

import requests

from libs.base import BaseClient


class Coding(BaseClient):

    def __init__(self):
        super().__init__()
        self.url = 'https://e.coding.net/login'

    async def handler(self, **kwargs):
        try:
            self.logger.info(f'{self.username} start login.')
            await asyncio.sleep(8)
            await self.page.type('#account', self.username, {'delay': 30})
            await asyncio.sleep(0.5)
            await self.page.type('#password', self.password, {'delay': 30})
            await asyncio.sleep(0.5)
            await self.page.click('div.cuk-checkbox-2-box')
            await asyncio.sleep(0.5)
            await self.page.click('button[type="Submit"]')
            await asyncio.sleep(8)

            cookies = await self.get_cookies()
            cookies = json.dumps(cookies)
            self.logger.info(self.page.url)
            result = requests.post(f'{self.api}/coding/save', data={'cookies': cookies, 'username': self.username}).text
            self.logger.info(result)
        except Exception as e:
            await self.send_photo(self.page, 'coding')
