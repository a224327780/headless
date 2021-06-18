import asyncio
import json

import requests

from libs.base import BaseClient


class Coding(BaseClient):

    def __init__(self):
        super().__init__()
        self.url = 'https://e.coding.net/login'

    async def handler(self, **kwargs):
        ip = requests.get('http://api.ipify.org/').text
        self.logger.info(ip)
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

            url = await self.page.url()
            user = url.split('.')[0].replace('https://', '')

            cookies = await self.get_cookies()
            cookies = json.dumps(cookies)
            self.logger.info(url)

            data = {'cookies': cookies, 'username': self.username, 'user': user, 'project': user}
            result = requests.post(f'{self.api}/coding/save_cookie', data=data).text
            self.logger.info(result)
        except Exception as e:
            self.logger.exception(e)
            await self.send_photo(self.page, 'coding')
