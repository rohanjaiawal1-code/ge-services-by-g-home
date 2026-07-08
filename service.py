import xbmc, xbmcaddon, urllib.request, json

addon = xbmcaddon.Addon()
JSON_URL = "https://raw.githubusercontent.com/rohanjaiawal1-code/ge-services-by-g-home/main/users.json"

def play_playlist(video_list):
    playlist = xbmc.Playlist(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    for url in video_list:
        playlist.add(url)
    xbmc.Player().play(playlist)

def run_automation():
    phone = addon.getSetting("user_phone")
    username = addon.getSetting("user_name")
    setup_done = addon.getSetting("setup_done")

    # JSON डेटा लोड करें
    try:
        with urllib.request.urlopen(JSON_URL, timeout=10) as url:
            data = json.loads(url.read().decode())
    except:
        # --- OFFLINE LOGIC ---
        # स्वागत -> Ad -> Offline -> Ad -> Offline -> Ad -> Ad -> Ad -> Offline (Loop)
        offline_seq = [
            data['videos']['welcome'][0], data['videos']['ads'][0], 
            data['videos']['offline'][0], data['videos']['ads'][1],
            data['videos']['offline'][1], data['videos']['ads'][0],
            data['videos']['ads'][1], data['videos']['ads'][0],
            data['videos']['offline'][1]
        ]
        play_playlist(offline_seq)
        return

    # --- SETUP LOGIC (First Time) ---
    if setup_done != "true":
        play_playlist(data['videos']['setup'])
        addon.setSetting("setup_done", "true")
        return

    # --- ACTIVE USER LOGIC ---
    if phone in data['users'] and data['users'][phone].get('username') == username:
        if data['users'][phone].get('status') == 'active':
            # Welcome -> Ad -> Trial -> Ad -> Home
            active_seq = [data['videos']['welcome'][0], data['videos']['ads'][0], data['videos']['trial'][0], data['videos']['ads'][1]]
            play_playlist(active_seq)
            xbmc.executebuiltin('ActivateWindow(Home)') # Navigation open
        else:
            # --- EXPIRED LOGIC ---
            # Ad -> Expired -> Expired -> Expired -> Ad (Loop)
            expired_seq = [data['videos']['ads'][0], data['videos']['expired'][0], data['videos']['expired'][1], data['videos']['expired'][2], data['videos']['ads'][1]]
            play_playlist(expired_seq)
    else:
        # Login Fail
        xbmc.executebuiltin('Notification(GE, Login Failed, 5000)')

xbmc.sleep(3000)
run_automation()
