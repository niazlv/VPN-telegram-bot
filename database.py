import json
import sqlite3

# users:
#   [
#       *userid*: 
#           [
#               id: id(auto)
#               firstname: str
#               lastname: str
#               birthday: data
#               balance: int
#               isMale: bool 
#               vpn: [vpnid]
#           ]
#   ]
# vpn:
#   [
#       *vpnid*:
#           [
#               protocol: str
#               user: str
#               password: str
#               time_delete: datatime
#           ]
#   ]
class databaseVPN:
    conn = sqlite3.Connection
    cur = sqlite3.Cursor
    def __init__(self):
        print("class databaseVPN is upped")
        self.conn = sqlite3.connect("./databaseVPN.db")
        self.cur = self.conn.cursor()
        self.cur.execute(""" CREATE TABLE IF NOT EXISTS 'Users' (
                        'id' INTEGER PRIMARY KEY AUTOINCREMENT,
                        'userid' VARCHAR(45) NOT NULL,
                        'firstname' VARCHAR(45) NULL,
                        'lastname' VARCHAR(45) NULL,
                        'birthday' DATETIME NULL,
                        'balance' INT NOT NULL DEFAULT 0,
                        'isMale' TINYINT NOT NULL DEFAULT 1,
                        'vpnids' JSON NOT NULL DEFAULT '{}');
        """)
        self.cur.execute(""" CREATE TABLE IF NOT EXISTS 'vpns' (
                        'vpnid' INTEGER PRIMARY KEY UNIQUE,
                        'protocol' VARCHAR(100) NOT NULL,
                        'user' VARCHAR(45) NOT NULL,
                        'password' VARCHAR(45) NOT NULL,
                        'time_delete' DATETIME NOT NULL);
        """)
        self.conn.commit()
    def addUser(self,userid:str,vpnids:dict[str,any],firstname:str=None,lastname:str=None,birthday="01.01.1970",balance:int=0,isMale:bool=True):
        #self.cur = self.conn.cursor()
        print(str(vpnids))
        user = (userid,firstname,lastname,balance,isMale,str(vpnids))
        self.cur.execute("INSERT INTO users(userid, firstname, lastname, balance, isMale, vpnids) VALUES(?, ?, ?, ?, ?, ?);", user)
        self.conn.commit()

db = databaseVPN()
db.addUser(1234,{"test":["1234",'12456','5363w3']})