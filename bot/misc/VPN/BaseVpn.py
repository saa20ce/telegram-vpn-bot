from abc import ABC, abstractmethod


class BaseVpn(ABC):

    NAME_VPN: str

    @abstractmethod
    async def get_all_user_server(self):
        pass

    @abstractmethod
    async def get_client(self, name):
        pass

    @abstractmethod
    async def add_client(self, name):
        pass

    @abstractmethod
    async def delete_client(self, telegram_id):
        pass

    @abstractmethod
    async def get_key_user(self, name, name_key):
        pass
