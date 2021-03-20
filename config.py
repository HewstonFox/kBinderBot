import os
from pathlib import Path

DB_URL = os.environ.get('MONGODB_URL')
TOKEN = os.environ.get('BOT_TOKEN')
LOCALES_DIR = Path(__file__).parent / 'locales'
I18N_DOMAIN = 'kBinderBot'
