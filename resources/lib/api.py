# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import time
import datetime
import xbmc, xbmcgui, xbmcplugin, sys
from . import requests
from . import gui

try:
    import urllib.parse as urllib
except:
    import urllib

RAN_API_BASE = 'https://middleware.7tv.de'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
bv = xbmc.getInfoLabel('System.BuildVersion')
kodiVersion = int(bv.split('.')[0])


def get_playlist_url(m3u8_url, height=720):
    import re
    try:
        xbmc.log("get_playlist_url {0}".format(m3u8_url))
        response = requests.get(m3u8_url)
        m3u8 = response.read()
        stream_url_prefix = m3u8_url[:m3u8_url.rfind('/') + 1]
        pattern = 'BANDWIDTH=(\d+).*?RESOLUTION=\d+x(\d+).*?\n(.+?)\n'
        videos = re.findall(pattern, m3u8)
        videos = sorted(videos, key=lambda k: (k[1], k[0]))
        del videos[0]
        stream_url_suffix = videos[0][2].replace('\r', '')
        for bandwidth, _height, suffix in videos:
            if int(_height) > height:
                break
            stream_url_suffix = suffix.replace('\r', '')
        stream_url = stream_url_prefix + stream_url_suffix
        if stream_url.startswith('http') and '.m3u8' in stream_url:
            return stream_url
        return m3u8_url
    except:
        return m3u8_url


def list_videos(resource, reliveOnly):
    try:
        json_url = RAN_API_BASE + resource
        xbmc.log("###########{0}".format(json_url))
        response = requests.get(json_url, headers={'Accept-Encoding': 'gzip'})
        videos = response.json()['contents']
    except:
        return gui.end_listing()
    try:
        is_livestream = videos[0]['type'] == 'livestream'
    except (KeyError, IndexError):
        is_livestream = False
    if is_livestream:
        videos = sorted(videos, key=lambda k: k.get('streamdate_start'))
        timestamp_now = time.time()
    for video in videos:
        if is_livestream:
            stream_date_end = video['streamdate_end']
            if stream_date_end >= timestamp_now:
                stream_date_start = video['streamdate_start']
                if stream_date_start <= timestamp_now:
                    duration_in_seconds = stream_date_end - timestamp_now
                    playable = True
                    print("YYY: " + video["resource"])
                    title = '[B][COLOR red]%s[/COLOR][/B]' % video['teaser']['title']
                    year = datetime.datetime.now().year
                else:
                    date = datetime.datetime.fromtimestamp(stream_date_start)
                    year = date.year
                    date = date.strftime('%d.%m.%Y, %H:%M')
                    duration_in_seconds = stream_date_end - stream_date_start
                    playable = False
                    title = video['teaser']['title']
                    title = '[COLOR blue]%s[/COLOR] %s' % (date, video['teaser']['title'])
            else:
                continue
        else:
            duration_in_seconds = video['duration_in_seconds']
            date = datetime.datetime.fromtimestamp(video['published'])
            year = date.year
            date = date.strftime('%d.%m.%Y')
            playable = True
            title = '[COLOR blue]%s[/COLOR] %s' % (date, video['teaser']['title'])
        resource = video['resource']
        thumb = video['teaser']['image']  # .replace('ran_app_1280x720', 'ran_app_512x288')
        desc = video['teaser']['image_alt'] or video['teaser']['title']

        if 'False' in reliveOnly or 'relive' in video['teaser']['title'].lower() or 're-Live' in video['teaser']['title'].lower():
            gui.add_video(title, thumb, {'f': 'play', 'resource': resource},
                      {'Title': video['teaser']['title'], 'Plot': desc, 'Genre': 'Sport', 'Year': year},
                      duration_in_seconds, thumb, is_playable=playable)
    gui.make_info_view_possible()
    gui.info_view()
    gui.end_listing()


def get_number_livestreams():
    xbmc.log("get_number_livestreams")
    try:
        json_url = RAN_API_BASE + '/ran-mega/mobile/v1/livestreams.json'
        response = requests.get(json_url, headers={'Accept-Encoding': 'gzip'})
        videos = response.json()['contents']
        timestamp_now = time.time()
        number_livestreams = 0
        for video in videos:
            stream_date_end = video['streamdate_end']
            if stream_date_end >= timestamp_now:
                stream_date_start = video['streamdate_start']
                if stream_date_start <= timestamp_now:
                    number_livestreams += 1
        return number_livestreams
    except:
        return 0


def _get_videos(video_id, access_token, client_name, client_location, salt, source_id=None):
    from hashlib import sha1
    xbmc.log("-_get_videos----")
    # # Step 1
    if source_id is None:
        json_url = 'https://vas.sim-technik.de/vas/live/v2/videos/{0}?{1}'.format(video_id, urllib.urlencode({
            'access_token': access_token,
            'client_location': client_location,
            'client_name': client_name
        }))
        response = requests.get(json_url, headers={'Accept-Encoding': 'gzip'})
        source_id = response.json().get('sources')[0].get('id')
    # # Step 2
    client_id_1 = '{0}{1}'.format(salt[:2], sha1('{0}{1}{2}{3}{4}{5}' \
                  .format(video_id, salt, access_token, client_location, salt, client_name) \
                  .encode("utf-8")).hexdigest())
    json_url = 'https://vas.sim-technik.de/vas/live/v2/videos/{0}/sources?{1}'.format(video_id, urllib.urlencode({
        'access_token':  access_token,
        'client_location':  client_location,
        'client_name':  client_name,
        'client_id': client_id_1
    }))
    response = requests.get(json_url, headers={'Accept-Encoding': 'gzip'})
    server_id = response.json().get('server_id')
    # # Step 3
    client_id_2 = '{0}{1}'.format(salt[:2], sha1('{0}{1}{2}{3}{4}{5}{6}{7}' \
                  .format(salt, video_id, access_token, server_id, client_location, source_id, salt, client_name) \
                  .encode('utf-8')).hexdigest())
    json_url = 'https://vas.sim-technik.de/vas/live/v2/videos/{0}/sources/url?{1}'.format(video_id, urllib.urlencode({
        'access_token':  access_token,
        'client_location':  client_location,
        'client_name':  client_name,
        'client_id': client_id_2,
        'server_id': server_id,
        'source_ids': source_id
    }))
    response = requests.get(json_url, headers={'Accept-Encoding': 'gzip'})
    videos = response.json().get('sources')
    return sorted(videos, key=lambda k: k.get('bitrate'))


def get_video_url(resource, height):
    from hashlib import sha1
    json_url = '{0}{1}'.format(RAN_API_BASE, resource)
    response = requests.get(json_url, headers={'Accept-Encoding': 'gzip'})
    json_data = response.json()
    if json_data.get('type') == 'livestream':
        url = json_data.get('stream_url')
        salt = '01iegahthei8yok0Eopai6jah5Qui0qu'
        access_token = "ran-app"
        location = 'https://app.ran.de/{0}'.format(url)
        client_token = '{0}{1}'.format(salt[:2], sha1('{0}{1}{2}{3}'.format(url, salt, access_token, location) \
                       .encode("utf-8")).hexdigest())
        newurl = 'https://vas-live-mdp.glomex.com/live/1.0/getprotocols?{0}'.format(urllib.urlencode({
            'access_token': access_token,
            'client_location': location,
            'client_token': client_token,
            'property_name': url
        }))
        xbmc.log(newurl)
        response = requests.get(newurl, headers={'Accept-Encoding': 'gzip', 'user-agent': USER_AGENT})
        res_json = response.json()
        xbmc.log('{0}'.format(res_json))

        servertoken = res_json.get('server_token')

        protokol = 'dash'
        if 'widevine' in res_json.get('protocols').get('dash').get('drm'):
            protokol_drm = 'widevine'
            protokol_param = '{0}:{1}'.format(protokol, protokol_drm)
        else:
            protokol_drm = 'clear'
            protokol_param = protokol
        client_token = '{0}{1}'.format(salt[:2], sha1('{0}{1}{2}{3}{4}{5}'.format(url, salt, access_token, servertoken, location, protokol_param) \
                       .encode('utf-8')).hexdigest())
        url2 = 'https://vas-live-mdp.glomex.com/live/1.0/geturls?{0}'.format(urllib.urlencode({
            'access_token':  access_token,
            'client_location':  location,
            'property_name':  url,
            'protocols': protokol_param,
            'server_token': servertoken,
            'client_token': client_token,
            'secure_delivery': 'true'
        }))
        response = requests.get(url2, headers={'Accept-Encoding': 'gzip', 'user-agent': USER_AGENT})
        jsondata = response.json()
        xbmc.log('{0}'.format(jsondata))
        xbmc.log('###############################')
        data_drm = jsondata.get('urls').get(protokol).get(protokol_drm)
        listitem = xbmcgui.ListItem(path='{0}|{1}'.format(data_drm.get('url'), USER_AGENT))
        listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
        listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        listitem.setProperty('inputstreamaddon' if kodiVersion <= 18 else 'inputstream', 'inputstream.adaptive')
        listitem.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')

        if data_drm.get('drm') and data_drm.get('drm').get('licenseAcquisitionUrl') and data_drm.get('drm').get('token'):
            drm_lic = data_drm.get('drm').get('licenseAcquisitionUrl')
            drm_token = data_drm.get('drm').get('token')
            listitem.setProperty('inputstream.adaptive.license_key', '{0}?token={1}|{2}|R{3}|'.format(drm_lic, drm_token, USER_AGENT, '{SSM}'))
            xbmc.log('lic_key = {0}?token={1}|{2}|R{3}|'.format(drm_lic, drm_token, USER_AGENT, '{SSM}'))

        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
        return None
    else:
        video_id = json_data['video_id']
        """
        access_token = 'r''a''n''-''a''p''p'
        client_location = 'h''t''t''p'':''/''/''a''p''p''.''r''a''n''.''d''e''/''%s' % video_id
        client_name = 'r''a''n''-''5''.''7''.''3'
        salt = '0''1''i''e''g''a''h''t''h''e''i''8''y''o''k''0''E''o''p''a''i''6''j''a''h''5''Q''u''i''0''q''u'
        source_id = 6
        access_token = 'p''r''o''s''i''e''b''e''n'
        client_location = json_data['url']
        client_name = 'k''o''l''i''b''r''i''-''2''.''0''.''1''9''-''s''p''l''e''c''4'
        salt = '0''1''!''8''d''8''F''_'')''r''9'']''4''s''[''q''e''u''X''f''P''%'
        source_id = 4
        """
        access_token = 'h''b''b''t''v'
        client_location = json_data['url']
        salt = '0''1''r''e''e''6''e''L''e''i''w''i''u''m''i''e''7''i''e''V''8''p''a''h''g''e''i''T''u''i''3''B'
        # http://hbbtv.prosieben.de/common/js/videocenter.js
        # __PATTERN = 'salt\s*:\s*"01(.+?)"'
        source_id = 4
        videos = _get_videos(video_id, access_token, access_token, client_location, salt, source_id)
        # height = (234, 270, 396, 480, 540, 720)
        url = videos[-1]['url']
        if height < 396:
            import re
            if height == 270:
                return re.sub(r'(.+?)(tp\d+.mp4)(.+)', r'\1tp%02d.mp4\3' % 4, url)
            # height == 234
            return re.sub(r'(.+?)(tp\d+.mp4)(.+)', r'\1tp%02d.mp4\3' % 3, url)
        if height == 396:
            return videos[0]['url']
        # else height in (480, 540, 720)
        # check available qualities:
        if 'tp12.mp4' in url:
            # available video ids are: (12,11,10,09,06) --> (720,720,540,540,360)
            if height == 480:
                return videos[0]['url']  # 360
            if height == 540:
                return videos[2]['url']  # 540
            # else: return highest --> 720
        # else: available video ids are: (08,07,06) --> (432,432,360)
        # highest is 432 and we want 480 or 540 or 720
        # return highest
        return url
