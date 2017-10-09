#!/usr/bin/env python3
# coding=utf-8

import re
import json

# Sed Module for Drastikbot
#
# Based on https://github.com/sys-fs/seddy/blob/master/seddy.py


class Module(): # Request commands to be used by the module
    def __init__(self):
        self.commands = ['#auto#']

class Queue:
    size = 0
    data = {}
    head = {}
    tail = {}
    count = {}
    
    def __init__(self, size, db, channel, irc):
        self.db   = db
        self.size = size
        self.c = channel
        self.data = {}
        for c in irc.channels:
            c = c.strip()
            self.data[c] = [None]*size
            self.tail[c] = 0
            self.head[c] = 0
            self.tail[c] = 0
            self.count[c]= 0
            
    def enqueue(self, s):
        if not self.full():
            self.count[self.c] += 1
            self.data[self.c][self.tail[self.c]] = s
            self.tail[self.c] = (self.tail[self.c] + 1) % self.size
            self.pushdb()
         
    def dequeue(self):
        if not self.empty():
            self.count[self.c] -= 1
            s = self.data[self.c][self.head[self.c]]
            self.head[self.c] = (self.head[self.c] + 1) % self.size
            return s, self.pushdb()
        
    def full(self):
        return self.size == self.count[self.c]
    
    def empty(self):
        return self.head[self.c] == self.count[self.c]
    
    def find(self, s, f=0):
        i = self.tail[self.c]-1
        while True:
            if i == -1:
                i = self.size-1
            if re.search(s, self.data[self.c][i], f):
                return self.data[self.c][i]
            i -= 1
            if i == self.tail[self.c]-1 or self.data[self.c][i] is None:
                return False

    def fetchdb(self):
        dbc = self.db.cursor()
        try:
            dbc.execute('''SELECT * FROM seddy;''')
            fetch = dbc.fetchone()
            self.data = json.loads(fetch[1])
            self.head = json.loads(fetch[2])
            self.tail = json.loads(fetch[3])
            self.count = json.loads(fetch[4])
        except:
            datajson = json.dumps(self.data)
            datahead = json.dumps(self.head)
            datatail = json.dumps(self.tail)
            datacount= json.dumps(self.count)
            
            dbc.execute('''CREATE TABLE IF NOT EXISTS seddy (size, data blob, head, tail, count);''')
            dbc.execute('''INSERT INTO seddy (size, data, head, tail, count) VALUES (?, ?, ?, ?, ?);'''
                        ,(str(self.size), datajson, datahead, datatail, datacount))
        
    def pushdb(self):
        dbc = self.db.cursor()
        datajson = json.dumps(self.data)
        datahead = json.dumps(self.head)
        datatail = json.dumps(self.tail)
        datacount= json.dumps(self.count)
        dbc.execute('''UPDATE seddy SET data = ? , head = ? , tail = ? , count = ? WHERE size = '48';'''
                    ,(datajson, datahead, datatail, datacount))
                
def seddy(sed, history, parser):
    f = 0
    regex = parser.split(sed)
    if len(regex) < 4:
        return False
    if 'i' in regex[3]:
        f |= re.I
    try:
        msg = history.find(regex[1], f)
    except:
        msg = False
    if msg == False:
        return False
    if "g" in regex[3]:
        try:
            res = re.sub(regex[1], regex[2], msg, flags=f)
        except:
            res = False
    else:
        try:
            res = re.sub(regex[1], regex[2], msg, 1, f)
        except:
            res = False
    return res.replace('\0', re.search(regex[1], msg, f).group(0))
            
def main(cmd, info, db, irc):
    msg = info[2]
    parse_sed  = re.compile('(?<!\\\\)/')
    is_sed     = re.compile('^s/.*/.*')
    parse_sed2 = re.compile('(?<!\\\\),')
    is_sed2    = re.compile('^s,.*,.*')
    history = Queue(48, db[0], info[0], irc)
    history.fetchdb()
    
    if history.full():
        history.dequeue()
    if not is_sed.match(msg) and not is_sed2.match(msg):
        history.enqueue(msg)
        
    if is_sed.match(msg):
        foo = seddy(msg, history, parse_sed)
        if foo != False:
            foo = re.sub('\\\\/', '/', foo)
            if history.full():
                history.dequeue()
            history.enqueue(foo)
            irc.privmsg(info[0], foo)
    elif is_sed2.match(msg):
        foo = seddy(msg, history, parse_sed2)
        if foo != False:
            foo = re.sub('\\\\,', ',', foo)
            if history.full():
                history.dequeue()
            history.enqueue(foo)
            irc.privmsg(info[0], foo)
