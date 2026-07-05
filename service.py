import xbmc
import xbmcaddon
import time
import os
import urllib.request
import random
import json
import socket

# ==========================================
# 🔴 CONFIGURATION: APNA GITHUB RAW JSON URL YAHAN DALEIN
# ==========================================
GITHUB_JSON_URL = "https://raw.githubusercontent.com/rohanjaiawal1-code/ge-services-by-g-home/main/users.json"

# Addon Paths Setup
ADDON = xbmcaddon.Addon()
ADDON_PATH = xbmc.translatePath(ADDON.getAddonInfo('path'))

DIR_WELCOME = os.path.join(ADDON_PATH, "welcome_videos")
DIR_OFFLINE = os.path.join(ADDON_PATH, "offline_videos")
DIR_EXPIRED = os.path.join(ADDON_PATH, "expired_videos")
DIR_ADS     = os.path.join(ADDON_PATH, "ads_videos")

def get_device_id():
    """ 
    Har device ka ek unique name (Hostname) nikalta hai, 
    taaki aapko har user ke liye code ke andar naam na badalna pade.
    """
    try:
        hostname = socket.gethostname()
        if hostname:
            return str(hostname).strip().lower()
    except:
        pass
    return "unknown_user"

def get_random_video(folder_path):
    """ Folder se koi bhi ek random .mp4 video uthane ke liye """
    if os.path.exists(folder_path):
        videos = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp4')]
        if videos:
            return os.path.join(folder_path, random.choice(videos))
    return ""

def check_user_status():
    """ GitHub se JSON download karke current device ka status check karta hai """
    device_id = get_device_id()
    try:
        req = urllib.request.Request(
            GITHUB_JSON_URL, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        response = urllib.request.urlopen(req, timeout=6)
        data = json.loads(response.read().decode('utf-8'))
        
        # JSON keys ko lowercase karke match karenge taaki mistake na ho
        data_clean = {k.strip().lower(): v.strip().lower() for k, v in data.items()}
        
        if device_id in data_clean:
            return data_clean[device_id]
        else:
            # Agar koi naya user h jiska naam aapne GitHub pe nahi dala, toh wo default lock rahega
            return "expired"
    except Exception as e:
        pass
    return "offline" # Connection fail hone par automatic offline block

def lock_navigation_loop():
    """ Strict Lock System: User ko settings/home me nahi jaane dega """
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
    # 1. Boot up validation check
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

# Kodi skin load hone ka safe time delay
time.sleep(4)
run_main_workflow()
