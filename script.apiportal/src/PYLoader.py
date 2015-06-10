import unicodedata
from urllib import urlopen, urlencode
import json
import os, xbmcaddon
from settings import *
import xbmc, xbmcgui
import base64
import time

addon = xbmcaddon.Addon(id='script.apiportal')

try: Emulating = xbmcgui.Emulating
except: Emulating = False

class PYLoader:
    def __init__(self, parent=0, URL="http://"+addon.getSetting("ip_adress")+":"+addon.getSetting("ip_port")+"/api/%s"):
        self.parent=parent
        self.processed=False
        self.URL = URL


    def login(self, user=addon.getSetting("username"), pw=addon.getSetting("password")):
        params = {"username": user, "password": pw}
        ret = urlopen(self.URL % "login", urlencode(params))
        return ret.read().strip("\"")

# send arbitrary command to pyload api, parameter as keyword argument
    def send(self, session, command, **kwargs):
        # convert arguments to json format
        params = dict([(k, json.dumps(v)) for k,v in kwargs.iteritems()])
        params["session"] = session
        ret = urlopen(self.URL % command, urlencode(params))
        return ret.read()

    def strip_accents(self, s):
        try:
             s = unicode(s,"ascii")
        except:
             s = unicode(s,"utf-8")
        return ''.join((c for c in unicodedata.normalize('NFKD', s) if unicodedata.category(c) != 'Mn'))

    def parse_json(self, data):
        ret = json.loads(data)
        return ret

    def getcaptcha(self, session):
        time.sleep(10)
        captcha = self.send(session, "isCaptchaWaiting")
        if captcha == "true":
            captcha = self.send(session, "getCaptchaTask")
            captcha = self.parse_json(captcha)
            captchaimg = captcha["data"]
            captchaname = "captcha" + str(captcha["tid"]) + "." + captcha["type"]
            captchafile = open(imageCacheDir + captchaname, "wb")
            captchafile.write(base64.decodestring(captchaimg))
            captchafile.close()
            return imageCacheDir + captchaname
        else:
            return "false"

    def setcaptcha(self, session):
        #print "here"
        captcha = self.send(session, "isCaptchaWaiting")
        #print "captcha:", captcha
        if captcha == "true":
            captcha = self.send(session, "getCaptchaTask")
            #print "captcha task:", captcha
            captcha = self.parse_json(captcha)
            captchaimg = captcha["data"]
            #print "captcha img:", captchaimg
            captchaname = "captcha" + str(captcha["tid"]) + "." + captcha["type"]
            captchafile = open(imageCacheDir + captchaname, "wb")
            captchafile.write(base64.decodestring(captchaimg))
            captchafile.close()
            #print "path:",xbmc.translatePath(imageCacheDir + captchaname)
            img = xbmcgui.ControlImage(550,15,240,100,xbmc.translatePath(imageCacheDir + captchaname))
            xdg = xbmcgui.WindowDialog()
            xdg.addControl(img)
            xdg.show()
            time.sleep(10)
            kb = xbmc.Keyboard('', 'Veuillez indiquer les lettres de l\'image ci-dessus', False)       
            kb.doModal()
            capcode = kb.getText()
            #Check input
            if (kb.isConfirmed()):
                userInput = kb.getText()
                if userInput != '':
                    capcode = kb.getText()
                    #print capcode
                    setcaptcha = self.send(session, "setCaptchaResult", tid=captcha["tid"], result=capcode)
                    time.sleep(10)
                    captcha = self.send(session, "isCaptchaWaiting")
                    os.remove(imageCacheDir + captchaname)
                    return captcha
                elif userInput == '':
                    dialog = xbmcgui.Dialog()
                    dialog.ok('Captcha error', 'Nothing entered. Please try to read the video by relaunching the process.')
            xdg.close()
            os.remove(imageCacheDir + captchaname)
            return "false"

    def setallcaptcha(self, session):
        time.sleep(10)
        while (self.setcaptcha(session)=="true"):
            self.setcaptcha(session)
