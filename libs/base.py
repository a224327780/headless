import asyncio
import base64
import logging
import os
import time
from typing import Optional

from aiohttp import ClientSession
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.network_manager import Request
from pyppeteer.page import Page


class BaseHeadless:

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.request_session = ClientSession()
        self.ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
        self.width = 1440
        self.height = 900

    async def run(self, **kwargs):
        raise NotImplementedError

    async def init(self, url, **kwargs):
        kwargs.setdefault('headless', True)
        kwargs.setdefault('ignorehttpserrrors', True)
        args = ['--disable-infobars', '--disable-web-security', '--no-sandbox',
                '--start-maximized', '--disable-features=IsolateOrigins,site-per-process']
        self.browser = await launch(args=args, **kwargs)
        self.page = await self.new_page(url)

    async def new_page(self, url=None, intercept_request=False):
        page = await self.browser.newPage()
        try:
            page.on('dialog', lambda dialog: asyncio.ensure_future(self.close_dialog(dialog)))
        except Exception as e:
            self.logger.debug(e)

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

        if url is not None:
            await page.goto(url, {'waitUntil': 'load'})
        return page

    async def intercept_request(self, request: Request):
        self.logger.debug(request.url)
        if request.resourceType in ["image"]:
            await request.abort()
        else:
            await request.continue_()

    async def get_cookies(self, page: Optional[Page] = None) -> dict:
        if not page:
            page = self.page
        cookies = await page.cookies()
        new_cookies = {}
        for cookie in cookies:
            new_cookies[cookie['name']] = cookie['value']
        return new_cookies

    @staticmethod
    async def close_dialog(dialog):
        await dialog.dismiss()

    @staticmethod
    async def accept_dialog(dialog):
        await dialog.accept()

    async def screenshot(self, name=None):
        if not name:
            name = int(time.time())
        file = f'./{name}.png'
        await self.page.screenshot(path=file, fullPage=True)
        return file

    async def get_page(self, index=-1) -> Page:
        page_list = await self.browser.pages()
        if index < len(page_list):
            return page_list[index]
        return self.page

    async def close_page(self, page_index):
        page = await self.get_page(page_index)
        try:
            await page.close()
        except Exception as e:
            self.logger.debug(e)

    async def close(self):
        try:
            if self.page and not self.page.isClosed():
                await self.page.close()
                self.page = None
        except Exception as e:
            self.logger.error(e)

        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
        except Exception as e:
            self.logger.error(e)

        await self.request_session.close()
        self.logger.info('done.')

    async def send_tg_message(self, text):
        api = os.getenv('TG_API', 'https://api01.eu.org/tg/message')
        async with self.request_session.post(api, data={'message': text}, timeout=20) as response:
            return await response.text()

    async def send_tg_photo(self, file):
        api = os.getenv('TG_API', 'https://api01.eu.org/tg/photo')
        async with self.request_session.post(api, data={'photo': open(file, 'rb')}, timeout=20) as response:
            return await response.text()

    async def get_captcha_code(self, file):
        with open(file, 'rb') as f:
            content = f.read()
        encoded_string = base64.b64encode(content)
        url = 'https://api.apitruecaptcha.org/one/gettext'
        captcha_user = os.getenv('CAPTCHA_USER')
        captcha_key = os.getenv('CAPTCHA_KEY')
        data = {'userid': captcha_user, 'apikey': captcha_key, 'data': str(encoded_string)[2:-1]}
        async with self.request_session.post(url, json=data, timeout=20) as response:
            response_data = await response.json()
            if 'result' in response_data:
                solved_text = response_data['result'].lower()
                self.logger.info(f'captcha: {solved_text}')
                operators = ['+', '-', '*', '/']
                if any(x in solved_text for x in operators):
                    return eval(solved_text)
                return solved_text
            return None
