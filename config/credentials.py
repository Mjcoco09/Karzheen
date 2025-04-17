import os
from dotenv import load_dotenv

load_dotenv()

class Credentials:
    @staticmethod
    def get_telegram_token():
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        return token

    @staticmethod
    def get_quotex_credentials():
        email = os.getenv('QUOTEX_EMAIL')
        password = os.getenv('QUOTEX_PASSWORD')
        
        if not email or not password:
            raise ValueError("Quotex credentials not found in environment variables")
        
        return {
            'email': email,
            'password': password
        }

    @staticmethod
    def get_admin_ids():
        admin_ids_str = os.getenv('ADMIN_USER_IDS', '')
        if not admin_ids_str:
            return []
        return [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()] 