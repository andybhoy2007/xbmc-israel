# -*- coding: utf-8 -*-

"""
    Plugin for streaming video content from www.sdarot.tv
"""
import urllib, urllib2, re, os, sys 
import xbmcaddon, xbmc, xbmcplugin, xbmcgui
import HTMLParser
import json
import cookielib

ADDON = xbmcaddon.Addon(id='plugin.video.sdarot.tv')
##General vars        
__plugin__ = "Sdarot.TV Video"
__author__ = "Cubicle"

__image_path__ = ''
__settings__ = xbmcaddon.Addon(id='plugin.video.sdarot.tv')
__language__ = __settings__.getLocalizedString
__PLUGIN_PATH__ = __settings__.getAddonInfo('path')
LIB_PATH = xbmc.translatePath( os.path.join( __PLUGIN_PATH__, 'resources', 'lib' ) )
sys.path.append (LIB_PATH)

from sdarotcommon import *

path = xbmc.translatePath(__settings__.getAddonInfo("profile"))
cookie_path = os.path.join(path, 'sdarot-cookiejar.txt')
print("Loading cookies from :" + repr(cookie_path))
cookiejar = cookielib.LWPCookieJar(cookie_path)

if os.path.exists(cookie_path):
    try:
        cookiejar.load()
    except:
        pass
  
cookie_handler = urllib2.HTTPCookieProcessor(cookiejar)
opener = urllib2.build_opener(cookie_handler)
urllib2.install_opener(opener)
print "built opener:" + str(opener)

#net=Net()


def LOGIN():
    loginurl = 'http://www.sdarot.tv/login'
    username    =ADDON.getSetting('user')
    password =ADDON.getSetting('pass')
    
    print "Trying to login to sdarot tv site"
    page = getData(url=loginurl,timeout=0,postData="username=change&password=change&submit_login=התחבר");
   
    print cookiejar
    
   



def MAIN_MENU():

    site='http://www.sdarot.tv'   
    LOGIN()
   
    addDir("הכל א-ת","all-heb",2,'');
    addDir("הכל a-z","all-eng",2,'');

def message(title, message):
    dialog = xbmcgui.Dialog()
    dialog.ok(title , message)
    
def INDEX_AZ(url):
    page = getData('http://www.sdarot.tv/series');
    matches = re.compile('<a href="/watch/(\d+)-(.*?)">.*?</noscript>.*?<div>(.*?)</div>').findall(page)
    sr_arr = []
    idx = 0
    i=0
    if url == "all-eng":
      idx = 1
    for match in matches:
      series_id = match[0]
      link_name = match[1]
      name = HTMLParser.HTMLParser().unescape(match[2])
      m_arr = name.split(" / ")
      if (len(m_arr)>1) and (idx==1):
        sr_arr.append(( series_id, link_name, m_arr[1].strip() ))
      else:
        sr_arr.append(( series_id, link_name, m_arr[0].strip() ))
      i=i+1
    sr_sorted = sorted(sr_arr,key=lambda sr_arr: sr_arr[2])
      
    for key in sr_sorted:
      series_link="http://www.sdarot.tv/watch/"+str(key[0])+"/"+key[1]
      image_link="http://www.sdarot.tv/media/series/"+str(key[0])+".jpg"      
      addDir(key[2],series_link,"3&image="+urllib.quote(image_link)+"&series_id="+str(key[0])+"&series_name="+urllib.quote(key[1]),image_link)
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
      

def sdarot_series(url):
    series_id=urllib.unquote_plus(params["series_id"])
    series_name=urllib.unquote_plus(params["series_name"])
    image_link=urllib.unquote_plus(params["image"])
    
    
    #opener.addheaders = [('Referer',url)]
    opener.open('http://www.sdarot.tv/landing/'+series_id).read()
    print "sdarot_series: Fetching URL:"+url  
    try:
        page = opener.open(url).read()
        print cookiejar
    except urllib2.URLError, e:
        print 'sdarot_season: got http error ' +str(e.code) + ' fetching ' + url + "\n"
        raise e
    #page = getData(url);
    #print "Page Follows:\n"
    #print page
                 #<ul id="season">
    block_regexp='id="season">(.*?)</ul>'
    seasons_list = re.compile(block_regexp,re.I+re.M+re.U+re.S).findall(page)[0]
    regexp='>(\d+)</a'
    matches = re.compile(regexp).findall(seasons_list)
    for season in matches:
        addDir("עונה "+ str(season),url,"5&image="+urllib.quote(image_link)+"&season_id="+str(season)+"&series_id="+str(series_id)+"&series_name="+urllib.quote(series_id),image_link)
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
      
def sdarot_season(url):
    series_id=urllib.unquote_plus(params["series_id"])
    series_name=urllib.unquote_plus(params["series_name"])
    season_id=urllib.unquote_plus(params["season_id"])
    image_link=urllib.unquote_plus(params["image"])
    page = getData(url="http://www.sdarot.tv/ajax/watch",timeout=0,postData="eplist=true&serie="+series_id+"&season="+season_id);
    print  ("episodes  are:" +page)
    episodes=page.split(",")
    for episode in episodes:
      if ( episode.find("-") != -1 ):
        episode=episode.replace("-0","")
      addVideoLink("פרק "+str(episode), url, "4&episode_id="+str(episode)+"&image="+urllib.quote(image_link)+"&season_id="+str(season_id)+"&series_id="+str(series_id)+"&series_name="+urllib.quote(series_id),image_link, '')      
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')

def sdarot_movie(url):
    series_id=urllib.unquote_plus(params["series_id"])
    series_name=urllib.unquote_plus(params["series_name"])
    season_id=urllib.unquote_plus(params["season_id"])
    image_link=urllib.unquote_plus(params["image"])
    episode_id=urllib.unquote_plus(params["episode_id"])
    title = series_name + "עונה " + season_id + " פרק" + episode_id
    page = getData(url="http://www.sdarot.tv/ajax/watch",timeout=0,postData="watch=true&serie="+series_id+"&season="+season_id+"&episode="+episode_id);
    
    print cookiejar
    try:
       
        #the website has a problem that the json is surrounded with exception - therefore we extract it from the text.
        jsonStart=page.find("{")
        page=page[jsonStart:]
        print "Stripped JSON:" + page
    except Exception as e:
        print "Unexpected error:"
        print e
        raise
    
    
    
    prms=json.loads(page)
    print "Token: "+str(prms["token"])+"\n"
    print "Time: "+str(prms["time"])+"\n"
    print "VID: "+str(prms["VID"])+"\n"
    token = str(prms["token"])
    vid_time = str(prms["time"])
    VID = str(prms["VID"])
    
    #player_url='http://www.sdarot.tv/templates/frontend/green_w/player.swf?file='+url+'&provider=http&fullscreen=true'
    player_url='http://www.sdarot.tv/templates/frontend/blue_html5/player/jwplayer.flash.swf'
    
    flv_url = "http://media1.sdarot.tv/media/videos/sd/"+VID+'.mp4?token='+token+'&time='+vid_time+'|User-Agent='+urllib.quote('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20100101 Firefox/15.0.1')+'&Referer='+urllib.quote(player_url)    
    liz = xbmcgui.ListItem(title, path=flv_url, iconImage=params["image"], thumbnailImage=params["image"])
    liz.setInfo(type="Video", infoLabels={ "Title": title })    
    liz.setProperty('IsPlayable', 'true')
    xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=liz)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=flv_url, listitem=liz, isFolder=False)
    
params = getParams(sys.argv[2])
url=None
name=None
mode=None
module=None
page=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:
        module=urllib.unquote_plus(params["module"])
except:
        pass
try:
        page=urllib.unquote_plus(params["page"])
except:
        pass
    
if mode==None or url==None or len(url)<1:
    MAIN_MENU()

elif mode==2:
    INDEX_AZ(url)

elif mode==3:
    sdarot_series(url)

elif mode==4:
    sdarot_movie(url)

elif mode==5:
    sdarot_season(url)

xbmcplugin.setPluginFanart(int(sys.argv[1]),xbmc.translatePath( os.path.join( __PLUGIN_PATH__,"fanart.jpg") ))
xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=0)

