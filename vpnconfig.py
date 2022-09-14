import datetime
import imp
import os
import subprocess

from config import ip

i2tp = "/etc/ppp/chap-secrets"
x_auth = "/etc/ipsec.d/passwd"  #openssl passwd -1 "passwd"
psk = "/etc/ipsec.secrets"


#open UDP ports 500 and 4500 for the VPN

def restartServices()->int:
    services = ['ipsec','xl2tpd']
    for i in services:
        subprocess.Popen(['service',i,'restart'])
    return 0

def read(src:str)->list[str]:
    data = []
    try:
        with open(src, 'r') as f:
            data = f.read().splitlines()
    except Exception as e:
        print(e)
    return data

def write(data:list[str],src:str)->int:
    try:
        with open(src,"w") as f:
            for i in range(0,len(data)):
                f.write(data[i]+'\n')
    except Exception as e:
        print(e)
        return -1
    os.chmod(src,600)
    return 0

def appendfile(data,src:str)->int:
    try:
        with open(src,'r+') as f:
            r = f.read().splitlines()
            f.write(str(data)+'\n')
    except Exception as e:
        print(e)
        return -1
    os.chmod(src,600)
    return 0

def create(data:list[str],dst:str)->int:
    """This function uses not secure os function.
    Because of this, it requires DST with file(not directory) as at example:
        /etc/ppp/chap-secrets
    NOT THIS:
        /etc/ppp

        /
    """
    try:
        paths = dst[:dst.rfind('/')]
        if(not os.path.exists(paths)):
            os.makedirs(paths)
        return write(data,dst)
    except Exception as e:
        print(e)
        return -1
    return 0

def backup(src:str,dst:str)->int:
    data = read(src)
    if(len(data)<=0):
        return -1
    created = create(data,dst)
    if(not created == 0):
        return -2
    return 0

def autobackup(src:str)->str:
    date = datetime.datetime.now().strftime("%d%m%y%H%M")
    if(not src[0] == '/'):
        src = "/" + src
    dst = './backups/byDays/'+datetime.datetime.now().strftime('%d%m%y')+src+"_"+date+".backup"
    if(src == i2tp): 
        dst = './backups/ppp/chap-secrets_'+date+'.backup'
    if(src == x_auth):
        dst = './backups/ipsec.d/passwd_'+date+'.backup'
    result = backup(src,dst)
    if(not result == 0):
        return ""
    return dst

def restorefile(src:str,dst:str)->int:
    readed = read(src)
    if(readed <= 0):
        return -1
    return write(readed,dst)

def removeuser(user,src:str)->int:
    """find and remove user from file.
    if user not found, function return 404 code
    """
    data = str(user)
    readed = read(src)
    if(len(readed) <= 0):
        return -2
    backuped = autobackup(src)
    try:
        for i in range(0,len(readed)):
            if(not readed[i].find(data)==-1):
                readed.remove(readed[i])
                result = write(readed,src)
                if(not result == 0):
                    raise Exception("create function is wrong! Error code: "+str(result))
                return 0
    except Exception as e:
        print(e)
        print("edited file exception: "+src)
        print("backup is here---> "+backuped)
        print("try restore file...")
        result = restorefile(backuped,src)
        if(result == 0):
            print("restore successful!")
        else:
            print("file not restored. Now try restore manually")
        return -1
    return 404

def adduser(user:str,password:str,src:str,type:str)->int:
    """type it is protocol type.
    
    type = i2tp
        it is a /etc/ppp/chap-secrets
    type = x-auth
        it is a /etc/ipsec.d/passwd
    """
    backuped = autobackup(src)
    if(type == "i2tp"):
        #need make string like this: "admin" i2tpd "password" *

        data = '"'+user+'" i2tpd "'+password+'" *'
        result = removeuser(user,src)
        return appendfile(data,src)
    elif(type == "x-auth"):
        #make system call
        passwdhash = subprocess.Popen(["openssl","passwd","-1",password],stdout=subprocess.PIPE).stdout.readlines()[0]
        passwdhash = str(passwdhash)[2:len(passwdhash)+1]
        if(not len(passwdhash) == 34):
            return -2
        #need make string like this: username:passwordhashed:xauth-psk
        data = user+':'+passwdhash+':xauth-psk'
        result = removeuser(user,src)
        return appendfile(data,src)

    else:
        print("not allowed! Rewrite the source code! Function adduser")
        return -1
    return 0

def autoadduser(user:str,password:str)->int:
    """NOT RECOMENDED USE THIS FUNCTION. 
    Be careful. Remember that i2tp and x_auth variables must be actual.
    """
    result = adduser(user=user,password=password,src=i2tp,type="i2tp")
    if(not result == 0):
        print("ERROR: i2tp user not added")
        return result
    result = adduser(user=user,password=password,src=x_auth,type="x-auth")
    if(not result == 0):
        print("ERROR: x-auth user not added")
        return result
    restartServices()
    return 0

def autodeluser(user:str)->int:
    """NOT RECOMENDED USE THIS FUNCTION. 
    Be careful. Remember that i2tp and x_auth variables must be actual.
    """
    result = removeuser(user=user,src=i2tp)
    if(not result == 0):
        print("ERROR: i2tp user not deleted")
        return result
    result = removeuser(user=user,src=x_auth)
    if(not result == 0):
        print("ERROR: x-auth user not deleted")
        return result
    restartServices()
    return 0

def getPSK(src:str=psk)->str:
    """Return PSK"""
    data = read(src)[0]
    if(len(data)<=0):
        return ""
    data = data[data.find("PSK")+5:data.rfind('"')]
    return data

def setPSK(_PSK,src:str=psk)->int:
    """set your psk"""
    backuped = autobackup(src)
    data = '%%any  %%any  : PSK "'+_PSK+'"'
    result = write([data],src)
    restartServices()
    return result
    