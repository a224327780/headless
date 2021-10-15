import asyncio
import os

from libs.base_huawei import BaseHuaWei


class HuaWei(BaseHuaWei):

    def __init__(self):
        super().__init__()

    async def handler(self, **kwargs):
        self.cancel = False

        self.logger.info(f'{self.username} start login.')
        if kwargs.get('iam'):
            await self.iam_login(self.username, self.password, kwargs.get('parent'))
        else:
            await self.login(self.username, self.password)

        url = self.page.url
        if 'auth' in url:
            self.logger.error(f'{self.username} login fail.')
            # await self.send_photo(self.page, 'login')
            return None

        await self.sign_task()

        cookies = await self.get_cookies()
        self.logger.info(cookies)
        return None

        await self.init_user()

        await asyncio.sleep(2)

        if not self.user:
            await self.send_photo(self.page, 'user')
            return None

        await self.init_projects()

    
        self.logger.info(self.user)
        self.logger.info(self.projects)
        # self.logger.info(self.cftk)

        n = len(self.projects)
        self.logger.info(n)

        if n <= 0:
            await self.new_project()

        await self.start()

        await self.init_projects()

        await self.delete_function()
        await self.delete_api()
        await self.delete_api_group()
        await self.delete_project()

    async def async_timeout_run(self, callback):
        try:
            func = getattr(self, callback)
            await asyncio.wait_for(func(), timeout=60.0)
        except asyncio.TimeoutError as t:
            self.logger.warning(f'{callback} {t}')

    async def login(self, username, password):
        await self.page.waitForSelector('#personalAccountInputId input')
        await self.page.type('#personalAccountInputId input', username, {'delay': 10})
        await asyncio.sleep(1)
        await self.page.type('#personalPasswordInputId input', password, {'delay': 10})
        await asyncio.sleep(2)

        await self.page.click('#btn_submit')
        await asyncio.sleep(5)

    async def iam_login(self, username, password, parent):
        self.parent_user = os.environ.get('PARENT_USER', parent)

        for i in range(4):
            try:
                await self.page.waitForSelector('#subUserLogin')
                await asyncio.sleep(2)
                await self.page.click('#subUserLogin')
                await asyncio.sleep(1)
                await self.page.type('#IAMAccountInputId input', self.parent_user, {'delay': 10})
                await asyncio.sleep(0.5)
                await self.page.type('#IAMUsernameInputId input', username, {'delay': 10})
                await asyncio.sleep(0.5)
                await self.page.type('#IAMPasswordInputId input', password, {'delay': 10})
                await self.page.click('#loginBtn')
                await asyncio.sleep(5)
                break
            except Exception as e:
                self.logger.debug(e)
                await self.page.goto(self.url, {'waitUntil': 'load'})

    async def get_cookies(self):
        cookies = await self.page.cookies()
        new_cookies = {}
        for cookie in cookies:
            new_cookies[cookie['name']] = cookie['value']
        return new_cookies
