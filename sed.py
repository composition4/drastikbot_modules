#!/usr/bin/env python3
# coding=utf-8

'''
Sed module for drastikbot. Replace text using sed's substitution command.
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

import subprocess
import pickle
import re

# Sed Module for Drastikbot
#
# Replace text using sed's substitution command.
#
# This module keeps a buffer of the last posted messages
# and when the substitution command is issued it calls sed
# and sends the result.
#
# Depends:
#   - sed :: default unix program, should be in the repos


class Module():

    def __init__(self):
        self.commands = ['#auto#']


def write(dbc, channel, msg):
    try:
        dbc.execute('''SELECT msglist FROM sed WHERE channel=?''', (channel,))
        fetch = dbc.fetchone()
        msglist = pickle.loads(fetch[0])
        msglist.append(msg)
    except:
        msglist = [msg]

    if len(msglist) > 50:
        del msglist[0]

    msglist = pickle.dumps(msglist)
    dbc.execute(
        '''CREATE TABLE IF NOT EXISTS sed (channel TEXT PRIMARY KEY, msglist BLOB);''')
    try:
        dbc.execute(
            '''INSERT INTO sed (channel, msglist) VALUES (?, ?);''', (channel, msglist))
    except:
        dbc.execute(
            '''UPDATE sed SET msglist = ? WHERE channel = ?;''', (msglist, channel))


def read(dbc, channel):
    dbc.execute('''SELECT msglist FROM sed WHERE channel=?''', (channel,))
    fetch = dbc.fetchone()
    msglist = pickle.loads(fetch[0])
    return msglist


def main(cmd, info, db, irc):
    dbc = db[0].cursor()
    channel = info[0]
    msg = info[2]

    sed_parse = re.compile('(?<!\\\\)/')
    sed_cmd = re.compile('^s/.*/.*')

    if sed_cmd.match(msg):
        sed_args = sed_parse.split(msg)
        if len(sed_args) < 4:
            # if the last / is missed etc.
            return
        msglist = read(dbc, channel)

        n = 1
        while n <= 50:
            if re.search(sed_args[1], msglist[-n], re.I):
                a = n
                break
            else:
                a = False
            n = n + 1

        if a:
            echo = ['echo', msglist[-a]]
            p = subprocess.run(echo, stdout=subprocess.PIPE)
            echo_outs = p.stdout
            sed = ['sed', '--sandbox', 's/{}/{}/{}'.format(
                sed_args[1], sed_args[2], sed_args[3])]
            p = subprocess.run(sed, stdout=subprocess.PIPE, input=echo_outs)
            sed_outs = p.stdout.decode('utf-8')
            irc.privmsg(channel, sed_outs)
            write(dbc, channel, sed_outs)
    else:
        write(dbc, channel, msg)
