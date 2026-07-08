import xbmc, xbmcaddon, urllib.request, json, os, xbmcvfs, random

addon = xbmcaddon.Addon()
media_path = xbmcvfs.translatePath("special://profile/addon_data/plugin.video.ge/media/")
offline_img = os.path.join(media_path, 'offline.jpg')

def show_static_image():
    if xbmcvfs.exists(offline_img):
        xbmc.executebuiltin(f'ShowPicture("{offline_img}")')

def monitor():
    xbmc.log("GE Agent: Monitoring Started (Fixed Loop)", level=xbmc.LOGINFO)
    monitor = xbmc.Monitor()
    player = xbmc.Player()
    
    # last_status se loop control hoga
    last_status = "none"

    while not monitor.abortRequested():
        # 1. Fetch JSON
        data = None
        try:
            req = urllib.request.Request("https://raw.githubusercontent.com/rohanjaiawal1-code/ge-services-by-g-home/main/users.json", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as url:
                data = json.loads(url.read().decode())
        except:
            current_status = "offline"
        
        # 2. Status Logic
        if data:
            phone = addon.getSetting("user_phone")
            username = addon.getSetting("user_name")
            if phone in data['users'] and data['users'][phone].get('username') == username:
                current_status = data['users'][phone].get('status', 'error').strip().lower()
            else:
                current_status = "error"
        else:
            current_status = "offline"

        # 3. Action Logic (Strictly triggered only on status change)
        if current_status != last_status:
            xbmc.log(f"GE Agent Switching: {last_status} -> {current_status}", level=xbmc.LOGINFO)
            
            # Stop any existing play before changing
            player.stop()
            
            if current_status == 'active':
                # Active Sequence: One Time Play
                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                playlist.clear()
                
                # Add Videos: Welcome -> Ads -> Trial
                playlist.add(data['videos']['welcome'][0])
                ads_list = data['videos'].get('ads', [])
                if ads_list:
                    selected_ads = random.sample(ads_list, min(len(ads_list), 2))
                    for ad_url in selected_ads:
                        playlist.add(ad_url)
                playlist.add(data['videos']['trial'][0])
                
                # Play (No Repeat)
                player.play(playlist)
                last_status = 'active'
            
            elif current_status in ['expired', 'error']:
                # Loop mode for Expired/Error
                xbmc.executebuiltin(f'PlayMedia("{data["videos"][current_status][0]}")')
                xbmc.executebuiltin("PlayerControl(RepeatAll)")
                last_status = current_status
            
            else: # Offline
                show_static_image()
                last_status = current_status
        
        # 4. Idle Check (Sequence finish hone ke baad status change na karein)
        if monitor.waitForAbort(10):
            break

monitor()
