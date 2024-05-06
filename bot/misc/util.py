import json
import os


class Config:
    admin_tg_id: int
    month_cost: list
    deposit: list
    auto_extension: bool = False
    trial_period: int
    UTC_time: int
    max_people_server: int
    limit_ip: int
    limit_GB: int
    tg_token: str
    yoomoney_token: str
    yoomoney_wallet_token: str
    tg_wallet_token: str
    lava_token_secret: str
    lava_id_project: str
    yookassa_shop_id: str
    yookassa_secret_key: str
    recurring_payment_amount: int
    recurring_payment_interval_days: int
    recurring_payment_interval_minutes: int
    referral_day: int
    referral_percent: int
    minimum_withdrawal_amount: int
    COUNT_SECOND_DAY: int = 86400
    COUNT_SECOND_MOTH: int = 2678400
    languages: str
    name: str
    id_channel: int = 1
    link_channel: str = ''

    def __init__(self):
        try:
            with open('config.json', encoding="utf-8") as file_handler:
                text_mess = json.load(file_handler)
            for k, v in text_mess.items():
                setattr(self, k, v)

        except FileNotFoundError as e:
            text_error = (f'Файла config.json не существует\n'
                          f'Скопируйте из архива и вставьте в корень проекта\n'
                          f'{e}')
            raise FileNotFoundError(text_error)
        except ValueError as e:
            text_error = (f'Вы допустили ошибку в файле config.json\n'
                          f'Проверьте там должна быть такая структура:\n'
                          f'{{\n'
                          f'"value1":"текст",\n'
                          f'"value2": 150 \n '
                          f'}}\n'
                          f'{e}')
            raise ValueError(text_error)
        self.write_env()

    def write_env(self):
        self.admin_tg_id = (
            int(os.getenv("ADMIN_ID", 11111))
            if self.admin_tg_id == 11111
            else self.admin_tg_id
        )
        self.tg_wallet_token = (
            os.getenv("WALLET", "")
            if self.tg_wallet_token == ""
            else self.tg_wallet_token
        )
        self.yookassa_shop_id = (
            os.getenv("YOOKASSA_SHOP_ID", "")
            if self.yookassa_shop_id == ""
            else self.yookassa_shop_id
        )
        self.yookassa_secret_key = (
            os.getenv("YOOKASSA_SECRET_KEY", "")
            if self.yookassa_secret_key == ""
            else self.yookassa_secret_key
        )
        self.yoomoney_token = (
            os.getenv("YOOMONEY_TOKEN", "")
            if self.yoomoney_token == ""
            else self.yoomoney_token
        )
        self.yoomoney_wallet_token = (
            os.getenv("YOOMONEY_WALLET", "")
            if self.yoomoney_wallet_token == ""
            else self.yoomoney_wallet_token
        )
        self.lava_token_secret = (
            os.getenv("LAVA_TOKEN", "")
            if self.lava_token_secret == ""
            else self.lava_token_secret
        )
        self.lava_id_project = (
            os.getenv("LAVA_ID", "")
            if self.lava_id_project == ""
            else self.lava_id_project
        )


CONFIG = Config()
