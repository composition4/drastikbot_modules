#!/usr/bin/env python3
# coding=utf-8

#A module to demonstrate how a Drastikbot module should be structured

class Module(): # Request commands to be used by the module
    def __init__(self):
        self.commands = ['memtest']

def main(cmd, info, irc): # Main function called by the bot when a command is triggered
    # "cmd" is the command(s) requested in the Module class
    # "info" is a list containing:[channel, usernick, txtmsg]
    # "irc" is the irc library
    c = info[3].cursor()
    try:
        c.execute('''CREATE TABLE a (b)''')
    except:
        print('olagood')
    c.execute("INSERT INTO a VALUES (1)")
    if cmd is 'memtest':
        c.execute('SELECT b FROM a')
        irc.privmsg(info[0], str(c.fetchall()))
    
