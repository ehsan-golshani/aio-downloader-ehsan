import os
import hashlib

BOT_TOKEN = os.environ.get('BALE_TOKEN')
REQUIRED_HASH = os.environ.get('BOT_PASSWORD_HASH')
SALT = os.environ.get('PASSWORD_SALT')

BOT_ROOT = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BOT_ROOT, 'files')

ALLOWED_DIRS = {
    'downloads': os.path.join(FILES_DIR, 'downloads'),
    'telegram': os.path.join(FILES_DIR, 'telegram'),
    'google-play': os.path.join(FILES_DIR, 'google-play'),
}

def verify_password(pwd):
    if not REQUIRED_HASH or not SALT:
        return False
    h = hashlib.sha256((pwd + SALT).encode()).hexdigest()
    return h == REQUIRED_HASH
