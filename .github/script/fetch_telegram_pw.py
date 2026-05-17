#!/usr/bin/env python3
"""
Telegram Channel Archiver - نسخه نهایی با ساختار جدید
- هر کانال در پوشه مجزا
- pages/ برای فایل‌های Markdown
- media/ برای عکس، ویدیو، فایل‌های حجیم (>1MB)
- file-base64/ برای فایل‌های کوچک (<1MB) با تبدیل Base64
"""

import asyncio
import argparse
import base64
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
CONTENT_DIR = REPO_ROOT / "telegram" / "content"  # قدیمی - برای سازگاری موقت

IRAN_TZ = ZoneInfo("Asia/Tehran")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
MESSAGES_PER_PAGE = 20
MAX_SIZE_FOR_BASE64 = 1024 * 1024  # 1 مگابایت

parser = argparse.ArgumentParser()
parser.add_argument('--channel', type=str, default=None)
parser.add_argument('--limit', type=int, default=0)
parser.add_argument('--force', action='store_true')
args = parser.parse_args()

TARGET_CHANNEL = args.channel
CUSTOM_MODE = args.limit > 0

print("=" * 50)
print("🚀 Telegram Archiver - نسخه نهایی با ساختار جدید")
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
    """دریافت پوشه اصلی کانال"""
    channel_dir = DATA_DIR / channel_name
    channel_dir.mkdir(parents=True, exist_ok=True)
    return channel_dir

def get_pages_dir(channel_dir):
    """پوشه فایل‌های صفحه (Markdown)"""
    pages_dir = channel_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    return pages_dir

def get_media_dir(channel_dir):
    """پوشه فایل‌های مدیا (عکس، ویدیو، فایل‌های حجیم)"""
    media_dir = channel_dir / "media"
    media_dir.mkdir(parents=True, exist_ok=True)
    return media_dir

def get_base64_dir(channel_dir):
    """پوشه فایل‌های Base64 (کانفیگ‌ها و فایل‌های کوچک)"""
    base64_dir = channel_dir / "file-base64"
    base64_dir.mkdir(parents=True, exist_ok=True)
    return base64_dir

def get_page_files(pages_dir):
    files = list(pages_dir.glob("page_*.md"))
    pages = []
    for f in files:
        match = re.search(r'page_(\d+)\.md', f.name)
        if match:
            pages.append((int(match.group(1)), f))
    pages.sort(key=lambda x: x[0])
    return pages

def get_existing_ids(pages_dir):
    all_ids = set()
    for _, file_path in get_page_files(pages_dir):
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            ids = re.findall(r'post (\d+)', content)
            all_ids.update(int(i) for i in ids)
    return all_ids

def get_extension_from_content_type(content_type):
    if not content_type:
        return None
    content_type = content_type.lower()
    if 'image/jpeg' in content_type or 'image/jpg' in content_type:
        return '.jpg'
    if 'image/png' in content_type:
        return '.png'
    if 'image/gif' in content_type:
        return '.gif'
    if 'image/webp' in content_type:
        return '.webp'
    if 'video/mp4' in content_type:
        return '.mp4'
    if 'video/webm' in content_type:
        return '.webm'
    if 'video/quicktime' in content_type:
        return '.mov'
    if 'application/pdf' in content_type:
        return '.pdf'
    if 'application/zip' in content_type:
        return '.zip'
    if 'text/plain' in content_type:
        return '.txt'
    return None

def get_extension_from_filename(filename):
    if not filename:
        return None
    known_extensions = [
        '.jpg', '.jpeg', '.png', '.gif', '.webp',
        '.mp4', '.webm', '.mov', '.avi', '.mkv',
        '.pdf', '.zip', '.rar', '.7z', '.tar', '.gz',
        '.mp3', '.wav', '.flac', '.ogg',
        '.apk', '.exe', '.msi',
        '.npvt', '.inpvt', '.ovpn', '.8nptv',
        '.txt', '.json', '.xml', '.yml', '.yaml'
    ]
    lower_name = filename.lower()
    for ext in known_extensions:
        if lower_name.endswith(ext):
            return ext
    return None

def fix_filename_extension(filename, content_type):
    if not filename:
        return None
    filename = filename.strip()
    current_ext = get_extension_from_filename(filename)
    correct_ext = get_extension_from_content_type(content_type)
    if current_ext in ['.npvt', '.inpvt', '.ovpn', '.8nptv']:
        return filename
    if correct_ext and not current_ext:
        return filename + correct_ext
    if not current_ext and correct_ext:
        return filename + correct_ext
    return filename

def convert_to_base64(file_path):
    """تبدیل فایل به Base64 و بازگشت محتوا"""
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
            base64_data = base64.b64encode(file_data).decode('utf-8')
            return base64_data
    except Exception as e:
        print(f"    ⚠️ Base64 conversion failed: {e}")
        return None

def save_base64_file(base64_dir, filename, base64_data, original_filename=None):
    """ذخیره فایل Base64 به صورت .txt با اطلاعات کامل"""
    base64_filename = filename
    if not base64_filename.endswith('.txt'):
        base64_filename = filename + '.txt'
    file_path = base64_dir / base64_filename
    
    # ایجاد محتوای HTML ساده برای دانلود
    html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>{filename}</title></head>
<body>
<pre style="word-wrap:break-word; white-space:pre-wrap; font-family:monospace; font-size:12px;">
این فایل به صورت Base64 ذخیره شده است. برای دانلود فایل اصلی، کد زیر را کپی کرده و در یک دیکودر Base64 قرار دهید.

نام فایل اصلی: {original_filename or filename}
تاریخ ایجاد: {jdatetime.datetime.now(IRAN_TZ).strftime('%Y/%m/%d %H:%M:%S')}

========== کد Base64 ==========

{base64_data}

========== پایان کد ==========

برای تبدیل به فایل اصلی، می‌توانید از ابزارهای آنلاین دیکود Base64 استفاده کنید.
</pre>
</body>
</html>"""
    
    file_path.write_text(html_content, encoding='utf-8')
    print(f"    📁 Saved Base64 file: {base64_filename}")
    return f"file-base64/{base64_filename}"

def download_and_save_file(url, channel_name, post_id, media_type, original_filename, pages_dir):
    """دانلود فایل و ذخیره در پوشه مناسب بر اساس حجم و نوع"""
    if not url:
        return None
    
    # تعیین پوشه مقصد
    channel_dir = pages_dir.parent
    media_dir = get_media_dir(channel_dir)
    base64_dir = get_base64_dir(channel_dir)
    
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
        content_length = len(resp.content)
        
        # اصلاح نام فایل
        final_filename = fix_filename_extension(base_filename, content_type)
        if not get_extension_from_filename(final_filename):
            ext = get_extension_from_content_type(content_type)
            if ext:
                final_filename += ext
            else:
                final_filename += '.dat'
        
        # عکس‌ها و ویدیوها همیشه به media میروند
        is_media = media_type in ['photo', 'video'] or content_type.startswith('image/') or content_type.startswith('video/')
        
        # تصمیم‌گیری برای پوشه مقصد
        if is_media:
            target_dir = media_dir
            relative_path = f"media/{final_filename}"
            print(f"    📁 Media file -> media/ ({content_length} bytes)")
        elif content_length < MAX_SIZE_FOR_BASE64:
            # فایل کوچک: هم فایل اصلی و هم Base64 ذخیره میشه
            target_dir = base64_dir
            relative_path = f"file-base64/{final_filename}"
            
            # ذخیره فایل اصلی در base64_dir
            local_path = target_dir / final_filename
            local_path.write_bytes(resp.content)
            
            # تبدیل به Base64 و ذخیره فایل جدا
            base64_data = base64.b64encode(resp.content).decode('utf-8')
            save_base64_file(base64_dir, final_filename, base64_data, final_filename)
            
            print(f"    📁 Small file -> file-base64/ ({content_length} bytes) + Base64")
            return relative_path
        else:
            target_dir = media_dir
            relative_path = f"media/{final_filename}"
            print(f"    📁 Large file -> media/ ({content_length} bytes)")
        
        # ذخیره فایل
        local_path = target_dir / final_filename
        if local_path.exists():
            print(f"    📁 Already exists: {final_filename}")
            return relative_path
        
        local_path.write_bytes(resp.content)
        print(f"    ✅ Downloaded: {final_filename}")
        return relative_path
        
    except Exception as e:
        print(f"    ⚠️ Download failed: {e}")
        return None

async def scrape_messages(page, channel_name, target_count, last_id):
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
                const videoEl = el.querySelector('video');
                if (videoEl && videoEl.src && !videoEl.src.startsWith('blob:')) {
                    mediaItems.push({ type: 'video', url: videoEl.src, filename: null });
                }
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

def save_page(pages_dir, page_num, messages, channel_name):
    file_path = pages_dir / f"page_{page_num}.md"
    now = jdatetime.datetime.now(IRAN_TZ).strftime('%Y/%m/%d %H:%M')
    content = f"# آرشیو کانال {channel_name} - صفحه {page_num}\n\n📅 آخرین بروزرسانی: {now}\n\n---\n\n"
    for msg in messages:
        content += f"## {channel_name} — post {msg['id']}\n\n"
        for media in msg.get('mediaItems', []):
            if media['type'] == 'photo' and media.get('url'):
                content += f'<div align="center"><img src="{media["url"]}" alt="Photo"></div>\n\n'
            elif media['type'] == 'video' and media.get('url'):
                content += f'<div align="center"><video src="{media["url"]}" controls style="max-width:100%; border-radius:12px;"></video></div>\n\n'
                content += f'<div align="center"><a href="{media["url"]}" target="_blank" style="color:#2ea4d9;">🎬 دانلود ویدیو</a></div>\n\n'
            elif media['type'] == 'document' and media.get('url'):
                fname = media.get('filename', 'فایل')
                content += f'<div align="center"><a href="{media["url"]}" target="_blank" class="file-link" style="color:#2ea4d9;">📎 {fname}</a></div>\n\n'
        if msg.get('text'):
            content += f'<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">\n{msg["text"]}\n</div>\n\n'
    file_path.write_text(content, encoding='utf-8')
    print(f"    💾 Saved page {page_num} with {len(messages)} messages")
    return file_path

async def process_channel(page, channel_name, state):
    channel_dir = get_channel_dir(channel_name)
    pages_dir = get_pages_dir(channel_dir)
    existing_ids = get_existing_ids(pages_dir)
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
    
    new_messages = [m for m in messages if m['id'] not in existing_ids]
    if not new_messages:
        print(f"   ℹ️ All messages already exist")
        return 0
    
    # دانلود و ذخیره مدیاها
    for msg in new_messages:
        for media in msg.get('mediaItems', []):
            if media['type'] == 'photo':
                media['url'] = download_and_save_file(media['url'], channel_name, msg['id'], 'photo', None, pages_dir)
            elif media['type'] == 'video':
                media['url'] = download_and_save_file(media['url'], channel_name, msg['id'], 'video', None, pages_dir)
            elif media['type'] == 'document':
                media['url'] = download_and_save_file(media['url'], channel_name, msg['id'], 'document', media.get('filename'), pages_dir)
    
    # جمع‌آوری پیام‌های موجود
    all_messages = []
    for _, file_path in get_page_files(pages_dir):
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            blocks = re.split(r'\n(?=## )', content)
            for block in blocks:
                pid_match = re.search(r'post (\d+)', block)
                if pid_match:
                    pid = int(pid_match.group(1))
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
    
    all_messages.extend(new_messages)
    all_messages.sort(key=lambda x: x['id'], reverse=True)
    
    # بازسازی صفحات
    pages = {}
    for i in range(0, len(all_messages), MESSAGES_PER_PAGE):
        page_num = i // MESSAGES_PER_PAGE + 1
        pages[page_num] = all_messages[i:i + MESSAGES_PER_PAGE]
    
    for page_num, page_msgs in pages.items():
        save_page(pages_dir, page_num, page_msgs, channel_name)
    
    existing_pages = get_page_files(pages_dir)
    for page_num, file_path in existing_pages:
        if page_num not in pages:
            file_path.unlink()
    
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