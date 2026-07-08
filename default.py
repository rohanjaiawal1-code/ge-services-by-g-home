import xbmc, xbmcgui, xbmcplugin, sys, urllib.request, json

addon_handle = int(sys.argv[1])
JSON_URL = "https://raw.githubusercontent.com/rohanjaiawal1-code/ge-services-by-g-home/main/users.json"

def get_videos():
    try:
        with urllib.request.urlopen(JSON_URL, timeout=10) as url:
            data = json.loads(url.read().decode())
            return data['videos'].get('welcome', [])
    except:
        return []

def main():
    videos = get_videos()
    for vid_url in videos:
        li = xbmcgui.ListItem(label='Play Premium Video')
        xbmcplugin.addDirectoryItem(addon_handle, f'plugin://plugin.video.ge/?action=play&url={vid_url}', li, False)
    xbmcplugin.endOfDirectory(addon_handle)

params = dict(arg.split('=') for arg in sys.argv[2][1:].split('&') if '=' in arg)

if params.get('action') == 'play':
    xbmc.executebuiltin(f'PlayMedia({params["url"]})')
else:
    main()
