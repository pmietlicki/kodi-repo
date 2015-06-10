#############################################################################
#
# CPlayer:
# Video and audio player class which extends the funcionality of the default
# xbmc player class.
#############################################################################

from string import *
import sys, os.path
import urllib
import urllib2
import re, random, string
import xbmc, xbmcgui
import re, os, time, datetime, traceback
import shutil
import zipfile
from libs2 import *
from settings import *
from CURLLoader import *
from CFileLoader import *
import iptools
from PYLoader import *

try: Emulating = xbmcgui.Emulating
except: Emulating = False

#####################################################################
# Description: My player class, overrides the XBMC Player
######################################################################
class CPlayer(xbmc.Player):
    def  __init__(self, core, function):
        self.function=function
        self.core=core
        self.stopped=False
        self.pls = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
#        self.pls.clear()

        xbmc.Player.__init__(self)

    def onPlayBackStarted(self):
        self.function(1)
    
    def onPlayBackEnded(self):
        self.stopped=True
        self.function(2)
        
    def onPlayBackStopped(self):
        self.stopped=True
        self.function(3)

    ######################################################################
    # Description: Play the video, audio in the playlist
    # Parameters : playlist = the input playlist containing all items
    #              first = index of first item
    #              lasts = index of last item
    # Return     : 0 if succesful, -1 if no audio, video files in list
    ######################################################################    
    def play(self, playlist, first, last):
        self.pls.clear()

        if first == last:
            URL = playlist.list[first].URL
            xbmc.Player.play(self, URL)
        else:
        
            index = first
            urlopener = CURLLoader()
            self.stopped=False
            count=0
            while (index <= last) and (self.stopped == False):        
                if (count>0) and not (xbmc.Player().isPlaying()):
                    self.stopped=True
                type = playlist.list[index].type
                if type == 'video' or type == 'audio' or type == 'ps3plus':
                    URL = playlist.list[index].URL

                    result = urlopener.urlopen(URL, playlist.list[index])
                    if result["code"] == 0:
                        loc_url = urlopener.loc_url

                        name = playlist.list[index].name
                        
                        #if (xbmc.getInfoLabel("System.BuildVersion")[:1] == '9') or \
                        #   (xbmc.getInfoLabel("System.BuildVersion")[:2] == '10'):                        
                        listitem = xbmcgui.ListItem(name)
                        listitem.setInfo('video', {'Title': name})
                        self.pls.add(url=loc_url, listitem=listitem)                      
                        #else:
                        #    self.pls.add(loc_url, name)
                        
                        if self.pls.size() == 1:
                            #start playing, continue loading                      
                            xbmc.Player.play(self, self.pls)
                index = index + 1
                count = count + 1
            
            if self.pls.size() == 0:
                #no valid items found
                return {"code":1,"data":"no valid items found"}
        
        if not (xbmc.Player().isPlaying()):
            return {"code":1,"data":"no valid items found"} 

        return {"code":0}

    ######################################################################
    ######################################################################            
    def play_URL(self, URL, mediaitem=0):
        #URL=mediaitem.URL
        #check if the URL is empty or not
        if URL == '':
            return {"code":1, "data":"URL is empty"}
                                              
        urlopener = CURLLoader()
        result = urlopener.urlopen(URL, mediaitem)
        addon = xbmcaddon.Addon(id='script.apiportal')
        #Pb de latences sur ce code voir si indispensable
#        if (result["code"] != 0) and (addon.getSetting("pyload_enabled")=="true"):
#            try:
#                downloader = PYLoader()
#                session = downloader.login()
#                downloadable = downloader.send(session, "checkURLs", urls=[URL])
#                if not "BasePlugin" in downloadable:
#                    result = downloader.send(session, "addPackage", name=mediaitem.name.strip(), links=[URL])
#                    fileid = downloader.send(session, "getPackageData", pid=result)
#                    fileid = downloader.parse_json(fileid)
#                    folder = fileid["folder"]
#                    download_folder = downloader.send(session, "getConfigValue", category="general", option="download_folder")
#                    download_folder = download_folder.replace('"','')
#                    time.sleep(10)
#                    captcha = downloader.send(session, "isCaptchaWaiting")
#                    if captcha == "true":
#                        dialog = xbmcgui.Dialog()
#                        dialog.ok('Captcha en attente', "Veuillez vous connecter sur http://"+iptools.get_lan_ip()+":"+addon.getSetting("ip_port")+" pour le rentrer.")
#                    time.sleep(10)
#                    fileinfo = downloader.send(session, "getFileData", fid=fileid["links"][0]["fid"])
#                    fileinfo = downloader.parse_json(fileinfo)
#                    dialog = xbmcgui.Dialog()
#                    dialog.ok('Telechargement en cours', "Veuillez vous connecter sur http://"+iptools.get_lan_ip()+":"+addon.getSetting("ip_port")+" pour plus d\'informations.")
#                    try:
#                        self.play_media(xbmc.translatePath("file:///"+download_folder+"/"+folder+"/"+fileinfo["name"]+".chunk0"))
#                    except IOError:
#                        return result
#            except:
#                return result

        try:
            URL = urlopener.loc_url
        except AttributeError:
            URL = URL
        
        SetInfoText("Loading...... ", setlock=True)

        self.pls.clear() #clear the playlist
                
        ext = getFileExtension(URL)
        #todo ashx  
        if ext == 'ashx':
            ext = 'm3u'
               
        if ext == 'pls' or ext == 'm3u':
            loader = CFileLoader2() #file loader
            loader.load(URL, tempCacheDir + "playlist." + ext, retries=2)
            if loader.state == 0: #success
                result = self.pls.load(loader.localfile)
                if result == False:
                    return {"code":1}
                    
                #xbmc.Player.play(self, self.pls) #play the playlist
                self.play_media(loader.localfile)
        else:
            #self.pls.add(urlopener.loc_url)
            if mediaitem.playpath != '':
                self.play_RTMP(mediaitem.URL, mediaitem.playpath, mediaitem.swfplayer, mediaitem.pageurl);
            else: 
                self.play_media(URL)
        
        if not (xbmc.Player().isPlaying()):
            return {"code":1,"error":"unable to play this item"} 
            
        return {"code":0}

    ######################################################################
    ######################################################################  
    def play_media(self, URL):
        if xbmc.getInfoLabel("System.BuildVersion")[:2] == '10':
            #XBMC Dharma
            cmd = 'xbmc.PlayMedia(%s)' % URL
            xbmc.executebuiltin(cmd)
        else:
            xbmc.Player.play(self, URL)
            
    ######################################################################
    ###################################################################### 
    def play_RTMP(self, URL, playpath, swfplayer, pageurl):
        #check if the URL is empty or not
        if URL == '':
            return {"code":1,"data":"URL is empty"}
    
        self.pls.clear() #clear the playlist
    
        item=xbmcgui.ListItem('', iconImage='', thumbnailImage='')
        if swfplayer != '':
            item.setProperty("SWFPlayer", swfplayer)
        if playpath != '':
            item.setProperty("PlayPath", playpath)
        if pageurl != '':
            item.setProperty("PageURL", pageurl)

        xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(URL, item)
        
        return {"code":0}
        
