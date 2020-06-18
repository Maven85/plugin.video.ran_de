# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys
from . import api
from . import gui

try:
    import urllib.parse as urllib
except:
    import urllib


def play(**kwargs):
    import xbmcaddon
    addon = xbmcaddon.Addon(id='plugin.video.ran_de')
    height = (234, 270, 396, 480, 540, 720)[int(addon.getSetting('video.quality'))]
    resource = urllib.unquote_plus(kwargs['resource'])
    video = api.get_video_url(resource, height)
    if video:
        gui.play(video)


def videos(**kwargs):
    resource = urllib.unquote_plus(kwargs['resource'])
    reliveOnly = kwargs['reliveOnly']
    api.list_videos(resource, reliveOnly)


def index():
    from . import thumbnails
    live_caption = api.get_number_livestreams()
    if live_caption:
        live_caption = '[B]Live (%s)[/B]' % live_caption
    else:
        live_caption = 'Live (%s)' % live_caption
    gui.add_folder(live_caption, thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/livestreams.json', 'reliveOnly': False}, 'aktuelle Live Streams')
    gui.add_folder('Neueste Videos', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos.json', 'reliveOnly': False}, 'Liste der neuesten Videos - über alle Kategorien')
    gui.add_folder('Neueste Videos - [COLOR blue] Re-Live only [/COLOR]', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos.json', 'reliveOnly': True}, 'Liste der neuesten Re-Lives - über alle Kategorien')
    gui.add_folder('Fussball', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos/fussball.json', 'reliveOnly': False}, 'Liste der neuesten Fussball-Videos')
    gui.add_folder('US-Sports', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos/us-sport.json', 'reliveOnly': False}, 'Liste der neuesten US-Sport-Videos (NBA, NFL, NHL)')
    gui.add_folder('US-Sports: [COLOR blue] Re-Live only [/COLOR]', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos/us-sport.json', 'reliveOnly': True}, 'Liste der neuesten Re-Live-Videos des US-Sports auf ran.de (NBA, NFL, NHL)')
    gui.add_folder('Tennis', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos/tennis.json', 'reliveOnly': False}, 'Liste der neuesten Tennis-Videos')
    gui.add_folder('Handball', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos/handball.json', 'reliveOnly': False}, 'Liste der neuesten Handball-Videos')
    gui.add_folder('Boxen', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos/boxen.json', 'reliveOnly': False}, 'Liste der neuesten Box-Videos')
    gui.add_folder('Darts', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos/darts.json', 'reliveOnly': False}, 'Liste der neuesten Darts-Videos')
    gui.add_folder('eSports', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos/esport.json', 'reliveOnly': False}, 'Liste der neuesten eSports-Videos')
    gui.add_folder('DTM', thumbnails.THUMB_MAIN, {'f': 'videos', 'resource': '/ran-mega/mobile/v1/videos/dtm.json', 'reliveOnly': False}, 'Liste der neuesten Videos der Deutschen Tourenwagen Meisterschaft (DTM)')
    gui.end_listing()


d = dict(p.split('=') for p in sys.argv[2][1:].split('&') if len(p.split('=')) == 2)
f = d.pop('f', 'index')
exec('{0}(**d)'.format(f))
