import sys
import os
import json
import uuid
from Queue import *

class Chat:
    def __init__(self):
        self.sessions = {}
        self.users = {}
        self.groups = {}
        self.users['messi'] = { 'nama': 'Lionel Messi', 'negara': 'Argentina', 'password': 'surabaya', 'incoming' : {}, 'outgoing': {} }
        self.users['henderson'] = { 'nama': 'Jordan Henderson', 'negara': 'Inggris', 'password': 'surabaya', 'incoming': {}, 'outgoing': {} }
        self.users['lineker'] = { 'nama': 'Gary Lineker', 'negara': 'Inggris', 'password': 'surabaya','incoming': {}, 'outgoing':{}}
        self.users['darke'] = { 'nama': 'Darke Foster', 'negara': 'Canada', 'password': 'prototype', 'incoming' : {}, 'outgoing': {} }
        
    def proses(self, data):
        j = data.split(" ")
        try:
            command = j[0].strip()
            if (command == 'auth'):
                username = j[1].strip()
                password = j[2].strip()
                print "Authenticating {}" . format(username)
                return self.autentikasi_user(username,password)
            elif (command == 'send'):
                sessionid = j[1].strip()
                usernameto = j[2].strip()
                message = ""
                for w in j[3:]:
                    message = "{} {}" .format(message, w)
                usernamefrom = self.sessions[sessionid]['username']
                print "send message from {} to {}" . format(usernamefrom, usernameto)
                return self.send_message(sessionid, usernamefrom, usernameto, message)
            elif (command == 'inbox'):
                sessionid = j[1].strip()
                username = self.sessions[sessionid]['username']
                print "inbox {}" . format(sessionid)
                return self.get_inbox(username)
            elif (command == 'logout'):
                sessionid = j[1].strip()
                print "Logouting {}" . format(self.sessions[sessionid]['username'])
                if(sessionid in self.sessions):
                    del self.sessions[sessionid]                
                return {'status' : 'OK'}
            elif (command == 'create_group'):                
                group = j[1].strip()
                sessionid = j[2].strip()
                print "creating group {}" . format(group)
                return self.create_group(group, sessionid)
            elif (command == 'list_group'):
                print "list group"
                return self.list_group()
            elif (command =='list_mygroup'):                
                sessionid = j[1].strip()
                username = self.sessions[sessionid]['username']
                print "{}'s group list".format(username)
                return self.list_mygroup(username)
            elif (command =='join_group'):
                group = j[1].strip()
                sessionid = j[2].strip()
                print "{} Joins group {}".format(self.sessions[sessionid]['username'], group)
                return self.join_group(group, sessionid)
            elif (command =='leave_group'):
                group = j[1].strip()
                sessionid = j[2].strip()
                print "{} leaves group {}".format(self.sessions[sessionid]['username'], group)
                return self.leave_group(group, sessionid)
            elif (command == 'send_group'):
                sessionid = j[1].strip()
                groupto = j[2].strip()
                message = ""
                for w in j[3:]:
                    message = "{} {}" .format(message, w)
                usernamefrom = self.sessions[sessionid]['username']
                print "send message from {} to group {}" . format(usernamefrom, groupto)
                return self.send_group(sessionid, usernamefrom, groupto, message)
            elif (command == 'inbox_group'):
                group = j[1].strip()
                sessionid = j[2].strip()
                username = self.sessions[sessionid]['username']
                print "Inbox group {}".format(group)
                return self.inbox_group(group, username)
            else:
                return {'status' : 'ERROR', 'message' : '**Protocol Tidak Benar'}
        except IndexError:
            return {'status' : 'ERROR', 'message' : '--Protocol Tidak Benar'}
    
    def autentikasi_user(self, username, password):
        if(username not in self.users):
            return {'status' : 'ERROR', 'message' : 'User Tidak Ada'}
        if(self.users[username]['password'] != password):
            return {'status' : 'ERROR', 'message' : 'Password Salah'}
        tokenid = str(uuid.uuid4())
        self.sessions[tokenid] = { 'username' : username, 'userdetail' : self.users[username]}
        return {'status' : 'OK', 'tokenid' : tokenid}
    
    def get_user(self, username):
        if(username not in self.users):
            return False
        return self.users[username]
    
    def get_group(self, groupname):
        if(groupname not in self.groups):
            return False
        return self.groups[groupname]
    
    def send_message(self, sessionid, username_from, username_dest, message):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        s_fr = self.get_user(username_from)
        s_to = self.get_user(username_dest)
        
        if (s_fr == False or s_to == False):
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}
        message = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': message }
        outqueue_sender = s_fr['outgoing']
        inqueue_receiver = s_to['incoming']
        try:
            outqueue_sender[username_from].put(message)
        except KeyError:
            outqueue_sender[username_from] = Queue()
            outqueue_sender[username_from].put(message)
        try:
            inqueue_receiver[username_from].put(message)
        except KeyError:
            inqueue_receiver[username_from] = Queue()
            inqueue_receiver[username_from].put(message)
        return {'status': 'OK', 'message': 'Message Sent'}

    def get_inbox(self, username):
        s_fr = self.get_user(username)
        incoming = s_fr['incoming']
        msgs = {}
        for users in incoming:
            msgs[users] = []
            while not incoming[users].empty():
                msgs[users].append(s_fr['incoming'][users].get_nowait())
        return {'status': 'OK', 'messages': msgs}
    
    def create_group(self, group, sessionid):
        if(group in self.groups):
            return {'status': 'ERROR', 'message': 'Group sudah ada'}
        else:
            self.groups[group] = { 'nama' : group, 'messages': [], 'members': []}
            #autojoin
            autolog = self.sessions[sessionid]['username']
            self.groups[group]['members'].append(autolog)
            return {'status': 'OK', 'message': self.groups[group]}
    
    def list_group(self):
        msgs = []
        for k in self.groups:
            msgs.append(self.groups[k]['nama'])
        return {'status': 'OK', 'messages': msgs}  
    
    def list_mygroup(self, username):
        msgs = []         
        for k in self.groups:
             if (username in self.groups[k]['members']):
                 msgs.append(self.groups[k]['nama'])
        return {'status': 'OK', 'messages': msgs}  
    
    def join_group(self, group, sessionid):
        if(group not in self.groups):
            return {'status': 'ERROR', 'message': 'Group tidak ada'}
        else:
            username = username = self.sessions[sessionid]['username']
            if (username in self.groups[group]['members']):
                return {'status': 'ERROR', 'message': 'Anda sudah menjadi bagian dari group'}
            else:
                self.groups[group]['members'].append(username)
                return {'status': 'OK', 'message': self.groups[group]}
    
    def leave_group(self, group, sessionid):
        if(group not in self.groups):
            return {'status': 'ERROR', 'message': 'Group tidak ada'}
        else:
            username = username = self.sessions[sessionid]['username']
            if (username not in self.groups[group]['members']):
                return {'status': 'ERROR', 'message': 'Anda bukan member group ini'}
            else:
                self.groups[group]['members'].remove(username)
                return {'status': 'OK', 'message': self.groups[group]}
            
    def send_group(self, sessionid, username_from, group_dest, message):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        s_to = self.get_group(group_dest)
        
        #grupnya gak ada
        if (s_to == False):
            return {'status': 'ERROR', 'message': 'User atau Group Tidak Ditemukan'}
        #gakmasuk grup
        if (username_from not in self.groups[group_dest]['members']):
            return {'status': 'ERROR', 'message': 'Anda bukan member group ini'}
        
        messages = { 'from': username_from, 'msg': message }
        self.groups[group_dest]['messages'].append(messages)
        return {'status': 'OK', 'message': 'Message Sent'}
    
    def inbox_group(self, group, username):
        if(group not in self.groups):
            return {'status': 'ERROR', 'message': 'Group tidak ada'}
        if(username not in self.groups[group]['members']):
            return {'status': 'ERROR', 'message': 'Anda bukan bagian dari grup'}
        msgs = []
        for k in self.groups[group]['messages']:
            msgs.append(k)
        return {'status': 'OK', 'messages': msgs}  
if __name__=="__main__":
    j = Chat()
    sesi = j.proses("auth messi surabaya")
    print sesi
    #sesi = j.autentikasi_user('messi','surabaya')
    #print sesi
    tokenid = sesi['tokenid']
    print j.proses("send {} henderson hello gimana kabarnya son " . format(tokenid))
    #print j.send_message(tokenid,'messi','henderson','hello son')
    #print j.send_message(tokenid,'henderson','messi','hello si')
    #print j.send_message(tokenid,'lineker','messi','hello si dari lineker')
    
    print j.get_inbox('messi')
    