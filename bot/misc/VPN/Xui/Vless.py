import json
import uuid

import pyxui.errors

from bot.misc.VPN.Xui.XuiBase import XuiBase
from bot.misc.util import CONFIG


class Vless(XuiBase):
    NAME_VPN = 'Vless 🐊'

    def __init__(self, server):
        super().__init__(server)

    async def get_client(self, name):
        try:
            return self.xui.get_client(
                inbound_id=self.inbound_id,
                email=name,
            )
        except pyxui.errors.NotFound:
            return 'User not found'

    async def add_client(self, name):
        try:
            response = self.xui.add_client(
                inbound_id=self.inbound_id,
                email=str(name),
                uuid=str(uuid.uuid4()),
                limit_ip=CONFIG.limit_ip,
                total_gb=CONFIG.limit_GB * 1073741824
            )
            if response['success']:
                return True
            return False
        except pyxui.errors.NotFound:
            return False

    async def delete_client(self, telegram_id):
        try:
            response = self.xui.delete_client(
                inbound_id=self.inbound_id,
                email=telegram_id,
            )
            return response['success']
        except pyxui.errors.NotFound:
            return False

    async def get_key_user(self, name, name_key):
        info = await self.get_inbound_server()
        client = await self.get_client(name)
        if client == 'User not found':
            await self.add_client(name)
            client = await self.get_client(name)
        stream_settings = json.loads(info['streamSettings'])
        fp = stream_settings["realitySettings"]["settings"]["fingerprint"]
        pbk = stream_settings["realitySettings"]["settings"]["publicKey"]
        key = (f'vless://{client["id"]}@'
               f'{self.adress}:{info["port"]}?'
               f'type={stream_settings["network"]}&'
               f'security={stream_settings["security"]}&'
               f'fp={fp}&'
               f'pbk={pbk}&'
               f'sni={stream_settings["realitySettings"]["serverNames"][0]}&'
               f'sid={stream_settings["realitySettings"]["shortIds"][0]}&'
               f'spx=%2F'
               f'#{name_key}')
        return key
