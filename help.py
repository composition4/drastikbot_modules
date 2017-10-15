#!/usr/bin/env python3
# coding=utf-8

'''
Help module for drastikbot.
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

# Help Module for Drastikbot


class Module():  # Request commands to be used by the module

    def __init__(self):
        self.commands = ['help', 'bots']


def main(cmd, info, db, irc):
    try:
        msg_nocmd = info[2].split(' ', 1)[1].strip()
    except IndexError:
        msg_nocmd = ''

    if 'help' == cmd and not info[3]:
        irc.privmsg(
            info[0], '{}: Help: https://drastik.org/drastikbot/help.html'.format(info[1]))
    elif 'bots' == cmd and not info[3]:
        irc.privmsg(
            info[0], 'Drastikbot v2.0 :: Python 3 :: https://drastik.org/drastikbot')
