import asyncio
import base64
import hashlib
import hmac
import logging
import os
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

import async_timeout
import requests
from pyppeteer import launch, launcher
from pyppeteer.browser import Browser
from pyppeteer.network_manager import Request
from pyppeteer.page import Page


class BaseClient:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.url = None
        self.username = None
        self.password = None
        self.parent_user = None
        self.git = None
        self.ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
        self.api = 'https://api01-a224327780.cloud.okteto.net'
        self.width = 1440
        self.height = 900

    async def before_run(self):
        pass

    async def after_run(self, **kwargs):
        pass

    async def run(self, **kwargs):
        await self.before_run()

        username_list = kwargs.get('username').split(',')
        password_list = kwargs.get('password').split(',')

        self.logger.warning(username_list)

        for i, username in enumerate(username_list):
            password = password_list[0] if len(password_list) == 1 else password_list[i]
            self.username = username
            self.password = password
            try:
                async with async_timeout.timeout(240):
                    await self.run_master(**kwargs)
            except asyncio.TimeoutError:
                self.logger.warning(f'{username} timeout.')
            finally:
                await self.after_run()
                await self.close()
                await asyncio.sleep(2)

    async def run_master(self, **kwargs):
        try:
            await self.init(**kwargs)
            await self.handler(**kwargs)
        except Exception as e:
            self.logger.exception(e)

    async def init(self, **kwargs):
        # launcher.DEFAULT_ARGS.remove('--enable-automation')
        self.browser = await launch(ignorehttpserrrors=True, headless=kwargs.get('headless', True),
                                    args=['--disable-infobars', '--disable-web-security', '--no-sandbox',
                                          '--start-maximized', '--disable-features=IsolateOrigins,site-per-process'])
        self.page = await self.get_new_win_page(self.url)

    async def get_new_win_page(self, url, intercept_request=None):
        page = await self.browser.newPage()
        try:
            page.on('dialog', lambda dialog: asyncio.ensure_future(self.close_dialog(dialog)))
        except Exception as e:
            self.logger.warning(e)

        await page.setUserAgent(self.ua)
        await page.setViewport(viewport={'width': self.width, 'height': self.height})

        js_text = """
        () =>{
            Object.defineProperties(navigator,{ webdriver:{ get: () => false } });
            window.navigator.chrome = { runtime: {},  };
            Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN','en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], });
         }
            """
        await page.evaluateOnNewDocument(js_text)

        if intercept_request:
            await page.setRequestInterception(True)
            page.on('request', intercept_request)

        await page.goto(url, {'waitUntil': 'load'})
        return page

    async def intercept_request(self, request: Request):
        self.logger.info(request.url)
        if request.resourceType in ["image"]:
            await request.abort()
        else:
            await request.continue_()

    async def get_cookies(self):
        cookies = await self.page.cookies()
        new_cookies = {}
        for cookie in cookies:
            new_cookies[cookie['name']] = cookie['value']
        return new_cookies

    async def handler(self, **kwargs):
        raise RuntimeError

    async def close(self):
        try:
            if self.page and not self.page.isClosed():
                await self.page.close()
                self.page = None
        except Exception as e:
            self.logger.debug(e)

        try:
            if self.browser and self.browser:
                await self.browser.close()
                self.browser = None
        except Exception as e:
            self.logger.debug(e)
            # os.system("kill -9 `ps -ef|grep chrome|grep -v grep|awk '{print $2}'`")

    @staticmethod
    async def close_dialog(dialog):
        await dialog.dismiss()

    @staticmethod
    async def accept_dialog(dialog):
        await dialog.accept()

    @staticmethod
    def send_message(text, title='Notice'):
        ding_url = 'https://oapi.dingtalk.com/robot/send'
        access_token = os.environ.get('DING_TOKEN')
        _timestamp = str(round(time.time() * 1000))
        secret = 'SEC25b6b9851cc21443c8b020dc03562a199e3cfecd502062861fc3d2c1ae226a8d'
        secret_enc = secret.encode('utf-8')
        string_to_sign_enc = '{}\n{}'.format(_timestamp, secret).encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code)
        json_data = {'msgtype': 'markdown', 'markdown': {'text': text, 'title': title}}
        params = {'access_token': access_token, 'timestamp': _timestamp, 'sign': sign}
        return requests.post(ding_url, params=params, json=json_data).json()

    @staticmethod
    def get_bj_time():
        utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
        return utc_dt.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')

    async def send_photo(self, page, title):
        file = f'/tmp/{int(time.time())}.png'
        await page.screenshot(path=file, fullPage=True)
        files = {'file': open(file, 'rb')}
        requests.post(f'{self.api}/tg/photo', files=files,
                      data={'chat_id': '-375307506', 'title': f'{self.username}->{title}'}, timeout=20)
