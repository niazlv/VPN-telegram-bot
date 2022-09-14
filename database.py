import datetime
import json
import sqlite3
from xmlrpc.client import Boolean

from vpnconfig import ip

# users:
#   [
#       *userid*: 
#           [
#               id: id(auto)
#               firstname: str
#               lastname: str
#               birthday: date
#               created_on: datetime
#               updated_on: datetime
#               balance: int
#               isMale: bool 
#               vpn: [vpnid]
#           ]
#   ]
# vpn:
#   [
#       *vpnid*:
#           [
#               server: str
#               protocol: str
#               user: str
#               password: str
#               time_delete: datatime
#           ]
#   ]

#полезная статья https://www.techonthenet.com/sqlite/tables/alter_table.php

class databaseVPN:
    conn = sqlite3.Connection
    cur = sqlite3.Cursor
    def __init__(self):
        print("class databaseVPN is upped")
        self.conn = sqlite3.connect("./databaseVPN.db",check_same_thread=False)
        self.cur = self.conn.cursor()
        self.cur.execute(r""" CREATE TABLE IF NOT EXISTS 'Users' (
                        'id' INTEGER PRIMARY KEY AUTOINCREMENT,
                        'userid' VARCHAR(45) NOT NULL,
                        'firstname' VARCHAR(45) NULL,
                        'lastname' VARCHAR(45) NULL,
                        'birthday' DATETIME NULL,
                        'created_on' DATETIME NOW,
                        'updated_on' DATETIME,
                        'balance' INT NOT NULL DEFAULT 0,
                        'isMale' TINYINT NOT NULL DEFAULT 1,
                        'vpnids' JSON NOT NULL DEFAULT '{}',
                        'ammount' INT NOT NULL DEFAULT 1);
        """)
        self.cur.execute(r""" CREATE TABLE IF NOT EXISTS 'vpns' (
                        'vpnid' INTEGER PRIMARY KEY AUTOINCREMENT,
                        'server' VARCHAR(100) NOT NULL,
                        'protocol' VARCHAR(100) NOT NULL,
                        'user' VARCHAR(45) NOT NULL,
                        'password' VARCHAR(45) NOT NULL,
                        'time_delete' DATETIME NOT NULL,
                        'status' JSON NOT NULL DEFAULT '{"status": {"value": 1, "description": "auto added by creating"}}');
        """)
        self.conn.commit()
    def addUser(self,userid:str,vpnids:dict[str,any],firstname:str=None,lastname:str=None,birthday:datetime=datetime.date(1970,1,1).strftime('%Y-%m-%d %H:%M:%S'),balance:int=0,isMale:bool=True):
        """Place data about user to database"""
        #self.cur = self.conn.cursor()
        created_on = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_on = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = (userid,firstname,lastname,balance,isMale,str(vpnids),birthday, created_on, updated_on)
        self.cur.execute("INSERT INTO users(userid, firstname, lastname, balance, isMale, vpnids, birthday, created_on, updated_on) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);", user)
        self.conn.commit()
    
    def getUser(self, type:str ,data:any)->list:
        return self.cur.execute("SELECT * FROM users WHERE "+type+" = ?;",(str(data),)).fetchall()
    
    def addVpn(self, protocol:str, user:str, password:str, ip:str=ip, time_delete:datetime=datetime.date(2029,1,1).strftime('%Y-%m-%d %H:%M:%S'))->int:
        "return added id"
        data = (protocol,user,password,time_delete,ip)
        self.cur.execute("INSERT INTO vpns(protocol, user, password, time_delete, server) VALUES(?, ?, ?, ?, ?);",data)
        self.conn.commit()
        return self.cur.execute("SELECT last_insert_rowid()").fetchall()[0][0]

    def getVpn(self, vpnid:int)->list:
        return self.cur.execute("SELECT * FROM vpns WHERE vpnid = ?",(vpnid,)).fetchall()
    
    def execute(self, command:str, isUpdated:Boolean=False)->list:
        """EXECUTE any sqlite3 code
        Return self.cursor.execute(command).fetchall()"""
        data = self.cur.execute(command).fetchall()
        self.conn.commit()
        return data

    def updateUser(self,userid:str,type:str,_data:str):
        updated_on = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = (updated_on,_data, userid)
        self.cur.execute("UPDATE Users SET updated_on = ?, "+type+" = ? WHERE userid = ?;",data)
        self.conn.commit()

    def updateVpn(self,vpnid:str,type:str,_data:str):
        data = (_data, vpnid)
        self.cur.execute("UPDATE vpns SET "+type+" = ? WHERE vpnid = ?;",data)
        self.conn.commit()