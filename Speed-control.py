import os.path
import subprocess
import urllib2
import cookielib
import re
import json
from configobj import ConfigObj
configfile = 'Speed-control.ini'
config = ConfigObj(configfile)
config.filename = configfile

def ping(ip):
    p = subprocess.Popen(["ping", "-n", "1", ip], stdout=subprocess.PIPE)
    output, err = p.communicate()
    if output[74:102] == "Destination host unreachable":
        return 'ofline'
    else:
        return 'online'

#speed set
def sabnzbdplus_speed_set(host, port, speed, api):
    sab = "http://%s:%s/api?mode=config&name=speedlimit&value=%s&apikey=%s" % (host, port, speed, api)
    urllib2.urlopen(sab)
    return True

def utorrent_speed_set(host, port, username, password, upload_speed, download_speed):
    theurl = 'http://%s:%s/gui/' % (host, port)
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    # this creates a password manager
    passman.add_password(None, theurl, username, password)

    authhandler = urllib2.HTTPBasicAuthHandler(passman)
    # create the AuthHandler

    opener = urllib2.build_opener(authhandler)

    cj = cookielib.CookieJar()
    opener.add_handler(urllib2.HTTPCookieProcessor(cj))

    urllib2.install_opener(opener)
    # All calls to urllib2.urlopen will now use our handler

    pagehandle = urllib2.urlopen(theurl)
    # authentication is now handled automatically for us

    pagehandle = urllib2.urlopen(theurl+"token.html")
    token = re.findall("<div.*?>(.*?)</", pagehandle.read())[0]
    # obtained the token

    add_url = "%s?action=setsetting&token=%s&s=max_ul_rate&v=%s&s=max_dl_rate&v=%s" % (theurl, token, upload_speed, download_speed)
    pagehandle = urllib2.urlopen(add_url)

def transmission_speed_set(host, Port, username, Password, upload_speed, download_speed):
    client = transmissionrpc.Client(
        address=host,
        port=Port,
        user=username,
        password=Password
        )
    if upload_speed != 0:
        client.set_session(
            speed_limit_up_enabled = True,
            speed_limit_up = upload_speed,
            speed_limit_down_enabled = True,
            speed_limit_down = download_speed
            )
    else:client.set_session(
            speed_limit_up_enabled = False,
            speed_limit_down_enabled = False,
            )



#status
def sabnzbdplus_status(host, port, api):
    sab = "http://%s:%s/api?mode=qstatus&output=json&apikey=%s" % (host, port, api)
    info = urllib2.urlopen(sab)
    infoj = json.loads(info.read())
    return {'downloading' : infoj['noofslots'] }

def utorrent_status(host, port, username, password):
    theurl = 'http://%s:%s/gui/' % (host, port)
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    # this creates a password manager
    passman.add_password(None, theurl, username, password)

    authhandler = urllib2.HTTPBasicAuthHandler(passman)
    # create the AuthHandler

    opener = urllib2.build_opener(authhandler)

    cj = cookielib.CookieJar()
    opener.add_handler(urllib2.HTTPCookieProcessor(cj))

    urllib2.install_opener(opener)
    # All calls to urllib2.urlopen will now use our handler

    pagehandle = urllib2.urlopen(theurl)
    # authentication is now handled automatically for us

    pagehandle = urllib2.urlopen(theurl+"token.html")
    token = re.findall("<div.*?>(.*?)</", pagehandle.read())[0]
    # obtained the token

    add_url = "%s?list=1&token=%s" % (theurl, token,)
    pagehandle = urllib2.urlopen(add_url)
    info = json.loads(pagehandle.read())
    tinfo = info['torrents'][0]
    seeding = 0
    downloading = 0
    for t in info['torrents']:
        if t[21] == 'Seeding':
            seeding += 1
        elif t[21] == 'Downloading':
            downloading += 1
    return {'seeding' : seeding, 'downloading' : downloading}

def transmission_status(host, Port, username, Password):
    client = transmissionrpc.Client(
        address=host,
        port=Port,
        user=username,
        password=Password
        )
    seeding = 0
    downloading = 0
    ss = client.session_stats()
    cc = 0
    while cc != ss.torrentCount:
        cc += 1
        wt = client.get_torrent(cc)
        if wt.status == 'seeding':
            seeding += 1
        elif wt.status == 'downloading':
            downloading += 1
    return {'seeding' : seeding, 'downloading' : downloading}

#config
def make_config():
        print 'makeing new config'
        config['Main'] = {}
        config['Main']['IPs'] = ['192.168.1.100', '192.168.1.101', '192.168.1.102']
        config['Main']['download_speed'] = '500'
        config['Main']['upload_speed'] = '100'
        #
        config['Transmission'] = {}
        config['Transmission']['Host'] = ''
        config['Transmission']['Port'] = ''
        config['Transmission']['UserName'] = ''
        config['Transmission']['PassWord'] = ''
        #
        config['sabnzbdplus'] = {}
        config['sabnzbdplus']['Host'] = ''
        config['sabnzbdplus']['Port'] = ''
        config['sabnzbdplus']['apikey'] = ''
        #
        config['utorrent'] = {}
        config['utorrent']['Host'] = ''
        config['utorrent']['Port'] = ''
        config['utorrent']['UserName'] = ''
        config['utorrent']['PassWord'] = ''
        config.write()
online_pc = 0
offline_pc = 0
if os.path.isfile(configfile):
    print "config is ok"
else:
    make_config()

#for ip in config['Main']['IPs']:
#    if ping(ip) == "online":
#        online_pc = online_pc + 1
#    else:
#        offline_pc = offline_pc + 1

#print "There are %i pcs online and %s pcs offline" % (online_pc, offline_pc)
#utorrent_speed_set(
#    config['utorrent']['Host'],
#    config['utorrent']['Port'],
#    config['utorrent']['UserName'],
#    config['utorrent']['PassWord'],
#    config['Main']['upload_speed'],
#    config['Main']['download_speed']
#    )

#sabnzbdplus_speed_set(
#    config['sabnzbdplus']['Host'],
#    config['sabnzbdplus']['Port'],
#    config['Main']['download_speed'],
#    config['sabnzbdplus']['apikey']
#    )

#transmission_speed_set(
#    config['Transmission']['Host'],
#    config['Transmission']['Port'],
#    config['Transmission']['UserName'],
#    config['Transmission']['PassWord'],
#    config['Main']['upload_speed'],
#    config['Main']['download_speed']
#    )

#if config['sabnzbdplus']['Host'] != "":
#    print 'gogo'


