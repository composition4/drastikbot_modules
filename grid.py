#!/usr/bin/env python3
# coding=utf-8

import time
import json
from passlib.hash import argon2
from config import Config

# SYSTEM MODULE
#
# TheGrid: Bot Administration Module for drastikbot
#
# NOTES:
#     * You might want to change the command for this module so that it will be harder to guess.
#         * The variables are: self.commands in Module(): , c in main():
#     * The first time the module will be loaded, the bot owner must register with .grid login <PASS>
#
# DEPENDENCIES:
#     * passlib :: pip3 install passlib
#         * argon2_cffi :: pip3 install argon2_cffi

class Module(): # Request commands to be used by the module
    def __init__(self):
        self.commands = ['grid']
        self.system   = True

class TheGrid():
    def __init__(self, irc, user, db):
        conf = Config(irc.cd)
        config = conf.read()['irc']['modules']['settings']['grid']
        self.owner = config['owner']
        
        self.irc = irc
        #self.dbm = db[0] # memory database
        #self.dbmc = self.dbm.cursor()
        self.db = db[1] # disk database
        self.dbc = self.db.cursor()
        
        self.user = user
        self.admins = {self.owner: ['ALL']}
        self.logged = {}

        try: # get a list of the registered admins
            self.dbc.execute('''SELECT user, access FROM TheGrid''')
            fetch = self.dc.fetchall()
            for f in fetch:
                self.admins[f[0]].append(json.loads(f[1]))
        except:
            pass
        
        try: # get a dictionary of the logged in users and the time they logged in
            self.dbc.execute('''SELECT user, time FROM TheGrid''')
            fetch = self.dbc.fetchall()
            for f in fetch:
                if time.time() - f[1] < 600:
                    del self.logged[f[0]]
                else:
                    self.logged[f[0]].append[f[1]]
        except:
            pass

    def password_hash(self, password):
        return argon2.hash(password)

    def password_verify(self, password, saved_hash):
        return argon2.verify(password, saved_hash)
        
    def register(self, password): # register function used to make the owner account
        self.dbc.execute('''CREATE TABLE IF NOT EXISTS TheGrid (user PRIMARY TEXT, password TEXT, access TEXT, time INTEGER);''')
        if self.user == self.owner:
            self.dbc.execute('''INSERT INTO TheGrid (user, password, access) VALUES (?, ?, ALL);''', (self.user, self.password_hash(password)))
            self.irc.notice(self.user, 'Created owner account')
        else:
            pass
        self.dbc.commit()
        
    def login(self, password):
        # check if user is in database and authenticate them.
        self.dbc.execute('''SELECT password FROM TheGrid WHERE user=?;''', (self.user,))
        fetch = self.dbc.fetchone()
        if self.password_verify(password, fetch[0]):
            self.dbc.execute('''INSERT INTO TheGrid time VALUES strftime('%s', 'now') WHERE user=?;''',(user,))
            self.irc.notice(self.user, 'You are now logged in.')
        else:
            return self.irc.notice(self.user, 'Login incorrect')

    def logout(self):
        if self.user in self.logged:
            del self.logged[self.user]
            self.dbc.execute('''UPDATE TheGrid SET time = 0 WHERE user=?''', (self.user,))          
            self.dbc.commit()
            return self.irc.notice(self.user,'You are now logged out.')

    def useradd(self, user, channels, password):
        if self.user == self.owner:
            c = ",".join(channels.replace(' ',''))
            c = json.dumps(c)
            self.dbc.execute('''INSERT INTO TheGrid (user, password, access) VALUES (?, ?, ?);''', (user, self.password_hash(password), c))
            self.dbc.commit()
            return self.irc.notice(self.user, 'Added user: {} with permitions for: {}'.format(user, c))
        
    def userdel(self, user):
        if self.user == self.owner:
            self.dbc.execute('''DELETE FROM TheGrid WHERE user=?;''', (user,))
            self.dbc.commit()
            return self.irc.notice(self.user, 'Deleted user: {}'.format(user))
        
    def reload(self, botsys):
        if self.user == self.owner:
           botsys[0]
           return self.irc.notice(self.user, 'Modules reloaded.')

    def privmsg(self, reciever, msg):
        if self.user == self.owner:
            return self.irc.privmsg(reciever, msg)

    def notice(self, reciever, msg):
        if self.user == self.owner:
            return self.irc.notice(reciever, msg)

    def mod_whitelist_add(self, module, channel, botsys):
        if module not in botsys[1].modules:
            return self.irc.notice(self.user, 'Module {} is not loaded'.format(module))
        if module in
        if self.user == self.owner:
            botsys[1].whitelist[module].append(channel)
        elif channel in self.admins[self.user]:
            botsys[1].whitelist[module].append(channel)    
        
    def helplist(self, user, irc):
        return #add a list of all the commands to be send as a privmsg to the user

def main(cmd, info, db, irc, botsys):
    channel   = info[0]
    user      = info[1]
    txtmsg    = info[2]
    msg_nocmd = info[3]
    args = msg_nocmd.split()

    tg = TheGrid(irc, user, db)
    c = 'grid'
    
    if self.user in self.logged:
        
        if c == cmd and not self.msg_nocmd: # .grid
            irc.privmsg(self.user, self.helplist(self.user))
        elif (c == cmd) and ('login' in args[0]): # .grid login <USER>:<PASSWORD>
            irc.notice(self.user, self.login(args[1]), db)
        elif (c == cmd) and ('logout' in args[0]): # .grid logout
            irc.notice(self.user, self.logout(self.user))
        elif (c == cmd) and ('privmsg' in args[0]): # .grid privmsg <CHANNEL> <TEXT>
            irc.privmsg(args[2], self.msg_nocmd.split(' ', 3)[3])
        elif (c == cmd) and ('notice' in args[0]): # .grid notice <CHANNEL> <TEXT>
            irc.notice(args[2], self.msg_nocmd.split(' ', 3)[3])
            
    elif (self.user in self.admins) and not (self.user in self.logged):
        
        if c == cmd and not self.msg_nocmd:
            irc.notice(info[1], 'You are not authorized')
        elif (c == cmd) and ('login' in args[0]):
            irc.notice(self.user, self.login(args[1]), db)
