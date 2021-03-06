import xbmc, xbmcgui, xbmcaddon
import re, os, time, datetime, traceback
import urllib2
import zipfile
import shutil

#############################################################################
# directory settings
#############################################################################

addon = xbmcaddon.Addon(id='script.apiportal')
RootDir = addon.getAddonInfo('path')

if RootDir[-1]==';': RootDir=RootDir[0:-1]
if RootDir[0] == '/':
    if RootDir[-1] != '/': RootDir = RootDir+'/'
else:
    if RootDir[-1]!='\\': RootDir = RootDir+'\\'

import xbmc
version = xbmc.getInfoLabel("System.BuildVersion")[:1]

#version = xbmc.getInfoLabel("System.BuildVersion")[:1]
if xbmc.getInfoLabel("System.BuildVersion")[:2] == '10':
    scriptDir = "special://home/addons/"
    pluginDir = "special://home/addons/"
    skinDir = "special://home/skin/"
    aPiPortalDir = scriptDir + "aPiPortal/"  
elif xbmc.getInfoLabel("System.BuildVersion")[:1] == '9':
    scriptDir = "special://home/scripts/"
    pluginDir = "special://home/plugins/"
    skinDir = "special://home/skin/"   
    aPiPortalDir = scriptDir + "aPiPortal/"   
else: 
    scriptDir = "Q:\\scripts\\"
    pluginDir = "Q:\\plugins\\"
    skinDir = "Q:\\skin\\"
    aPiPortalDir = scriptDir + "aPiPortal\\"    

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
#platform = get_system_platform()

shutil.copyfile(RootDir + 'startup.plx', aPiPortalDir + 'startup.plx')

xbmc.executescript(aPiPortalDir + 'default.py')

#xbmc.sleep(1000)
