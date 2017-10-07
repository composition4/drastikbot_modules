#!/usr/bin/env python3
# coding=utf-8

import os
import sys
import urllib.parse
import subprocess
from selenium import webdriver
from depot.manager import DepotManager

# Screenshot Module for Drastikbot
#
# It makes screenshots of websites and uploads them to w1r3.net
#
# Dependencies:
#   - PhantomJS :: apt install phantomjs
#   - curl      :: apt install curl
#   - selenium  :: pip3 install selenium
#   - filedepot :: pip3 install filedepot

class Module():
    def __init__(self):
        self.commands = ['screenshot']

def capture(website, height, width):
    filename = website.lstrip('https://') or website.lstrip('http://')
    filename = urllib.parse.quote_plus(filename) + '.png'
    
    if website.startswith('https://'):
        website = website.lstrip('https://')
        website = 'http://' + website
        
    depot = DepotManager.get()
    #browser to use, we disable ssl else screenshots will be empty
    driver = webdriver.PhantomJS(service_args=[
        '--ignore-ssl-errors=true', '--ssl-protocol=any', '--web-security=false'])
    driver.set_window_size(height, width) # set the window size that you need
    driver.get(website)
    driver.save_screenshot(filename)
    driver.quit()
    upload = "upload=@{}".format(filename)
    p = subprocess.Popen(["curl", "-F", upload, "https://w1r3.net"], stdout=subprocess.PIPE)
    (output, err) = p.communicate()
    output = output.decode('utf8')
    output = output.replace("\n","")
    output = output.replace("b'","")
    os.remove(filename)
    return output

def main(cmd, info, db, irc):
    channel   = info[0]
    usernick  = info[1]
    arg       = info[3]
    arg_list  = arg.split()

    def_height = 1280
    def_width  = 720

    max_res = 1920
    
    if 'screenshot' == cmd:
        if len(arg_list) == 1 and arg.startswith("http"):
            output = capture(arg, def_height, def_width)
            irc.privmsg(channel, ('{}: screenshot for "{}": {}'.format(usernick, arg, output)))
        elif len(arg_list) == 3 and arg_list[2].startswith("http"):
            if int(arg_list[0] or arg_list[1]) > max_res:
                irc.privmsg(channel, 'Maximum resolution allowed is {}'.format(max_res))
            else:
                output = capture(arg_list[2], arg_list[0], arg_list[1])
                irc.privmsg(channel, ('{}: screenshot for "{}": {}'.format(usernick, arg_list[2], output)))
        else:
            irc.privmsg(channel, 'Usage: {}screenshot [height width] <WEBSITE>'.format(irc.prefix))
