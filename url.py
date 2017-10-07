#!/usr/bin/env python3
# coding=utf-8

import re
import math
import requests
import bs4

# URL Module for Drastikbot
#
# Depends:
#   - requests      :: $ pip3 install requests
#   - beautifulsoup :: $ pip3 install beautifulsoup4

class Module(): # Request commands to be used by the module
    def __init__(self):
        self.commands = ['#auto#']

def convert_size(size_bytes):
    #https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])
        
def main(cmd, info, db, irc):
    # "cmd" is the command(s) requested in the Module class
    # "info" is a list containing:[channel, usernick, txtmsg]
    # "irc" is the irc library
    msg = info[2]
    
    #regex = '(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?'
    regex = '([http|https:\/\/[\w_-]+(?:(?:\.[\w_-]+)+)[\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-]?)'
    urls = re.findall(regex, msg)
    for u in urls:
        if not (u.startswith('http://') or u.startswith('https://')):
            u = 'http://' + u
            
        r = requests.get(u, stream = True, timeout=2)
        data = ''
        try:
            for i in r.iter_content(chunk_size=512, decode_unicode=True):
                data += i
                if '</title>' in data.lower():
                    html = bs4.BeautifulSoup(data, "html.parser")
                    irc.privmsg(info[0], html.title.text.strip())
                    break
                elif len(data) > 70000:
                    irc.privmsg(info[0], 'This file or website is too big')
                    break
        except:
            irc.privmsg(info[0], '{}, Size: {}'.format(
                r.headers['content-type'], convert_size(float(r.headers['content-length']))))
        finally:
            r.close()
