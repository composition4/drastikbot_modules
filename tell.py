#!/usr/bin/env python3
# coding=utf-8

# Tell Module for Drastikbot
#
# It works "like" memoserv. A user tells the bot to tell a message to a nick when that nick is seen.
# .tell drastik drastikbot is down | .tell <NICKNAME> <MESSAGE>

class Module():
    def __init__(self):
        self.commands = ['#auto#','tell']

def add(reciever, msg, sender, dbc):
    dbc.execute('''CREATE TABLE IF NOT EXISTS tell (reciever TEXT, msg TEXT, sender TEXT, date INTEGER);''')
    dbc.execute('''INSERT INTO tell VALUES (?, ?, ?, strftime('%s', 'now'));''',(reciever, msg, sender))
    
def find(nick, irc, dbc):
    try:
        dbc.execute('''SELECT sender, msg FROM tell WHERE reciever=?;''', (nick,))
        fetch = dbc.fetchall()
        
        for i in fetch:
            irc.privmsg(nick, '{}: {}'.format(i[0], i[1]))
    
        dbc.execute('''DELETE FROM tell WHERE reciever=?;''', (nick,)) # delete msg after it's sent
        dbc.execute('''DELETE FROM tell WHERE (strftime('%s', 'now') - date) > (3600 * 24 * 30 * 3);''') # delete old msges
    except: #nothing in the db yet, ignore errors
        pass
    
def main(cmd, info, db, irc):
    dbc       = db[1].cursor()
    channel   = info[0]
    usernick  = info[1]
    arg       = info[3]
    
    if 'tell' == cmd:
        try: 
            arg_list  = arg.split(' ', 1)
            reciever  = arg_list[0]
            msg       = arg_list[1]
        except IndexError:
            irc.privmsg(channel, 'Usage: {}tell <NICKNAME> <MESSAGE>'.format(irc.prefix))

        #if usernick == reciever:
        #    irc.privmsg(channel, 'You can tell yourself that.')
        if irc.nickname == reciever:
            irc.privmsg(channel, '{}: I am here now, tell me.'.format(usernick))
        else:
            add(reciever, msg, usernick, dbc)
            irc.privmsg(channel, '{}: I will tell {} when i see them.'.format(usernick, reciever))

    find(usernick, irc, dbc)
    db[1].commit()
