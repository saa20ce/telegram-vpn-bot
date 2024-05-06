import base64
import json
import secrets
import string

import pyxui.errors

from bot.misc.VPN.Xui.XuiBase import XuiBase
from bot.misc.util import CONFIG


def generate_password(length=44):
    characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(characters) for _ in range(length))
    encoded_password = base64.b64encode(password.encode()).decode()
    return encoded_password


class Shadowsocks(XuiBase):
    NAME_VPN = 'Shadowsocks 🦈'
    adress: str

    def __init__(self, server):
        super().__init__(server)

    async def get_client(self, name):
        try:
            return self.get_client_ss(
                inbound_id=self.inbound_id,
                email=name
            )
        except pyxui.errors.NotFound:
            return 'User not found'

    async def add_client(self, name):
        try:
            response = self.add_client_ss(
                inbound_id=self.inbound_id,
                email=str(name),
                limit_ip=CONFIG.limit_ip,
                total_gb=CONFIG.limit_GB * 1073741824
            )
            return response['success']
        except pyxui.errors.NotFound:
            return False

    async def delete_client(self, telegram_id):
        try:
            response = self.delete_client_ss(
                inbound_id=self.inbound_id,
                email=telegram_id,
            )
            return response['success']
        except pyxui.errors.NotFound:
            return False

    async def get_key_user(self, name, name_key):
        info = await self.get_inbound_server()
        client = await self.get_client(name)
        if client is None:
            await self.add_client(name)
            client = await self.get_client(name)
        stream_settings = json.loads(info['streamSettings'])
        settings = json.loads(info['settings'])
        user_base64 = base64.b64encode(
            f'{settings["method"]}:'
            f'{settings["password"]}:'
            f'{client["password"]}'
            .encode()).decode()
        key_str = (
            f'{user_base64}@'
            f'{self.adress}:'
            f'{info["port"]}?'
            f'type={stream_settings["network"]}#'
            f'{name_key}')
        key = f"ss://{key_str}"
        return key

    def add_client_ss(
        self,
        inbound_id: int,
        email: str,
        password: str = generate_password(44),
        enable: bool = True,
        limit_ip: int = 0,
        total_gb: int = 0,
        expire_time: int = 0,
        telegram_id: str = "",
        subscription_id: str = generate_password(12)[:-1],
    ):
        settings = {
            "clients": [
                {
                  "email": email,
                  "enable": enable,
                  "expiryTime": expire_time,
                  "limitIp": limit_ip,
                  "method": "",
                  "password": password,
                  "subId": subscription_id,
                  "tgId": telegram_id,
                  "totalGB": total_gb
                }
            ],
            "decryption": "none",
            "fallbacks": []
        }

        params = {
            "id": inbound_id,
            "settings": json.dumps(settings)
        }

        response = self.xui.request(
            path="addClient",
            method="POST",
            params=params
        )

        return self.xui.verify_response(response)

    def get_client_ss(
            self,
            inbound_id: int,
            email: str = False,
            password: str = False):

        get_inbounds = self.xui.get_inbounds()

        if not email and not password:
            raise ValueError()

        for inbound in get_inbounds['obj']:
            if inbound['id'] != inbound_id:
                continue

            settings = json.loads(inbound['settings'])

            for client in settings['clients']:
                if client['email'] != email and client['password'] != password:
                    continue

                return client

    def delete_client_ss(
            self,
            inbound_id: int,
            email: str = False,
            password: str = False
    ):
        find_client = self.get_client_ss(
            inbound_id=inbound_id,
            email=email,
            password=password
        )

        response = self.xui.request(
            path=f"{inbound_id}/delClient/{find_client['email']}",
            method="POST"
        )

        return self.xui.verify_response(response)
