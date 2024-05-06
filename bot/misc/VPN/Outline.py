import json

from outline_vpn.outline_vpn import OutlineVPN

from bot.misc.VPN.BaseVpn import BaseVpn
from bot.misc.util import CONFIG


class Outline(BaseVpn):
    NAME_VPN = 'Outline 🪐'

    def __init__(self, server):
        api_cert = json.loads(server.outline_link)
        self.client = OutlineVPN(
            api_url=api_cert['apiUrl'],
            cert_sha256=api_cert['certSha256']
        )

    async def get_all_user_server(self):
        return self.client.get_keys()

    async def get_client(self, name):
        all_user = await self.get_all_user_server()
        for user in all_user:
            if user.name == str(name):
                return user
        return None

    async def add_client(self, name):
        try:
            key = self.client.create_key(key_name=name)
            if CONFIG.limit_GB != 0:
                self.client.add_data_limit(
                    key.key_id,
                    CONFIG.limit_GB * 10 ** 9
                )
            return key
        except Exception as e:
            print(e, 'Outline.py Line 32')
            return False

    async def delete_client(self, telegram_id):
        client = await self.get_client(telegram_id)
        if client is not None:
            self.client.delete_key(key_id=client.key_id)

    async def get_key_user(self, name, name_key):
        client = await self.get_client(name)
        if client is None:
            key = await self.add_client(name)
            return await self.update_key_name(key.access_url, name_key)
        return await self.update_key_name(client.access_url, name_key)

    async def update_key_name(self, key, name_key):
        try:
            return key.replace('?outline=1', f'#{name_key}')
        except Exception as e:
            print(e)
        return key
