#!/usr/bin/env python3
# coding=utf-8

# Help Module for Drastikbot

class Module(): # Request commands to be used by the module
    def __init__(self):
        self.commands = ['help','bots']

def main(cmd, info, db, irc):
    try:
        msg_nocmd = info[2].split(' ',1)[1].strip()
    except IndexError:
        msg_nocmd = ''
        
    if 'help' == cmd and not info[3]:
        irc.privmsg(info[0], '{}: Help: https://drastik.org/drastikbot/help.html'.format(info[1]))
    elif 'bots' == cmd and not info[3]:
        irc.privmsg(info[0], 'Drastikbot v2.0 :: Python 3 :: https://drastik.org/drastikbot')
