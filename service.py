import xbmc, xbmcaddon, urllib.request, json

addon = xbmcaddon.Addon()
JSON_URL = "https://raw.githubusercontent.com/rohanjaiawal1-code/ge-services-by-g-home/main/users.json"

def play_video(url):
    # यह तरीका सबसे सेफ है, यह एरर नहीं देगा
    xbmc.executebuiltin(f'PlayMedia({url})')

def run_automation():
    phone = addon.getSetting("user_phone")
    username = addon.getSetting("user_name")
    setup_done = addon.getSetting("setup_done")

    try:
        with urllib.request.urlopen(JSON_URL, timeout=10) as url:
            data = json.loads(url.read().decode())
    except:
        # इंटरनेट नहीं है तो Offline वीडियो
        play_video(data['videos']['offline'][0])
        return

    # 1. SETUP (1 Time)
    if setup_done != "true":
        play_video(data['videos']['setup'][0])
        addon.setSetting("setup_done", "true")
        return

    # 2. ACTIVE USER
    if phone in data['users'] and data['users'][phone].get('username') == username:
        if data['users'][phone].get('status') == 'active':
            # Active है तो Welcome -> Ad -> Trial
            play_video(data['videos']['welcome'][0])
            xbmc.sleep(5000) # 5 सेकंड रुकें
            play_video(data['videos']['ads'][0])
            xbmc.sleep(5000)
            play_video(data['videos']['trial'][0])
        else:
            # Expired है तो Expired लूप
            play_video(data['videos']['expired'][0])
    else:
        # गलत लॉगिन है
        xbmc.executebuiltin('Notification(GE Error, Login Failed, 5000)')

# Kodi स्टार्ट होते ही चलाएं
xbmc.sleep(5000)
run_automation()
