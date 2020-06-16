import sys
import xbmc
import xbmcgui
import xbmcplugin

try:
    import urllib.parse as urllib
except:
    import urllib

HOST_AND_PATH = sys.argv[0]
ADDON_HANDLE = int(sys.argv[1])


def make_info_view_possible():
    xbmcplugin.setContent(ADDON_HANDLE, 'movies')


def add_folder(title, thumb, url_params, description, context_menu_items=None):
    item = xbmcgui.ListItem(title)
    item.setInfo('video', {'plot': description})
    item.setArt({'thumb': thumb})
    if context_menu_items is not None:
        item.addContextMenuItems(context_menu_items)
    make_info_view_possible()
    return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url='%s?%s' % (HOST_AND_PATH, urllib.urlencode(url_params)),
                                       listitem=item, isFolder=True)


def add_video(title,
              thumb=None,
              url_params=None,
              video_info_labels=None,
              duration_in_seconds=None,
              fanart=None,
              video_url=None,
              icon=None,
              is_playable=True,
              context_menu_items=None,
              subtitle_list=None):
    """
    Callback function to pass directory contents back to XBMC as a list.

    :param title: primary title of video
    :param thumb: path to thumbnail
    :param url_params: dictionary of url parameters
    :param video_info_labels: {
            genre: string (Comedy)
            year: integer (2009)
            episode: integer (4) ...
        }
    :param video_stream_info: {
            codec         : string (h264)
            aspect        : float (1.78)
            width         : integer (1280)
            height        : integer (720)
            duration      : integer (seconds)
        }
    :param fanart: path to fanart image
    :param video_url: direct url to video
    :param icon: path to icon
    :param is_playable: boolean
    :param context_menu_items: [('title', 'xbmc.function')]
    :param subtitle_list: ['url to srt']
    :return: boolean for successful completion
    """
    item = xbmcgui.ListItem(title)
    item.setInfo(type='video', infoLabels=video_info_labels)
    item.setArt({'icon': icon, 'thumb': thumb})
    item.setProperty('IsPlayable', str(is_playable).lower())
    item.setProperty('fanart_image', fanart)
    if duration_in_seconds is not None:
        item.addStreamInfo('video', {'duration': duration_in_seconds})
    if context_menu_items is not None:
        item.addContextMenuItems(context_menu_items)
    if subtitle_list is not None:
        try:
            item.setSubtitles(subtitle_list)
        except AttributeError:
            pass  # requires xbmc version >= 14 (Helix)
    url = video_url or '%s?%s' % (HOST_AND_PATH, urllib.urlencode(url_params))
    return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=item)


def end_listing():
    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def play(url):
    xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, xbmcgui.ListItem(path=url))


def player_play(title, thumb, stream_url):
    title = urllib.unquote_plus(title)
    thumb = urllib.unquote_plus(thumb)
    item = xbmcgui.ListItem(title)
    item.setArt({'thumb': thumb})
    xbmc.Player().play(stream_url, item)


def get_search_input(heading, default_text=''):
    keyboard = xbmc.Keyboard(default_text, heading)
    keyboard.doModal()
    if keyboard.isConfirmed():
        return keyboard.getText()


def info_view():
    xbmc.executebuiltin('Container.SetViewMode(504)')