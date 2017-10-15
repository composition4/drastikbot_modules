#!/usr/bin/env python3
# coding=utf-8

'''
Search module for drastikbot.
Copyright (C) 2017 drastik.org

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import urllib.parse
import json
import requests
import bs4

# Search Module for Drastikbot
#
# Provides the results of various search engines like:
# Google, YouTube (and HookTube), Bing, Duckduckgo, Searx, Startpage
#
# Depends:
#   - requests      :: $ pip3 install requests
#   - beautifulsoup :: $ pip3 install beautifulsoup4


class Module():  # Request commands to be used by the module

    def __init__(self):
        self.commands = ['g', 'yt', 'ht', 'bing', 'ddg', 'searx', 'sp']


def str2url(query):
    return urllib.parse.quote_plus(query)


def short_url(url):
    service = 'http://tinyurl.com/create.php?source=indexpage&url={}&submit=Make+TinyURL%21&alias='.format(
        url)
    r = requests.get(service, timeout=2)
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    return soup.find('a', {'target': ['_blank']}, href=True).get('href')


def google(query):
    search = 'https://www.google.com/search?q={}'.format(query)
    r = requests.get(search, timeout=2)
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    return soup.find('cite').text


def youtube(query):
    search = 'https://www.youtube.com/results?search_query={}'.format(query)
    r = requests.get(search, timeout=2)
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    return soup.find('a', {'class': ['yt-uix-tile-link']}, href=True).get('href')


def bing(query):
    search = 'https://www.bing.com/search?q={}'.format(query)
    r = requests.get(search, timeout=2)
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    return soup.find('cite').text


def ddg(query, query_p):
    if query_p[0] == '!':
        search = 'http://api.duckduckgo.com/?q={}&format=json&no_redirect=1'.format(
            query)
        r = requests.get(search, timeout=2)
        data = json.loads(r.text)
        return data["Redirect"]
    else:
        search = 'https://duckduckgo.com/html/?q={}'.format(query)
        r = requests.get(search, timeout=2)
        soup = bs4.BeautifulSoup(r.text, "html.parser")
        result = soup.find(
            'a', {'class': ['result__url']}, href=True).get('href')
        result = urllib.request.unquote(result)[15:]
        if len(result) > 80:
            return short_url(result)
        else:
            return result


def searx(query):
    search = 'https://searx.me/?q={}'.format(query)
    r = requests.get(search, timeout=5)
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    return soup.find('div', {'class': ['external-link']}).text


def startpage(query):
    search = 'https://www.startpage.com/do/asearch?q={}'.format(query)
    r = requests.get(search, timeout=2)
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    return soup.find('a', {'id': ['title_1']}, href=True).get('href')


def title(url):
    # this is modified code from the url.py module, safe only for youtube.
    r = requests.get(url, stream=True, timeout=2)
    data = ''
    for i in r.iter_content(chunk_size=512, decode_unicode=True):
        data += i
        if '</title>' in data.lower():
            html = bs4.BeautifulSoup(data, "html.parser")
            return html.title.text.strip()
            break


def main(cmd, info, db, irc):
    # "cmd" is the command(s) requested in the Module class
    # "info" is a list containing:[channel, usernick, txtmsg]
    # "irc" is the irc library
    query_p = info[2].split(' ', 1)[1]
    query = str2url(query_p)
    if cmd == 'g':
        irc.privmsg(
            info[0], '\x0302G\x0304o\x0308o\x0302g\x0309l\x0304e\x0F: {}'.format(google(query)))
    elif cmd == 'yt':
        yt_url = youtube(query)
        irc.privmsg(info[0], '\x0301,00You\x0300,04Tube\x0F: https://www.youtube.com{} | {}'.format(
            yt_url, title('https://www.youtube.com{}'.format(yt_url))))
    elif cmd == 'ht':
        yt_url = youtube(query)
        irc.privmsg(info[0], '\x0315hooktube\x0F: https://hooktube.com{} | {}'.format(
            yt_url, title('https://www.youtube.com{}'.format(yt_url))))
    elif cmd == 'bing':
        irc.privmsg(info[0], '\x0315Bing\x0F: {}'.format(bing(query)))
    elif cmd == 'ddg':
        irc.privmsg(
            info[0], '\x0315DuckDuckGo\x0F: {}'.format(ddg(query, query_p)))
    elif cmd == 'searx':
        irc.privmsg(info[0], '\x0315sear\x0311X\x0F: {}'.format(searx(query)))
    elif cmd == 'sp':
        irc.privmsg(
            info[0], '\x0304start\x0302page\x0F: {}'.format(startpage(query)))
