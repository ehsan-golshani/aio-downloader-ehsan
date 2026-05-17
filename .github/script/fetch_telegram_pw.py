def download_and_save_file(url, channel_name, post_id, media_type, original_filename):
    """دانلود فایل و ذخیره در پوشه مناسب بر اساس حجم و نوع"""
    if not url:
        return None
    
    url = url.strip()
    if url.startswith('/'):
        url = f"https://t.me{url}"
    elif url.startswith('//'):
        url = f"https:{url}"
    
    # تعیین نام فایل پایه
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
        
        # تعیین پوشه مقصد بر اساس نوع و حجم
        is_media = media_type in ['photo', 'video'] or content_type.startswith('image/') or content_type.startswith('video/')
        
        channel_dir = get_channel_dir(channel_name)
        
        if is_media:
            target_dir = get_media_dir(channel_dir)
            relative_path = f"media/{final_filename}"
            print(f"    📁 Media file -> media/ ({content_length} bytes)")
        elif content_length < MAX_SIZE_FOR_BASE64:
            target_dir = get_base64_dir(channel_dir)
            relative_path = f"file-base64/{final_filename}"
            print(f"    📁 Small file -> file-base64/ ({content_length} bytes)")
            
            # ذخیره فایل اصلی در پوشه file-base64
            target_dir.mkdir(parents=True, exist_ok=True)
            local_path = target_dir / final_filename
            local_path.write_bytes(resp.content)
            
            # ذخیره نسخه Base64 خام (بدون هیچ توضیح اضافه)
            base64_data = base64.b64encode(resp.content).decode('utf-8')
            base64_path = target_dir / (final_filename + ".base64")
            base64_path.write_text(base64_data, encoding='utf-8')
            print(f"    📁 Raw Base64 saved: {final_filename}.base64")
            
            return relative_path
        else:
            target_dir = get_media_dir(channel_dir)
            relative_path = f"media/{final_filename}"
            print(f"    📁 Large file -> media/ ({content_length} bytes)")
        
        # ذخیره فایل
        target_dir.mkdir(parents=True, exist_ok=True)
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