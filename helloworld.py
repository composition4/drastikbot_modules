#!/usr/bin/env python3
# coding=utf-8

import time

#A module to demonstrate how a Drastikbot module should be structured

class Module(): # Request commands to be used by the module
    def __init__(self):
        self.commands = ['hello','world']
        
def hello():
    b = 'world'
    return b

def world():
    a = 'hello'
    return a

def main(cmd, info, db, irc): # Main function called by the bot when a command is triggered
    # "cmd" is the command(s) requested in the Module class
    # "info" is a list containing:[channel, usernick, txtmsg, msg_nocmd]
    # "irc" is the irc library
    if cmd == 'hello':
        time.sleep(20)
        irc.privmsg(info[0], 'world')
    elif cmd == 'world':
        irc.privmsg(info[0], 'hello')
    
