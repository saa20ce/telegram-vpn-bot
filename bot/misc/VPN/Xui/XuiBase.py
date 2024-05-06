from abc import ABC

from pyxui import XUI

from bot.misc.VPN.BaseVpn import BaseVpn


class XuiBase(BaseVpn, ABC):

    NAME_VPN: str

    def __init__(self, server):
        adress = server.ip.split(':')
        adress_port = f'{adress[0]}:{adress[1]}'
        if server.connection_method:
            full_address = f'https://{adress_port}'
        else:
            full_address = f'http://{adress_port}'
        self.adress = f'{adress[0]}'
        self.xui = XUI(
            full_address=full_address,
            panel=server.panel,
            https=server.connection_method
        )
        self.inbound_id = int(server.inbound_id)
        self.xui.login(username=server.login, password=server.password)

    async def get_inbound_server(self):
        try:
            info = self.xui.get_inbounds()['obj']
            for inbound in info:
                if inbound['id'] == self.inbound_id:
                    return inbound
        except IndexError:
            return "Error inbound"

    async def get_all_user_server(self):
        try:
            inbound_server = await self.get_inbound_server()
            return inbound_server.get('clientStats')
        except IndexError:
            return "Error inbound"
