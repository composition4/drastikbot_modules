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
#     * The first time the module will be loaded, the bot owner must register with .grid register <PASS>
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
        self.config_r = Config(irc.cd).read()
        self.config_w = Config(irc.cd).write
        self.owner = self.config_r['irc']['owner']
        
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
            fetch = self.dbc.fetchall()
            for f in fetch:
                if f[0] == self.owner: continue
                self.admins[f[0]] = json.loads(f[1])
        except:
            pass
        
        try: # get a dictionary of the logged in users and the time they logged in
            self.dbc.execute('''SELECT user, time FROM TheGrid''')
            fetch = self.dbc.fetchall()
            for f in fetch:
                if time.time() - f[1] > 600:
                    try: del self.logged[f[0]]
                    except: pass
                else: self.logged[f[0]] = f[1]
        except: pass

    def password_hash(self, password):
        return argon2.hash(password)

    def password_verify(self, password, saved_hash):
        return argon2.verify(password, saved_hash)
        
    def register(self, password): # register function used to make the owner account
        self.dbc.execute('''CREATE TABLE IF NOT EXISTS TheGrid (user TEXT PRIMARY KEY, password TEXT, access TEXT, time INTEGER);''')
        if self.user == self.owner:
            self.dbc.execute('''INSERT INTO TheGrid (user, password, access, time) VALUES (?, ?, 'ALL', 0);''', (self.user, self.password_hash(password)))
            self.irc.notice(self.user, 'Created owner account')
        else:
            pass
        self.db.commit()
        
    def login(self, password):
        # check if user is in database and authenticate them.
        self.dbc.execute('''SELECT password FROM TheGrid WHERE user=?;''', (self.user,))
        fetch = self.dbc.fetchone()
        if self.password_verify(password, fetch[0]):
            self.dbc.execute('''UPDATE TheGrid SET time = strftime('%s', 'now') WHERE user=?;''', (self.user,))
            self.db.commit()
            return self.irc.notice(self.user, 'You are now logged in.')
        else:
            return self.irc.notice(self.user, 'Login incorrect')

    def logout(self):
        if self.user in self.logged:
            del self.logged[self.user]
            self.dbc.execute('''UPDATE TheGrid SET time = 0 WHERE user=?;''', (self.user,)) 
            self.db.commit()
            return self.irc.notice(self.user,'You are now logged out.')

    def useradd(self, user, password, channels):
        if self.user == self.owner:
            if ',' in channels: # fragile maybe fix
                c = ''.join(channels.split())
                c = c.split(',')
            else:    
                c = channels.split()
            c = json.dumps(c)
            self.dbc.execute('''INSERT INTO TheGrid (user, password, access, time) VALUES (?, ?, ?, 0);''', (user, self.password_hash(password), c))
            self.db.commit()
            return self.irc.notice(self.user, 'Added user: {} with permitions for: {}'.format(user, c))
        
    def userdel(self, user):
        if self.user == self.owner:
            self.dbc.execute('''DELETE FROM TheGrid WHERE user=?;''', (user,))
            self.db.commit()
            return self.irc.notice(self.user, 'Deleted user: {}'.format(user))

    def userpass(self, user, password):
        if self.user == self.owner or user == self.user:
            self.dbc.execute('''UPDATE TheGrid SET password=? WHERE user=?;''', (self.password_hash(password), user))
            self.db.commit()
            return self.irc.notice(self.user, 'Changed password for user {}'.format(user))

    def userchannel(self, user, channel):
        if self.user == self.owner:
            self.dbc.execute('''SELECT access FROM TheGrid WHERE user=?;''', (user,))
            fetch = json.loads(self.dbc.fetchone()[0])
            fetch.append(channel)
            fetch = json.dumps(fetch)
            self.dbc.execute('''UPDATE TheGrid SET access=? WHERE user=?;''', (fetch, user))
            self.db.commit()
            return self.irc.notice(self.user, "Added channel {} to {}'s access list.".format(channel, user))

    def userlist(self):
        if self.user == self.owner:
            self.dbc.execute('''SELECT user, access FROM TheGrid;''')
            for f in self.dbc.fetchall():
                self.irc.notice(self.user, str(f).replace("'", '').strip("()").replace('"', ''))
                
    def privmsg(self, reciever, msg):
        if (self.user == self.owner) or (channel in self.admins[self.user]):
            return self.irc.privmsg(reciever, msg)

    def notice(self, reciever, msg):
        if (self.user == self.owner) or (channel in self.admins[self.user]):
            return self.irc.notice(reciever, msg)

    def join(self, channel, password):
        if self.user == self.owner:
            chanDict = {channel: password}
            self.irc.join(chanDict)
            self.config_r['irc']['channels']['join'][channel] = password
            self.config_w(self.config_r)
            return self.irc.notice(self.user, 'Joined {}'.format(channel))
        
    def part(self, channel, msg=None):
        if self.user == self.owner:
            self.irc.part(channel, msg)
            del self.config_r['irc']['channels']['join'][channel]
            self.config_w(self.config_r)
            return self.irc.notice(self.user, 'Left {}'.format(channel))
        
    def module_setlist_add(self, mode, module, channel, botsys):
        if mode == 'whitelist': edom = 'blacklist'
        elif mode == 'blacklist': edom = 'whitelist'

        if module not in botsys[0]:
            return self.irc.notice(self.user, 'Module "{}" is not loaded.'.format(module)) 
        try:
            c = self.config_r['irc']['modules']['settings'][module]
            if edom in c and len(c[edom]) != 0:
                return self.irc.notice(self.user, 'Failed to add a {}. A {} for "{}" has already been set.'.format(mode, edom, module))
            if channel in c[mode]:
                return self.irc.notice(self.user, 'Module "{}" is already {}ed from channel "{}".'.format(module, edom, channel))
        except KeyError: pass
        
        if (self.user == self.owner) or (channel in self.admins[self.user]):
            try: self.config_r['irc']['modules']['settings'][module][mode].append(channel)
            except KeyError: self.config_r['irc']['modules']['settings'][module] = {mode: [channel]}
            except KeyError: self.config_r['irc']['modules']['settings'] = {module : {mode: [channel]}}
            except KeyError: self.config_r['irc']['modules'] = {"settings": {module : {mode: [channel]}}}
            self.config_w(self.config_r)
            return self.irc.notice(self.user, 'Done.')

    def module_setlist_del(self, mode, module, channel):
        c = self.config_r['irc']['modules']['settings'][module][mode]
        if channel in c:
            if (self.user == self.owner) or (channel in self.admins[self.user]):
                c.remove(channel)
                self.config_w(self.config_r)
                return self.irc.notice(self.user, 'Done.')
        else:
            return self.irc.notice(self.user, 'Module "{}" has no {} for channel "{}"'.format(module, mode, channel))

    def module_setlist_list(self, module):
        try:
            c = self.config_r['irc']['modules']['settings'][module]
        except KeyError: return self.irc.notice(self.user, 'No blacklist or whitelist set for module {}.'.format(module))
        return self.irc.notice(self.user, '"{}": {}'.format(module, str(c).strip('{}')))
        
    def set_global_prefix(self, prefix):
        if self.user == self.owner:
            self.config_r['irc']['modules']['global_prefix'] = prefix
            self.config_w(self.config_r)
            return self.irc.notice(self.user, 'Changed the global_prefix to "{}"'.format(prefix))
            
    def set_chan_prefix(self, channel, prefix):
        if (self.user == self.owner) or (channel in self.admins[self.user]):
            try: self.config_r['irc']['channels']['settings'][channel]['prefix'].append(prefix)
            except KeyError: self.config_r['irc']['channels']['settings'][channel] = {"prefix": prefix }
            except KeyError: self.config_r['irc']['channels']['settings'] = {channel : {"prefix": prefix }}
            except KeyError: self.config_r['irc']['channels'] = {"settings": {channel : {"prefix": prefix }}}
            self.config_w(self.config_r)
            return self.irc.notice(self.user, 'Changed the prefix for channel "{}" to "{}"'.format(channel, prefix))

    def mod_import(self, botsys):
        if self.user == self.owner:
            botsys()
            return self.irc.notice(self.user, 'Imported new modules')
        
    def helplist(self, user, irc):
        return #add a list of all the commands to be send as a privmsg to the user

def main(cmd, info, db, irc, botsys):
    channel   = info[0]
    user      = info[1]
    txtmsg    = info[2]
    msg_nocmd = info[3]
    args = msg_nocmd.split()

    grid = TheGrid(irc, user, db)
    c = 'grid'
    
    if user in grid.logged and c == cmd:
        
        if not msg_nocmd: # .grid
            irc.privmsg(user, grid.helplist(user))

        elif 'logout' in args[0] and len(args) == 1:
            # .grid logout
            grid.logout()

        elif 'import' in args[0] and len(args) == 1:
            # .grid import
            grid.mod_import(botsys[1])
            
        elif 'privmsg' in args[0]:
            # .grid privmsg <RECIEVER> <TEXT>
            grid.privmsg(args[1], msg_nocmd.split(' ', 2)[2])
        elif 'notice' in args[0]:
            # .grid notice <RECIEVER> <TEXT>
            grid.notice(args[1], msg_nocmd.split(' ', 2)[2])
        elif 'join' in args[0] and len(args) <= 3 :
            # .grid join <CHANNEL> <password>
            try: password = args[2]
            except IndexError: password = ''
            grid.join(args[1], password)
        elif 'part' in args[0] and len(args) <= 3:
            # .grid part <CHANNEL> <msg>
            try: msg = args[2]
            except IndexError: msg = ''
            grid.part(args[1], msg)
            
        elif 'user' in args[0] and 'add' in args[1]:
            # .grid user add <NICK> <PASSWORD> <CHANNEL1, CHANNEL2>
            grid.useradd(args[2], args[3], msg_nocmd.split(' ',4)[4])
        elif 'user' in args[0] and 'del' in args[1] and len(args) == 3:
            # .grid user del <USER>
            grid.userdel(args[2])
        elif 'user' in args[0] and 'password' in args[1] and len(args) == 4:
            # .grid user password <USER> <PASSWORD>
            grid.userpass(args[2], args[3])
        elif 'user' in args[0] and 'channel' in args[1] and len(args) == 4:
            # .grid user channel <USER> <CHANNEL>
            grid.userchannel(args[2], args[3])
        elif 'user' in args[0] and 'list' in args[1] and len(args) == 2:
            # .grid user list
            grid.userlist()
            
        elif 'module' in args[0] and 'whitelist' in args[1] and 'add' in args[2] and len(args) == 5:
            # .grid module whitelist add <MODULE> <CHANNEL>
            grid.module_setlist_add('whitelist', args[3], args[4], botsys)
        elif 'module' in args[0] and 'whitelist' in args[1] and 'del' in args[2] and len(args) == 5:
            # .grid module whitelist del <MODULE> <CHANNEL>
            grid.module_setlist_del('whitelist', args[3], args[4])
        elif 'module' in args[0] and 'blacklist' in args[1] and 'add' in args[2] and len(args) == 5:
            # .grid module blacklist add <MODULE> <CHANNEL>
            grid.module_setlist_add('blacklist', args[3], args[4], botsys)
        elif 'module' in args[0] and 'blacklist' in args[1] and 'del' in args[2] and len(args) == 5:
            # .grid module blacklist del <MODULE> <CHANNEL>
            grid.module_setlist_del('blacklist', args[3], args[4])
        elif 'module' in args[0] and 'list' in args[1] and len(args) == 3:
            # .grid module list <MODULE>
            grid.module_setlist_list(args[2])
            
        elif 'prefix' in args[0] and 'channel' in args[1] and len(args) == 4:
            # .grid prefix channel <CHANNEL> <PREFIX>
            grid.set_chan_prefix(args[2], args[3])
        elif 'prefix' in args[0] and 'global' in args[1] and len(args) == 3:
            # .grid prefix global <PREFIX>
            grid.set_global_prefix(args[2])

        elif 'login' in args[0] and len(args) <= 2:
            irc.notice(user, 'You are already logged in.')
            
    elif user in grid.admins and not user in grid.logged and c == cmd:
        
        if not msg_nocmd:
            irc.notice(info[1], 'You are not authorized.')
        elif 'login' in args[0] and len(args) == 2:
            # .grid login <PASSWORD>
            grid.login(args[1])
        elif 'register' in args[0] and len(args) == 2:
            # .grid register <PASSWORD>
            grid.register(args[1])
        else:
            irc.notice(info[1], 'You are not authorized.')
