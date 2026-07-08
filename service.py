import xbmc, xbmcaddon, urllib.request, json

addon = xbmcaddon.Addon()
JSON_URL = "https://raw.githubusercontent.com/rohanjaiawal1-code/ge-services-by-g-home/main/users.json"

def check_login():
    phone = addon.getSetting("user_phone")
    username = addon.getSetting("user_name")
    
    if not phone or not username:
        return

    try:
        with urllib.request.urlopen(JSON_URL, timeout=10) as url:
            data = json.loads(url.read().decode())
        
        # Check if phone and username match
        if phone in data['users'] and data['users'][phone].get('username') == username:
            xbmc.log("GE Auth: Success", level=xbmc.LOGNOTICE)
        else:
            xbmc.executebuiltin('Notification(GE Error, Access Denied!, 5000)')
    except Exception as e:
        xbmc.log(f"GE Auth Error: {e}", level=xbmc.LOGERROR)

check_login()
