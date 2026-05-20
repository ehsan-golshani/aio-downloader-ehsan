import telebot, os, glob, json, hashlib
from telebot import api
api.TELEGRAM_API_URL = 'https://tapi.bale.ai/bot{0}/{1}'

from config import BOT_TOKEN, verify_password, ALLOWED_DIRS, FILES_DIR

bot = telebot.TeleBot(BOT_TOKEN)
AUTH_FILE = os.path.join(os.path.dirname(__file__), 'auth.json')

def load_auth():
    try:
        with open(AUTH_FILE, 'r') as f:
            return set(json.load(f).get('users', []))
    except:
        return set()

def save_auth(users):
    with open(AUTH_FILE, 'w') as f:
        json.dump({'users': list(users)}, f)

authorized = load_auth()

def auth_required(func):
    def wrapper(m):
        if str(m.chat.id) in authorized:
            return func(m)
        bot.reply_to(m, "🔒 لطفاً با /auth <رمز> احراز هویت کنید")
    return wrapper

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🔐 ربات شخصی\nبرای دسترسی: /auth <رمز عبور>")

@bot.message_handler(commands=['auth'])
def auth(m):
    parts = m.text.split()
    if len(parts) != 2:
        return bot.reply_to(m, "فرمت: /auth رمز")
    if verify_password(parts[1]):
        authorized.add(str(m.chat.id))
        save_auth(authorized)
        bot.reply_to(m, "✅ احراز هویت شد")
    else:
        bot.reply_to(m, "❌ رمز اشتباه")

@bot.message_handler(commands=['list'])
@auth_required
def list_files(m):
    files = []
    for name, path in ALLOWED_DIRS.items():
        if os.path.exists(path):
            for f in glob.glob(os.path.join(path, '*')):
                if os.path.isfile(f):
                    files.append(f"📁 {name}: {os.path.basename(f)}")
    bot.reply_to(m, "\n".join(files) if files else "هیچ فایلی نیست")

@bot.message_handler(commands=['download'])
@auth_required
def download(m):
    name = ' '.join(m.text.split()[1:])
    if not name:
        return bot.reply_to(m, "نام فایل را وارد کنید")
    for path in ALLOWED_DIRS.values():
        for f in glob.glob(os.path.join(path, '*')):
            if os.path.basename(f) == name:
                with open(f, 'rb') as file:
                    bot.send_document(m.chat.id, file)
                return
    bot.reply_to(m, "فایل یافت نشد")

@bot.message_handler(commands=['folders'])
@auth_required
def folders(m):
    text = "پوشه‌ها:\n" + "\n".join([f"• {n}: {p}" for n,p in ALLOWED_DIRS.items()])
    bot.reply_to(m, text)

print("ربات شروع به کار کرد")
bot.infinity_polling()
