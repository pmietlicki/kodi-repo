import xbmc, xbmcgui, xbmcaddon
import re, os, time, datetime, traceback
import urllib2
import zipfile
import shutil
import sys

# Script constants
__scriptname__ = "aPiPortail"
__author__ = "aPiTV"
__url__ = ""
__credits__ = ""
__version__ = "1.0"

addon = xbmcaddon.Addon(id='script.apiportail-fr')
RootDir = addon.getAddonInfo('path')
sys.path.append(os.path.join(RootDir.replace(";",""),'src'))

if RootDir[-1]==';': RootDir=RootDir[0:-1]
if RootDir[0] == '/':
    if RootDir[-1] != '/': RootDir = RootDir+'/'
    SEPARATOR = '/'    
else:
    if RootDir[-1] != '\\': RootDir=RootDir+'\\'
    SEPARATOR = '\\'

version_default = '0.0.0'
version_URL=''
update_URL=''

#############################################################################
def onReadVersion():
    version = version_default
    try:
        f=open(RootDir + 'version.dat', 'r')
        data = f.read()
        data = data.splitlines()
        version=data[0]
        f.close()
    except IOError:
        pass
    
    return version

#############################################################################
def onReadNewVersion(URL):
    version = version_default
    try:
#oldtimeout=socket_getdefaulttimeout()
#socket_setdefaulttimeout(timeout)
            
        f = urllib2.urlopen(URL)

        data = f.read()
        data = data.splitlines()    
        version=data[0]   

    except IOError:
        pass
#socket_setdefaulttimeout(oldtimeout)       
    return version  

#############################################################################
def onSaveVersion(version):
    try:
        f=open(RootDir + 'version.dat', 'w')
        f.write(version + '\n')
        f.close()
    except IOError:
        pass

######################################################################
def installUpdate(URL):
    try:
        #oldtimeout=socket_getdefaulttimeout()
        #socket_setdefaulttimeout(timeout)
            
        f = urllib2.urlopen(URL)

        file = open(RootDir + "update.zip", "wb")
        file.write(f.read())
        file.close()  

    except IOError:
        #socket_setdefaulttimeout(oldtimeout)  
        return -1

    #socket_setdefaulttimeout(oldtimeout)       

    zfobj = zipfile.ZipFile(RootDir + "update.zip")

    for name in zfobj.namelist():
        index = name.rfind('/')
        if index != -1:
            #entry contains path
            if not os.path.exists(RootDir+name[:index+1]):
                try:
                    #create the directory structure
                    os.makedirs(os.path.join(RootDir, name[:index+1]))
                except IOError:
                    return -1 #failure
                    
        if not name.endswith('/'):
            #entry contains a filename
            try:
                outfile = open(os.path.join(RootDir, name), 'wb')
                outfile.write(zfobj.read(name))
                outfile.close()
            except IOError:
                pass #There was a problem. Continue...

    zfobj.close()

    try:
        os.remove(RootDir + "update.zip")
    except IOError:
        pass
        
    return 0 #succesful

######################################################################
def socket_getdefaulttimeout():
    return socket.getdefaulttimeout()

######################################################################
def socket_setdefaulttimeout(url_open_timeout):
    if platform == "xbox":
        socket.setdefaulttimeout(url_open_timeout)

#############################################################################
def Trace(string):
    f = open(RootDir + "trace.txt", "a")
    f.write(string + '\n')
    f.close()

######################################################################  
def get_system_platform():
    platform = "unknown"
    if xbmc.getCondVisibility( "system.platform.linux" ):
        platform = "linux"
    elif xbmc.getCondVisibility( "system.platform.xbox" ):
        platform = "xbox"
    elif xbmc.getCondVisibility( "system.platform.windows" ):
        platform = "windows"
    elif xbmc.getCondVisibility( "system.platform.osx" ):
        platform = "osx"
#    Trace("Platform: %s"%platform)
    return platform

#############################################################################
#############################################################################

#retrieve the platform.
platform = get_system_platform()

#read the current version installed
#version = onReadVersion()
#newversion = onReadNewVersion(version_URL)

#if (version != version_default) and (newversion != version_default) and \
#    (version != newversion):
#    installUpdate(update_URL)
#    #save updated version.
#    onSaveVersion(newversion)
#    dialog = xbmcgui.Dialog()
#    dialog.ok("Message", "aPiTV a ete mis a jour.")


#############################################################################
#Start aPiPortail
#############################################################################
import apitv
win = apitv.MainWindow("skin.xml", addon.getAddonInfo('path'))
win.doModal()
del win

#xbmc.executescript(RootDir + 'default_.py')

