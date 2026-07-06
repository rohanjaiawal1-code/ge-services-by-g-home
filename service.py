import xbmc
import xbmcaddon
import time
import os
import urllib.request
import random
import json
import socket
import threading
from xbmcvfs import translatePath

# ==========================================
# 🔴 GITHUB RAW JSON CONFIGURATION
# ==========================================
GITHUB_JSON_URL = "https://raw.githubusercontent.com/rohanjaiawal1-code/ge-services-by-g-home/main/users.json"

# Addon Info & Paths (Kodi 19+ Python 3 Standard)
ADDON = xbmcaddon.Addon()
ADDON_PATH = translatePath(ADDON.getAddonInfo('path'))

LOCAL_VIDEOS = {
    "welcome": os.path.join(ADDON_PATH, "local_welcome.mp4"),
    "ads": os.path.join(ADDON_PATH, "local_ads.mp4"),
    "expired": os.path.join(ADDON_PATH, "local_expired.mp4"),
    "offline": os.path.join(ADDON_PATH, "local_offline.mp4")
}

def get_device_id():
    try:
        hostname = socket.gethostname()
        if hostname: 
            return str(hostname).strip().lower()
    except: 
        pass
    return "unknown_user"

def fetch_remote_data():
    try:
        # Cache bypass karne ke liye timestamp query string lagayi hai
        nocache_url = f"{GITHUB_JSON_URL}?t={int(time.time())}"
        req = urllib.request.Request(nocache_url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=7) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        xbmc.log(f"GE_LOCK_NET_ERROR: {str(e)}", xbmc.LOGERROR)
        return None

def check_user_status(data):
    if not data or "users" not in data: 
        return "offline" # Net nahi hai ya data nahi mila toh offline handle karo
    
    device_id = get_device_id()
    try:
        users_clean = {k.strip().lower(): v.strip().lower() for k, v in data["users"].items()}
        return users_clean.get(device_id, "expired") # Agar list me naam nahi hai toh expired/lock dikhao
    except: 
        return "expired"

def get_video_target(data, category):
    # Pehle check karo agar local video pehle se downloaded hai aur sahi size ki hai
    if os.path.exists(LOCAL_VIDEOS[category]) and os.path.getsize(LOCAL_VIDEOS[category]) > 1000:
        return LOCAL_VIDEOS[category]
    # Agar local nahi hai, toh JSON se live stream link uthao
    try:
        if data and "videos" in data and category in data["videos"]:
            links = data["videos"][category]
            if links: 
                return random.choice(links)
    except: 
        pass
    return ""

def background_download_engine(data):
    """ BG Engine: Chupchaap links ko background me download karega bina screen hile """
    if not data or "videos" not in data: 
        return
    headers = {'User-Agent': 'Mozilla/5.0'}
    for category, local_path in LOCAL_VIDEOS.items():
        try:
            links = data["videos"].get(category, [])
            if not links: 
                continue
            url = links[0]
            if os.path.exists(local_path) and os.path.getsize(local_path) > 1000: 
                continue
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                with open(local_path, 'wb') as f: 
                    f.write(response.read())
            xbmc.log(f"GE_LOCK_DOWNLOADED: {category} video saved locally.", xbmc.LOGINFO)
        except: 
            pass

def lock_navigation_loop():
    """ Lock System: Fullscreen player ko track karega aur back key block rakhega """
    monitor = xbmc.Monitor()
    while not monitor.waitForAbort(2):
        data = fetch_remote_data()
        status = check_user_status(data)
        
        if status == "active":
            xbmc.Player().stop()
            xbmc.executebuiltin("ActivateWindow(home)")
            break 
            
        if not xbmc.Player().isPlaying():
            category = "offline" if status == "offline" else "expired"
            play_target = get_video_target(data, category)
            if play_target:
                xbmc.Player().play(play_target)
                xbmc.executebuiltin("ActivateWindow(fullscreenvideo)")
                
        if not xbmc.getCondVisibility("Window.IsVisible(fullscreenvideo)"):
            xbmc.executebuiltin("ActivateWindow(fullscreenvideo)")

def run_main_workflow():
    data = fetch_remote_data()
    status = check_user_status(data)
    device_id = get_device_id()
    
    # Informative overlay for Admin tracking
    xbmc.executebuiltin(f'Notification(GE-Services, Device ID: {device_id} Connected, 5000)')
    
    if status != "offline":
        # Download system ko alag thread me bhejo taaki loop freeze na ho
        threading.Thread(target=background_download_engine, args=(data,)).start()
        
    if status != "active":
        xbmc.executebuiltin(f'Notification(GE-LOCK, STATUS: EXPIRED OR UNREGISTERED, 7000)')
        lock_navigation_loop()
        return

    # --- AGAR ACTIVE HAI TOH MARKETING PLAYBACK SEQUENCE CHALAO ---
    # 1. Welcome Video Sequence (20 Seconds max)
    welcome_target = get_video_target(data, "welcome")
    if welcome_target:
        xbmc.Player().play(welcome_target)
        xbmc.executebuiltin("ActivateWindow(fullscreenvideo)")
        for _ in range(20):
            if xbmc.Monitor().waitForAbort(1): return
            xbmc.executebuiltin("ActivateWindow(fullscreenvideo)")
        xbmc.Player().stop()

    # 2. Ads Video Sequence (60 Seconds max)
    ad_target = get_video_target(data, "ads")
    if ad_target:
        xbmc.Player().play(ad_target)
        xbmc.executebuiltin("ActivateWindow(fullscreenvideo)")
        for _ in range(60):
            if xbmc.Monitor().waitForAbort(1): return
            xbmc.executebuiltin("ActivateWindow(fullscreenvideo)")
        xbmc.Player().stop()

    # Favourites Browser open karke exit karo workflow
    xbmc.executebuiltin("ActivateWindow(FavouritesBrowser)")

# Kodi startup settling time delay
time.sleep(5)
run_main_workflow()