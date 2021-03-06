#!/usr/bin/env python3
# coding=utf-8

'''
Seen module for drastikbot.
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

import datetime

# Seen Module for Drastikbot
#
# It logs the last activity of every user posting and returns it upon request.
# It logs time, post, nickname, channel.
#
# user = The one used the bot (or posted a random line)
# nick = The nickname requested by the user


class Module():

    def __init__(self):
        self.commands = ['#auto#', 'seen']


def update(channel, nick, msg, time, dbc):
    dbc.execute(
        '''CREATE TABLE IF NOT EXISTS seen (nick TEXT PRIMARY KEY, msg TEXT, time TEXT, channel TEXT);''')
    dbc.execute(
        '''INSERT OR IGNORE INTO seen (nick, msg, time, channel) VALUES (?, ?, ?, ?);''',
                (nick, msg, str(time), channel))
    dbc.execute('''UPDATE seen SET msg=?, time=?, channel=? WHERE nick=?;''',
                (msg, str(time), channel, nick))


def fetch(nick, dbc):
    try:
        dbc.execute(
            '''SELECT msg, time, channel FROM seen WHERE nick=?;''', (nick,))
        fetch = dbc.fetchone()
        msgFnd = fetch[0]
        timeFnd = datetime.datetime.strptime(fetch[1], "%Y-%m-%d %H:%M:%S")
        channelFnd = fetch[2]
        return (msgFnd, timeFnd, channelFnd)
    except:
        return False


def main(cmd, info, db, irc):
    dbc = db[1].cursor()
    timestamp = datetime.datetime.utcnow().replace(microsecond=0)
    channel = info[0]
    usernick = info[1]
    arg = info[3]
    msg = info[2]

    update(channel, usernick, msg, timestamp, dbc)
    db[1].commit()
    if cmd == 'seen':
        get = fetch(arg, dbc)
        if get:
            ago = timestamp - get[1]
            if '\x01ACTION' in get[0][:10]:
                toSend = '{} was last seen at {} UTC [{} ago], doing "{} {}"'.format(
                    info[3], get[1], ago, info[3], get[0][8:])
            else:
                toSend = '{} was last seen at {} UTC [{} ago], saying "{}"'.format(
                    info[3], get[1], ago, get[0])
        elif arg == '':
            return irc.privmsg(channel, 'Usage: {}seen <NICKNAME>'.format(info[4]))
        else:
            return irc.privmsg(channel, "Sorry, I have't seen {} around".format(arg))

        if arg == usernick:
            irc.privmsg(channel, 'You are here')
        elif get[2] == channel:
            irc.privmsg(channel, toSend)
        elif get[2] != channel:
            toSend = '{} in {}'.format(toSend, get[2])
            irc.privmsg(channel, toSend)
