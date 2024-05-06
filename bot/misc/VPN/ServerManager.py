from bot.misc.VPN.Xui.Vless import Vless
from bot.misc.VPN.Xui.Shadowsocks import Shadowsocks
from bot.misc.VPN.Outline import Outline


class ServerManager:
    VPN_TYPES = {0: Outline, 1: Vless, 2: Shadowsocks}

    def __init__(self, server):
        try:
            self.client = self.VPN_TYPES.get(server.type_vpn)(server)
        except Exception as e:
            print(e, 'ServerManager.py Line 13')

    async def get_all_user(self):
        try:
            return await self.client.get_all_user_server()
        except Exception as e:
            print(e, 'ServerManager.py Line 19')

    async def get_user(self, name):
        try:
            return await self.client.get_client(str(name))
        except Exception as e:
            print(e, 'ServerManager.py Line 25')

    async def add_client(self, name):
        try:
            return await self.client.add_client(str(name))
        except Exception as e:
            print(e, 'ServerManager.py Line 31')

    async def delete_client(self, name):
        try:
            await self.client.delete_client(str(name))
            return True
        except Exception as e:
            print(e, 'ServerManager.py Line 38')
            return False

    async def get_key(self, name, name_key):
        try:
            return await self.client.get_key_user(str(name), str(name_key))
        except Exception as e:
            print(e, 'ServerManager.py Line 45')
