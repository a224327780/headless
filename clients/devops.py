import asyncio
from urllib import parse

from libs.base import BaseHeadless


class Devops(BaseHeadless):
    sign_url = 'https://login.microsoftonline.com/common/oauth2/authorize?client_id=499b84ac-1321-427f-aa17-267ca6975798&site_id=501454&response_mode=form_post&response_type=code+id_token&redirect_uri=https%3A%2F%2Fapp.vssps.visualstudio.com%2F_signedin&nonce=ad2d5b65-0d7d-4d62-80fe-ac52ef632a3f&state=realm%3Daex.dev.azure.com%26reply_to%3Dhttps%253A%252F%252Faex.dev.azure.com%252Fsignup%253FacquisitionId%253D67ceb2a5-617a-4ddc-a213-dd584c52ba58%2526campaign%253Dacom~azure~devops~services~main~hero%2526githubsi%253Dtrue%2526WebUserId%253D26494b7d61954b90a1a794590280cf74%2526acquisitionType%253DbyDefault%26ht%3D3%26mkt%3Dzh-CN%26nonce%3Dad2d5b65-0d7d-4d62-80fe-ac52ef632a3f&resource=https%3A%2F%2Fmanagement.core.windows.net%2F&cid=ad2d5b65-0d7d-4d62-80fe-ac52ef632a3f&wsucxt=1&githubsi=true&msaoauth2=true&mkt=zh-CN&sso_reload=true'

    async def run(self, **kwargs):
        await self.init(self.sign_url, headless=kwargs.get('headless'))
        username = kwargs.get('username')
        password = kwargs.get('password')

        if not await self.login(username, password):
            file = await self.screenshot(username)
            await self.send_tg_photo(file)
            self.logger.error(f'[{username}] login fail.')
            return

        p = parse.urlsplit(self.page.url)
        org_name = p.path.strip('/').split('/')[0]
        setting_url = f'{p.scheme}://{p.netloc}/{org_name}/_settings/organizationPolicy'
        await self.do_setting(setting_url)
        token_url = f'{p.scheme}://{p.netloc}/{org_name}/_usersSettings/tokens'
        await self.do_create_token(token_url)

    async def do_setting(self, setting_url):
        setting_page = await self.new_page()
        try:
            await setting_page.goto(setting_url, {'waitUntil': 'load'})
            await asyncio.sleep(5)

            items = await setting_page.querySelectorAll('div.bolt-toggle-button-text')
            text = await setting_page.evaluate('item => item.textContent', items[2])
            if 'Off' in text:
                await items[2].click()
                await asyncio.sleep(2)
                await setting_page.click('.bolt-panel-footer-buttons .bolt-button.enabled.primary.bolt-focus-treatment')
                await asyncio.sleep(2)
        except Exception as e:
            self.logger.error(e)
        finally:
            await setting_page.close()

    async def do_create_token(self, token_url):
        if 'main' in token_url:
            token_url = token_url.replace('main', '')

        token_page = await self.new_page()
        try:
            await token_page.goto(token_url, {'waitUntil': 'load'})
            await asyncio.sleep(5)

            await token_page.click('button.bolt-button.bolt-icon-button.enabled.primary.bolt-focus-treatment')
            await asyncio.sleep(1)
            await token_page.type('#__bolt-textfield-input-2', 'api', {'delay': 30})
            await asyncio.sleep(0.5)
            await token_page.click('#Dropdown1')
            await asyncio.sleep(1)
            await token_page.click('#Dropdown1-list2')
            await asyncio.sleep(1)
            await token_page.click('#__bolt-rb-label-full')
            await asyncio.sleep(2)
            buttons = await token_page.querySelectorAll('div.bolt-panel-footer button')
            if len(buttons) == 2:
                await buttons[0].click()
                await asyncio.sleep(8)
                return await token_page.Jeval('.bolt-panel-content input', 'e => e.value')
        except Exception as e:
            self.logger.error(e)
            return None
        finally:
            await token_page.close()

    async def login(self, username, password):
        try:
            await self.page.type('input[type="email"]', username, {'delay': 30})
            await self.page.click('input[type="submit"]')

            await asyncio.sleep(5)
            await self.page.waitForSelector('input[type="password"]')

            await self.page.type('input[type="password"]', password, {'delay': 30})
            await self.page.click('input[type="submit"]')
            await asyncio.sleep(5)

            await self.page.click('input[type="submit"]')
            await asyncio.sleep(10)

            if self.page.url.startswith('https://dev.azure.com'):
                return True

            try:
                await self.page.click('button[type="submit"]')
                await asyncio.sleep(5)
            except Exception as e:
                self.logger.debug(e)

            return await self.login_captcha()
        except Exception as e:
            self.logger.error(e)
            return False

    async def login_captcha(self):
        for j in range(3):
            if self.page.url.startswith('https://dev.azure.com'):
                return True

            try:
                image_list = await self.page.querySelectorAll('img')
                if not image_list or len(image_list) <= 0:
                    await asyncio.sleep(5)
                    continue

                image = image_list[0]
                file = 'azure.png'
                await image.screenshot({'path': file})
                await asyncio.sleep(1)

                code = await self._get_captcha_code(file)
                if code is None:
                    continue

                await self.page.type('input[type="text"]', code, {'delay': 30})
                await self.page.click('button[type="submit"]')

                await asyncio.sleep(20)

                new_captcha = await self.page.querySelector('a[title="Get a new challenge"]')
                if not new_captcha:
                    return True

                await new_captcha.click()
                await asyncio.sleep(5)
            except Exception as e:
                self.logger.debug(e)
        return False

    async def _get_captcha_code(self, file):
        for _ in range(3):
            code = await self.get_captcha_code(file)
            if code:
                return code
        return None
