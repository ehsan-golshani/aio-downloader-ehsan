#!/usr/bin/env python3
"""
Telegram Channel Archiver - نسخه نهایی با پشتیبانی کامل از فایل و ویدیو
"""

import asyncio
import argparse
import json
import mimetypes
import re
import sys
import time
from pathlib import Path
from zoneinfo import ZoneInfo

import jdatetime
import requests
from playwright.async_api import async_playwright

# ========== تنظیمات ==========
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

CHANNELS_FILE = REPO_ROOT / "telegram" / "channels.json"
STATE_FILE = REPO_ROOT / "telegram" / "last_ids.json"
DATA_DIR = REPO_ROOT / "telegram" / "data"
CONTENT_DIR = REPO_ROOT / "telegram" / "content"

IRAN_TZ = ZoneInfo("Asia/Tehran")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
MESSAGES_PER_PAGE = 20

parser = argparse.ArgumentParser()
parser.add_argument('--channel', type=str, default=None)
parser.add_argument('--limit', type=int, default=0)
parser.add_argument('--force', action='store_true')
args = parser.parse_args()

TARGET_CHANNEL = args.channel
CUSTOM_MODE = args.limit > 0

print("=" * 50)
print("🚀 Telegram Archiver - نسخه نهایی")
print(f"📢 Channel: {TARGET_CHANNEL or 'ALL'}")
print("=" * 50)

# ========== توابع کمکی ==========
def load_channels():
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_channel_dir(channel_name):
    channel_dir = DATA_DIR / channel_name
    channel_dir.mkdir(parents=True, exist_ok=True)
    return channel_dir

def get_page_files(channel_dir):
    files = list(channel_dir.glob("page_*.md"))
    pages = []
    for f in files:
        match = re.search(r'page_(\d+)\.md', f.name)
        if match:
            pages.append((int(match.group(1)), f))
    pages.sort(key=lambda x: x[0])
    return pages

def get_existing_ids(channel_dir):
    all_ids = set()
    for _, file_path in get_page_files(channel_dir):
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            ids = re.findall(r'post (\d+)', content)
            all_ids.update(int(i) for i in ids)
    return all_ids

def get_extension_from_content_type(content_type):
    """دریافت پسوند مناسب از Content-Type"""
    if not content_type:
        return None
    
    content_type = content_type.lower()
    
    # تصاویر
    if 'image/jpeg' in content_type or 'image/jpg' in content_type:
        return '.jpg'
    if 'image/png' in content_type:
        return '.png'
    if 'image/gif' in content_type:
        return '.gif'
    if 'image/webp' in content_type:
        return '.webp'
    
    # ویدیوها
    if 'video/mp4' in content_type:
        return '.mp4'
    if 'video/webm' in content_type:
        return '.webm'
    if 'video/quicktime' in content_type:
        return '.mov'
    if 'video/x-msvideo' in content_type:
        return '.avi'
    
    # اسناد
    if 'application/pdf' in content_type:
        return '.pdf'
    if 'application/zip' in content_type:
        return '.zip'
    if 'application/x-rar-compressed' in content_type:
        return '.rar'
    if 'application/x-tar' in content_type:
        return '.tar'
    if 'application/x-gzip' in content_type:
        return '.gz'
    
    # کانفیگ‌ها
    if 'text/plain' in content_type:
        return '.txt'
    
    return None

def get_extension_from_filename(filename):
    """دریافت پسوند از نام فایل"""
    if not filename:
        return None
    
    # لیست پسوندهای معروف
    known_extensions = [
        '.jpg', '.jpeg', '.png', '.gif', '.webp',
        '.mp4', '.webm', '.mov', '.avi', '.mkv',
        '.pdf', '.zip', '.rar', '.7z', '.tar', '.gz',
        '.mp3', '.wav', '.flac', '.ogg',
        '.apk', '.exe', '.msi',
        '.npvt', '.inpvt', '.ovpn', '.8nptv',    # کانفیگ‌های خاص
        '.txt', '.json', '.xml', '.yml', '.yaml',
        '.html', '.css', '.js'
    ]
    
    lower_name = filename.lower()
    for ext in known_extensions:
        if lower_name.endswith(ext):
            return ext
    
    return None

def fix_filename_extension(filename, content_type):
    """اصلاح پسوند فایل بر اساس نام و Content-Type"""
    if not filename:
        return None
    
    # حذف کاراکترهای اضافی
    filename = filename.strip()
    
    # استخراج پسوند فعلی
    current_ext = get_extension_from_filename(filename)
    correct_ext = get_extension_from_content_type(content_type)
    
    # اگه پسوند درستی داره، همون رو برگردون
    if current_ext and correct_ext and current_ext == correct_ext:
        return filename
    
    # اگه پسوند فعلی در لیست معروف هاست، حفظش کن
    if current_ext in ['.npvt', '.inpvt', '.ovpn', '.8nptv']:
        return filename
    
    # اگه پسوند درستی از Content-Type داریم و فعلی نداریم
    if correct_ext and not current_ext:
        return filename + correct_ext
    
    # اگه فایل بدون پسونده (مثل Audio)
    if not current_ext and correct_ext:
        return filename + correct_ext
    
    return filename

def download_media(url, channel_name, post_id, media_type='photo', original_filename=None):
    """دانلود مدیا با مدیریت خطا و پسوند صحیح"""
    if not url:
        return None
    
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    
    url = url.strip()
    if url.startswith('/'):
        url = f"https://t.me{url}"
    elif url.startswith('//'):
        url = f"https:{url}"
    
    # تعیین نام فایل
    if original_filename:
        base_filename = original_filename
    else:
        base_filename = f"{channel_name}_{post_id}"
    
    try:
        print(f"    📥 Downloading: {url[:80]}...")
        resp = requests.get(url, headers=HEADERS, timeout=60)
        resp.raise_for_status()
        
        content_type = resp.headers.get('Content-Type', '').lower()
        
        # اصلاح نام فایل
        final_filename = fix_filename_extension(base_filename, content_type)
        
        # اگه هنوز پسوند نداره، از Content-Type استفاده کن
        if not get_extension_from_filename(final_filename):
            ext = get_extension_from_content_type(content_type)
            if ext:
                final_filename += ext
            else:
                final_filename += '.dat'
        
        local_path = CONTENT_DIR / final_filename
        
        if local_path.exists():
            print(f"    📁 Already exists: {final_filename}")
            return f"telegram/content/{final_filename}"
        
        local_path.write_bytes(resp.content)
        print(f"    ✅ Downloaded: {final_filename}")
        return f"telegram/content/{final_filename}"
        
    except Exception as e:
        print(f"    ⚠️ Download failed: {e}")
        return None

async def scrape_messages(page, channel_name, target_count, last_id):
    """دریافت پیام‌ها با مدیا"""
    url = f"https://t.me/s/{channel_name}"
    print(f"  🌐 Loading {url}")
    
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector("[data-post]", timeout=10000)
    except Exception as e:
        print(f"    ❌ Failed: {e}")
        return []
    
    messages = []
    seen_ids = set()
    scroll_count = 0
    max_scrolls = 25
    
    while True:
        new_msgs = await page.evaluate("""() => {
            const results = [];
            for (const el of document.querySelectorAll('[data-post]')) {
                const dataPost = el.getAttribute('data-post');
                if (!dataPost) continue;
                const parts = dataPost.split('/');
                if (parts.length < 2) continue;
                const postId = parseInt(parts[1]);
                if (isNaN(postId)) continue;
                
                const textEl = el.querySelector('.tgme_widget_message_text');
                let text = textEl ? textEl.innerText : '';
                
                let mediaItems = [];
                
                // 1. ویدیو
                const videoEl = el.querySelector('video');
                if (videoEl && videoEl.src && !videoEl.src.startsWith('blob:')) {
                    mediaItems.push({ type: 'video', url: videoEl.src, filename: null });
                }
                
                // 2. عکس
                if (mediaItems.length === 0) {
                    const photoWrap = el.querySelector('.tgme_widget_message_photo_wrap');
                    if (photoWrap) {
                        const style = photoWrap.getAttribute('style') || '';
                        const match = style.match(/url\\(['"]?(.*?)['"]?\\)/);
                        if (match) {
                            mediaItems.push({ type: 'photo', url: match[1], filename: null });
                        }
                    }
                }
                
                // 3. فایل ضمیمه
                const docWrap = el.querySelector('a.tgme_widget_message_document_wrap');
                if (docWrap) {
                    const docUrl = docWrap.getAttribute('href');
                    if (docUrl) {
                        let filename = null;
                        const nameEl = docWrap.querySelector('.tgme_widget_message_document_title');
                        if (nameEl) filename = nameEl.innerText;
                        if (!filename) filename = docUrl.split('/').pop() || 'file';
                        
                        mediaItems.push({ type: 'document', url: docUrl, filename: filename });
                    }
                }
                
                results.push({ id: postId, text: text, mediaItems: mediaItems });
            }
            return results;
        }""")
        
        for msg in new_msgs:
            if msg['id'] not in seen_ids:
                seen_ids.add(msg['id'])
                if target_count > 0:
                    if len(messages) < target_count:
                        messages.append(msg)
                else:
                    if msg['id'] > last_id:
                        messages.append(msg)
        
        if messages and target_count == 0:
            oldest = min(m['id'] for m in messages)
            if oldest <= last_id:
                break
        
        if target_count > 0 and len(messages) >= target_count:
            messages = messages[:target_count]
            break
        
        if scroll_count >= max_scrolls:
            break
        
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1.5)
        scroll_count += 1
    
    messages.sort(key=lambda x: x['id'], reverse=True)
    print(f"    ✅ Got {len(messages)} messages")
    return messages

def save_page(channel_dir, page_num, messages, channel_name):
    """ذخیره صفحه با فرمت Markdown"""
    file_path = channel_dir / f"page_{page_num}.md"
    
    now = jdatetime.datetime.now(IRAN_TZ).strftime('%Y/%m/%d %H:%M')
    
    content = f"# آرشیو کانال {channel_name} - صفحه {page_num}\n\n"
    content += f"📅 آخرین بروزرسانی: {now}\n\n---\n\n"
    
    for msg in messages:
        content += f"## {channel_name} — post {msg['id']}\n\n"
        
        # نمایش مدیاها
        for media in msg.get('mediaItems', []):
            if media['type'] == 'photo' and media.get('url'):
                content += f'<div align="center"><img src="{media["url"]}" alt="Photo"></div>\n\n'
            elif media['type'] == 'video' and media.get('url'):
                content += f'<div align="center"><video src="{media["url"]}" controls style="max-width:100%; border-radius:12px;"></video></div>\n\n'
                content += f'<div align="center"><a href="{media["url"]}" target="_blank" style="color:#2ea4d9;">🎬 دانلود ویدیو</a></div>\n\n'
            elif media['type'] == 'document' and media.get('url'):
                fname = media.get('filename', 'فایل')
                content += f'<div align="center"><a href="{media["url"]}" target="_blank" class="file-link" style="color:#2ea4d9;">📎 {fname}</a></div>\n\n'
        
        # متن پیام
        if msg.get('text'):
            content += f'<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">\n{msg["text"]}\n</div>\n\n'
    
    file_path.write_text(content, encoding='utf-8')
    print(f"    💾 Saved page {page_num} with {len(messages)} messages")
    return file_path

async def process_channel(page, channel_name, state):
    """پردازش یک کانال"""
    channel_dir = get_channel_dir(channel_name)
    existing_ids = get_existing_ids(channel_dir)
    last_id = state.get(channel_name, 0)
    
    is_new = len(existing_ids) == 0
    
    if is_new:
        print(f"\n📡 {channel_name}: New channel - fetching first {MESSAGES_PER_PAGE} messages")
        messages = await scrape_messages(page, channel_name, MESSAGES_PER_PAGE, 0)
    else:
        print(f"\n📡 {channel_name}: Checking for new messages after ID {last_id}")
        messages = await scrape_messages(page, channel_name, 0, last_id)
    
    if not messages:
        print(f"   ℹ️ No new messages")
        return 0
    
    # فیلتر پیام‌های تکراری
    new_messages = [m for m in messages if m['id'] not in existing_ids]
    
    if not new_messages:
        print(f"   ℹ️ All messages already exist")
        return 0
    
    # دانلود مدیاها
    for msg in new_messages:
        for media in msg.get('mediaItems', []):
            if media['type'] == 'photo':
                media['url'] = download_media(media['url'], channel_name, msg['id'], 'photo')
            elif media['type'] == 'video':
                media['url'] = download_media(media['url'], channel_name, msg['id'], 'video')
            elif media['type'] == 'document':
                media['url'] = download_media(media['url'], channel_name, msg['id'], 'document', media.get('filename'))
    
    # جمع‌آوری همه پیام‌ها
    all_messages = []
    
    # خواندن پیام‌های موجود
    for _, file_path in get_page_files(channel_dir):
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            blocks = re.split(r'\n(?=## )', content)
            for block in blocks:
                pid_match = re.search(r'post (\d+)', block)
                if pid_match:
                    pid = int(pid_match.group(1))
                    
                    # استخراج مدیاهای موجود
                    media_items = []
                    img_matches = re.findall(r'<img src="([^"]+)"', block)
                    for img in img_matches:
                        media_items.append({'type': 'photo', 'url': img})
                    
                    video_matches = re.findall(r'<video src="([^"]+)"', block)
                    for vid in video_matches:
                        media_items.append({'type': 'video', 'url': vid})
                    
                    file_matches = re.findall(r'class="file-link"[^>]*>📎 ([^<]+)</a>', block)
                    for fname in file_matches:
                        media_items.append({'type': 'document', 'url': '', 'filename': fname})
                    
                    text_match = re.search(r'<div dir="rtl"[^>]*>(.*?)</div>', block, re.DOTALL)
                    text = re.sub(r'<[^>]+>', '', text_match.group(1) if text_match else '').strip()
                    
                    all_messages.append({'id': pid, 'text': text, 'mediaItems': media_items})
    
    # اضافه کردن پیام‌های جدید
    all_messages.extend(new_messages)
    all_messages.sort(key=lambda x: x['id'], reverse=True)
    
    # بازسازی صفحات
    pages = {}
    for i in range(0, len(all_messages), MESSAGES_PER_PAGE):
        page_num = i // MESSAGES_PER_PAGE + 1
        pages[page_num] = all_messages[i:i + MESSAGES_PER_PAGE]
    
    # ذخیره صفحات
    for page_num, page_msgs in pages.items():
        save_page(channel_dir, page_num, page_msgs, channel_name)
    
    # حذف صفحات اضافی
    existing_pages = get_page_files(channel_dir)
    for page_num, file_path in existing_pages:
        if page_num not in pages:
            file_path.unlink()
    
    # به‌روزرسانی state
    new_last_id = max(m['id'] for m in new_messages)
    state[channel_name] = max(last_id, new_last_id)
    
    print(f"   ✅ Added {len(new_messages)} messages, reorganized into {len(pages)} pages")
    return len(new_messages)

async def main():
    channels = load_channels()
    
    if TARGET_CHANNEL:
        clean = TARGET_CHANNEL.lstrip('@')
        if clean in channels:
            channels = [clean]
            print(f"🎯 Target channel: {clean}")
        else:
            print(f"❌ Channel '{TARGET_CHANNEL}' not found")
            sys.exit(1)
    
    state = load_state()
    total = 0
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        for ch in channels:
            total += await process_channel(page, ch, state)
        
        await browser.close()
    
    save_state(state)
    print(f"\n✅ Done! Total new messages added: {total}")

if __name__ == "__main__":
    asyncio.run(main())