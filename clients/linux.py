import asyncio
import random
import aiofiles

from libs.base import BaseHeadless


class LinuxDo(BaseHeadless):
    base_url = 'https://linux.do/'
    width = 1920
    link_map = {}
    history_file = 'linux_do.txt'

    async def run(self, **kwargs):
        await self.init(self.base_url, headless=kwargs.get('headless'))
        await self.login(**kwargs)
        while True:
            async for link, name in self.get_links():
                if self.link_map.get(link):
                    continue
                self.link_map[link] = name
                self.logger.info(f'{link}\t{name}')
                await self.do_views(link)
                async with aiofiles.open(self.history_file, 'a') as f:
                    await f.write(f'{link}\n')
            self.logger.info('Wait 600 seconds')
            await asyncio.sleep(600)

    async def do_views(self, url):
        view_page = await self.new_page()
        try:
            await view_page.goto(url, {'waitUntil': 'load'})
            await asyncio.sleep(5)
            num = random.randint(2, 10)
            for _ in range(num):
                await view_page.evaluate('''() =>{ window.scrollBy(0, 100); }''')
                n = random.randint(1, 20)
                await asyncio.sleep(0.5 * n)
        except Exception as e:
            self.logger.error(e)
        finally:
            await view_page.close()

    async def get_links(self):
        try:
            await self.page.goto(f'{self.base_url}/new', {'waitUntil': 'load'})
            await asyncio.sleep(5)

            items = await self.page.querySelectorAll('table.topic-list a.raw-link')
            if items and len(items) > 0:
                for item in items:
                    name = await self.page.evaluate('el => el.textContent', item)
                    href = await self.page.evaluate('el => el.href', item)
                    yield href, name
        except Exception as e:
            self.logger.error(e)

    async def login(self, **kwargs):
        await asyncio.sleep(2)

        username = kwargs.get('username')
        password = kwargs.get('password')

        await asyncio.sleep(4)

        await self.page.click('div.panel .btn')
        await asyncio.sleep(1)

        await self.page.type('input[type="email"]', username, {'delay': 30})
        await self.page.type('input[type="password"]', password, {'delay': 30})
        await self.page.click('#login-button')
        await asyncio.sleep(4)
