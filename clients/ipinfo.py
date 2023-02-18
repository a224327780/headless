import asyncio

from libs.base import BaseHeadless
from random_username.generate import generate_username


class IpInfo(BaseHeadless):
    sign_url = 'https://ipinfo.io/signup'

    async def run(self, **kwargs):
        await self.init(self.sign_url, headless=kwargs.get('headless'))
        username = kwargs.get('username')
        password = kwargs.get('password')
        name = generate_username(2)

        await self.page.type('input[name="firstName"]', name[0], {'delay': 30})
        await self.page.type('input[name="lastName"]', name[1], {'delay': 30})
        await self.page.type('input[name="email"]', username, {'delay': 30})
        await self.page.type('input[name="password"]', password, {'delay': 30})

        await self.page.click('button[type="submit"]')
        self.logger.info(f'[{username}] submit.')
        await asyncio.sleep(10)

        if 'confirm' in self.page.url:
            self.logger.info(f'[{username}] register done.')
            return

        file = await self.screenshot('ipinfo')
        await self.send_tg_photo(file)
