import xbmc
import xbmcaddon
import time
import os
import urllib.request
import random
import json
import socket

# ==========================================
# 🔴 CONFIGURATION: APNA GITHUB RAW JSON URL
# ==========================================
GITHUB_JSON_URL = "https://raw.githubusercontent.com/rohanjaiawal1-code/ge-services-by-g-home/refs/heads/main/users.json"

# Addon Paths Setup
ADDON = xbmcaddon.Addon()
ADDON_PATH = xbmc.translatePath(ADDON.getAddonInfo('path'))

DIR_WELCOME = os.path.join(ADDON_PATH, "welcome_videos")
DIR_OFFLINE = os.path.join(ADDON_PATH, "offline_videos")
DIR_EXPIRED = os.path.join(ADDON_PATH, "expired_videos")
DIR_ADS = os.path.join(ADDON_PATH, "ads_videos")

def get_device_id():
    """ Device ka unique Hostname nikalta hai """
    try:
        hostname = socket.gethostname()
        if hostname:
            return str(hostname).strip().lower()
    except:
        pass
    return "unknown_user"

def get_random_video(folder_path):
    """ Folder se random .mp4 file select karne ke liye """
    if os.path.exists(folder_path):
        videos = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp4')]
        if videos:
            return os.path.join(folder_path, random.choice(videos))
    return ""

def check_user_status():
    """ GitHub se JSON download karta hai (Bina cache issue ke) """
    device_id = get_device_id()
    try:
        # Cache se bachne ke liye URL ke end me timestamp laga rahe hain
        nocache_url = f"{GITHUB_JSON_URL}?t={int(time.time())}"
        
        req = urllib.request.Request(
            nocache_url, 
            headers={
                'User-Agent': 'Mozilla/5.0',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        )
        response = urllib.request.urlopen(req, timeout=6)
        data = json.loads(response.read().decode('utf-8'))
        
        # Keys aur values ko clean aur lowercase karein
        data_clean = {k.strip().lower(): v.strip().lower() for k, v in data.items()}
        
        if device_id in data_clean:
            return data_clean[device_id]
        else:
            return "expired" # Agar new user list me nahi hai toh auto-lock
    except Exception as e:
        pass
    return "offline" # Internet band hone par auto offline block

def lock_navigation_loop():
    """ Strict Lock System: User ko settings/home par nahi jaane dega """
    while not xbmc.Monitor().waitForAbort(1):
        status = check_user_status()
        
        if status == "active":
            xbmc.Player().stop()
            break # Lock se bahar, Kodi open!
            
        if not xbmc.Player().isPlaying():
            target_folder = DIR_OFFLINE if status == "offline" else DIR_EXPIRED
            video_path = get_random_video(target_folder)
            if video_path:
                xbmc.Player().play(video_path)
                xbmc.executebuiltin("ActivateWindow(fullscreenvideo)")
                
        if not xbmc.getCondVisibility("Window.IsVisible(fullscreenvideo)"):
            xbmc.executebuiltin("ActivateWindow(fullscreenvideo)")
            
        time.sleep(1)

def run_main_workflow():
    # 1. Boot up status validation check
    status = check_user_status()
    if status != "active":
        lock_navigation_loop()
        
    # 2. Welcome Video Section (Strict 20 Seconds)
    welcome_vid = get_random_video(DIR_WELCOME)
    if welcome_vid:
        xbmc.Player().play(welcome_vid)
        xbmc.executebuiltin("ActivateWindow(fullscreenvideo)")
        for _ in range(20):
            if xbmc.Monitor().waitForAbort(1): return
            xbmc.executebuiltin("ActivateWindow(fullscreenvideo)")
            time.sleep(1)
        xbmc.Player().stop()

    # 3. Ads Video Section (Strict 60 Seconds)
    ads_vid = get_random_video(DIR_ADS)
    if ads_vid:
        xbmc.Player().play(ads_vid)
        xbmc.executebuiltin("ActivateWindow(fullscreenvideo)")
        for _ in range(60):
            if xbmc.Monitor().waitForAbort(1): return
            xbmc.executebuiltin("ActivateWindow(fullscreenvideo)")
            time.sleep(1)
        xbmc.Player().stop()

    # 4. Redirect to Favourites Window
    xbmc.executebuiltin("ActivateWindow(FavouritesBrowser)")

# Kodi skin completely load hone ka delay
time.sleep(4)
run_main_workflow()
