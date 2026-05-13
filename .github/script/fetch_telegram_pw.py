#!/usr/bin/env python3
# .github/scripts/fetch_telegram_pw.py

import asyncio
import json
import os
import re
import time
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import jdatetime
import requests
from playwright.async_api import async_playwright

# ==================== تنظیمات اولیه ====================
REPO_ROOT = Path(os.getenv('GITHUB_WORKSPACE', Path.cwd()))
CHANNELS_FILE = REPO_ROOT / "telegram" / "channels.json"
STATE_FILE = REPO_ROOT / "telegram" / "last_ids.json"
DATA_DIR = REPO_ROOT / "telegram" / "data"
CONTENT_DIR = REPO_ROOT / "telegram" / "content"
IRAN_TZ = ZoneInfo("Asia/Tehran")

# ---------- مهم: آدرس مخزن جدید را اینجا یک بار ست کن ----------
REPO_OWNER = os.getenv("REPO_OWNER", "ehsan-golshani")
REPO_NAME = os.getenv("REPO_NAME", "aio-downloader-ehsan")
RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
MESSAGES_PER_PAGE = 20
MAX_SCROLLS = 25

# ==================== توابع کمکی ====================
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
    if not content_type:
        return None
    ct = content_type.lower()
    if 'image/jpeg' in ct or 'image/jpg' in ct: return '.jpg'
    if 'image/png' in ct: return '.png'
    if 'video/mp4' in ct: return '.mp4'
    if 'video/webm' in ct: return '.webm'
    if 'application/pdf' in ct: return '.pdf'
    if 'application/zip' in ct: return '.zip'
    if 'application/x-tar' in ct: return '.tar'
    return None

def fix_filename_extension(filename, content_type):
    if not filename:
        return None
    current_ext = Path(filename).suffix.lower()
    known_exts = ['.npvt', '.inpvt', '.ovpn', '.8nptv']
    if current_ext in known_exts:
        return filename
    correct_ext = get_extension_from_content_type(content_type)
    if correct_ext and not current_ext:
        return filename + correct_ext
    return filename

def download_media(url, channel_name, post_id, original_filename=None):
    if not url:
        return None
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    url = url.strip()
    if url.startswith('/'):
        url = f"https://t.me{url}"
    elif url.startswith('//'):
        url = f"https:{url}"

    if original_filename:
        base_filename = original_filename
    else:
        base_filename = f"{channel_name}_{post_id}"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=60)
        resp.raise_for_status()
        content_type = resp.headers.get('Content-Type', '').lower()
        final_filename = fix_filename_extension(base_filename, content_type)
        if not Path(final_filename).suffix:
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

def fix_media_url(url):
    if not url:
        return ''
    if url.startswith('http'):
        return url
    if url.startswith('/'):
        return f"{RAW_BASE}{url}"
    if url.startswith('telegram/content/'):
        return f"{RAW_BASE}/{url}"
    return f"{RAW_BASE}/telegram/{url}"

# ==================== اسکرپینگ تلگرام ====================
async def scrape_messages(page, channel_name, target_count, last_id):
    url = f"https://t.me/s/{channel_name}"
    print(f"  🌐 Loading {url}")
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector("[data-post]", timeout=10000)
    except Exception as e:
        print(f"    ❌ Failed: {e}")
        return []

    messages, seen_ids, scroll_count = [], set(), 0
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
                if (videoEl && videoEl.src && !videoEl.src.startsWith('blob:'))
                    mediaItems.push({ type: 'video', url: videoEl.src, filename: null });
                if (!mediaItems.length) {
                    const photoWrap = el.querySelector('.tgme_widget_message_photo_wrap');
                    if (photoWrap) {
                        const style = photoWrap.getAttribute('style') || '';
                        const match = style.match(/url\\(['"]?(.*?)['"]?\\)/);
                        if (match) mediaItems.push({ type: 'photo', url: match[1], filename: null });
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
        if scroll_count >= MAX_SCROLLS:
            break
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1.5)
        scroll_count += 1

    messages.sort(key=lambda x: x['id'], reverse=True)
    print(f"    ✅ Got {len(messages)} messages")
    return messages

# ==================== ذخیره‌سازی و صفحه‌بندی ====================
def save_page(channel_dir, page_num, messages, channel_name):
    file_path = channel_dir / f"page_{page_num}.md"
    now = jdatetime.datetime.now(IRAN_TZ).strftime('%Y/%m/%d %H:%M')
    content = f"# آرشیو کانال {channel_name} - صفحه {page_num}\n\n📅 آخرین بروزرسانی: {now}\n\n---\n\n"
    for msg in messages:
        content += f"## {channel_name} — post {msg['id']}\n\n"
        for media in msg.get('mediaItems', []):
            if media['type'] == 'photo' and media.get('url'):
                content += f'<div align="center"><img src="{fix_media_url(media["url"])}" alt="Photo"></div>\n\n'
            elif media['type'] == 'video' and media.get('url'):
                content += f'<div align="center"><video src="{fix_media_url(media["url"])}" controls style="max-width:100%; border-radius:12px;"></video></div>\n\n'
                content += f'<div align="center"><a href="{fix_media_url(media["url"])}" target="_blank" style="color:#2ea4d9;">🎬 دانلود ویدیو</a></div>\n\n'
            elif media['type'] == 'document' and media.get('url'):
                fname = media.get('filename', 'فایل')
                content += f'<div align="center"><a href="{fix_media_url(media["url"])}" target="_blank" class="file-link" style="color:#2ea4d9;">📎 {fname}</a></div>\n\n'
        if msg.get('text'):
            content += f'<div dir="rtl" style="font-family: Vazirmatn, Tahoma, sans-serif;">\n{msg["text"]}\n</div>\n\n'
    file_path.write_text(content, encoding='utf-8')
    print(f"    💾 Saved page {page_num} with {len(messages)} messages")

# ==================== پردازش اصلی ====================
async def process_channel(page, channel_name, state):
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
        return 0
    new_messages = [m for m in messages if m['id'] not in existing_ids]
    if not new_messages:
        return 0

    for msg in new_messages:
        for media in msg.get('mediaItems', []):
            if media['type'] in ('photo', 'video', 'document'):
                media['url'] = download_media(media['url'], channel_name, msg['id'], media.get('filename'))

    all_messages = []
    for _, file_path in get_page_files(channel_dir):
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

    pages = {}
    for i in range(0, len(all_messages), MESSAGES_PER_PAGE):
        page_num = i // MESSAGES_PER_PAGE + 1
        pages[page_num] = all_messages[i:i + MESSAGES_PER_PAGE]

    for page_num, page_msgs in pages.items():
        save_page(channel_dir, page_num, page_msgs, channel_name)

    existing_pages = get_page_files(channel_dir)
    for page_num, file_path in existing_pages:
        if page_num not in pages:
            file_path.unlink()

    new_last_id = max(m['id'] for m in new_messages)
    state[channel_name] = max(last_id, new_last_id)
    print(f"   ✅ Added {len(new_messages)} messages, reorganized into {len(pages)} pages")
    return len(new_messages)

# ==================== اجرای اصلی ====================
async def main():
    channels = load_channels()
    target_channel = os.getenv("TARGET_CHANNEL")
    if target_channel:
        clean = target_channel.lstrip('@')
        if clean in channels:
            channels = [clean]
            print(f"🎯 Custom archive for: {clean}")
        else:
            print(f"❌ Channel '{target_channel}' not found")
            return

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