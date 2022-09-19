import datetime
import json
from os import times_result
import random
import secrets
import string
import subprocess
import threading
import time
import telebot
from telebot import types
from pytils import numeral

import vpnconfig
import database
import config


bot = telebot.TeleBot(config.token)
db = database.databaseVPN()
user_data = {}
data = [b'',b'']
isReal_payment = True
hide_admin = False

def is_digit(string):
    if string.isdigit():
       return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False

def get_price(hour:int):
    start_fee = config.price * 0.03 #3% от суммы
    if(hour <=720):
        fee = start_fee - ((start_fee/720)*hour)
    else:
        fee = 0
    return str(round(((config.price/720)*hour)+fee,1))

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.InlineKeyboardMarkup()
    item1=types.InlineKeyboardButton(text="Начать!",callback_data="start")
    markup.add(item1)
    bot.send_message(message.chat.id,
                    "Привет ✌️\n"
                    "Я предоставляю VPN сервисы за маленькую стоимость(просто поддержание работы сервиса и оплату хостинга)."
                    ,reply_markup=markup)

@bot.message_handler(commands=['menu'])
def menu_message(message):
    resp = db.getUser("userid",message.chat.id)
    if(len(resp)<=0):
        class XClass(object):
            def __init__(self):
                self.message = message
                self.data = 'start#'
    else:
        msg = bot.send_message(message.chat.id,"*menu*")
        class XClass(object):
            def __init__(self):
                self.message = msg
                self.data = 'main#'
    callback_inline(XClass())

@bot.message_handler(commands=['adminbal'])
def adminbal_message(message):
    if(str(message.chat.id) == str(config.admin_id)):
        message.text.split(" ")[1]

@bot.message_handler(commands=['sql'])
def sql_message(message):
    if(str(message.chat.id) == str(config.admin_id)):
        bot.send_message(message.chat.id,"sql:\n{}".format(db.execute(message.text[5:])))

@bot.message_handler(commands=['hideadmin'])
def hideadmin_message(message):
    global hide_admin
    if(str(message.chat.id) == str(config.admin_id)):
        lst = hide_admin
        hide_admin = not hide_admin
        bot.send_message(message.chat.id,"hide_admin {} -> {}".format(lst,hide_admin))

@bot.message_handler(commands=['exec'])
def exec_message(message):
    if(str(message.chat.id) == str(config.admin_id)):
        st = subprocess.Popen([message.text[6:]],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
        bot.send_message(message.chat.id,"{}\n\n{}".format(st[0].decode("utf-8"),st[1].decode("utf-8")))

@bot.message_handler(commands=['refill_balance'])
def refill_balance_message(message):
    resp = db.getUser("userid",message.chat.id)
    if(len(resp)<=0):
        class XClass(object):
            def __init__(self):
                self.message = message
                self.data = 'start#'
    else:
        #msg = bot.send_message(message.chat.id,"*refill_balance*")
        class XClass(object):
            def __init__(self):
                self.message = message
                self.data = 'refill#'
    callback_inline(XClass())

@bot.message_handler(commands=['account'])
def refill_balance_message(message):
    resp = db.getUser("userid",message.chat.id)
    if(len(resp)<=0):
        class XClass(object):
            def __init__(self):
                self.message = message
                self.data = 'start'
    else:
        msg = bot.send_message(message.chat.id,"*account*")
        class XClass(object):
            def __init__(self):
                self.message = msg
                self.data = 'account#'
    callback_inline(XClass())

@bot.message_handler(commands=['vpn'])
def vpn_message(message):
    resp = db.getUser("userid",message.chat.id)
    if(len(resp)<=0):
        class XClass(object):
            def __init__(self):
                self.message = message
                self.data = 'start'
    else:
        msg = bot.send_message(message.chat.id,"*vpn*")
        class XClass(object):
            def __init__(self):
                self.message = msg
                self.data = 'vpn'
    callback_inline(XClass())

def getvpnstr(userid:str, detalizated=False)->str:
    result = ""
    try:
        # получить точную активацию
        # vpns = db.execute("SELECT time_delete, user, vpnid, status FROM vpns WHERE userid = "+userid)
        # _json = json.loads(vpns[0][3])
        # _json['status']['value']
        # _json['status']['description']
        data = db.getUser("userid",userid)[0]
        jsonfromdata = json.loads(data[9])
        for i in range(0,len(jsonfromdata['vpnid'])):
            vpns = db.getVpn(jsonfromdata['vpnid'][i])[0]
            result += str(i+1)+".\t\tlogin: "+vpns[3]
            if(detalizated):
                result += "\n\t\tpasswd: "+vpns[4]
                result += "\n\t\tserver/ip: "+vpns[1]
                result += "\n\t\tprotocol: "+vpns[2]
                result += "\n\t\tPSK: "+vpnconfig.getPSK()
            _datedelta = datetime.datetime.now() - datetime.datetime.strptime(vpns[5],('%Y-%m-%d %H:%M:%S'))
            _strdate = (numeral.get_plural((_datedelta.days*-1), "день, дня, дней")) if _datedelta < datetime.timedelta(seconds=1) else "Expired"
            # result += "\n\t\tdestruction time: "+vpns[5]+"("+_strdate+")"
            result += "\n\t\tdestruction time: "+_strdate
            result += "\n\n"
    except Exception as e:
        print(e)
    return result

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global data
    markup = types.InlineKeyboardMarkup()
    account_btn=types.InlineKeyboardButton(text="Личный кабинет",callback_data="account")
    vpn_btn=types.InlineKeyboardButton(text="VPN",callback_data="vpn")
    destroy_btn = types.InlineKeyboardButton(text="Закрыть",callback_data="destroy")
    main_btn = types.InlineKeyboardButton(text="В главное меню",callback_data="main")
    refill_btn = types.InlineKeyboardButton(text="Пополнить баланс", callback_data="refill")
    detalizated_vpns_btn = types.InlineKeyboardButton(text="Подробные данные", callback_data="detalizated_account")
    menu_admin = types.InlineKeyboardButton(text="ADMIN PANEL",callback_data="admin")
    # Если сообщение из чата с ботом
    if call.message:
        if call.data[:5] == "start":
            resp = db.getUser("userid",call.message.chat.id)
            if(len(resp)<=0):
                if(not call.data[5:6] == "#"):
                    bot.answer_callback_query(call.id)
                BTNmarkup = types.ReplyKeyboardMarkup(True)
                item1=types.KeyboardButton("Принять")
                BTNmarkup.add(item1)
                msg = bot.send_message(call.message.chat.id,"бла бла бла. Что-то про лицензию. \nПродолжая пользоваться приложением, вы соглашаетесь с обработкой персональных данных.\nбла бла бла, для продолжения напишите \"Прининимаю\" либо нажмите на кнопку \"Принять\"",reply_markup=BTNmarkup)
                bot.register_next_step_handler(msg, after_start)
            else:
                call.data = "main start"
        if call.data[:4] == "main":
            if(call.data == "main"):
                bot.answer_callback_query(call.id)
            markup.add(refill_btn,account_btn)
            markup.add(vpn_btn)
            if(str(call.message.chat.id) == str(config.admin_id) and not hide_admin):
                markup.add(menu_admin)
            #markup.add(destroy_btn)
            text = "Вы в главном меню!\nОтсюда вы можете попасть в любое из подменю бота!"
            if(call.data == "main start"):
                bot.send_message(call.message.chat.id,text,reply_markup=markup)
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,reply_markup=markup)
        
        if call.data == "admin":
            if(str(call.message.chat.id) == str(config.admin_id)):
                markup.add(main_btn)
                bot.send_message(call.message.chat.id,"Вы в админ панели!\n/adminbal - NOTHING\n/sql - SQL EXECUTE",reply_markup=markup)

        if call.data[:7] == "account":
            if not call.data[7:8] == "#":
                bot.answer_callback_query(call.id)
            edit_btn = types.InlineKeyboardButton(text="Изменить",callback_data="edit")
            ikev2_get_btn = types.InlineKeyboardButton(text="Мои IKEv2(beta)",callback_data="get_vpn_ikev2")
            markup.add(edit_btn,detalizated_vpns_btn)
            markup.add(ikev2_get_btn)
            markup.add(main_btn)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                text="Вы - '"+str(call.message.chat.id)+"'\n"
                "Ваш баланс - "+str(db.getUser("userid",call.message.chat.id)[0][7]/10)+"₽\n"
                "Текушие активные аккаунты: \n"
                ""+getvpnstr(call.message.chat.id),reply_markup=markup)
        
        if call.data == "detalizated_account":
            bot.answer_callback_query(call.id)
            edit_btn = types.InlineKeyboardButton(text="Изменить",callback_data="edit")
            markup.add(edit_btn)
            markup.add(main_btn)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                text="Вы - '"+str(call.message.chat.id)+"'\n"
                "Ваш баланс - "+str(db.getUser("userid",call.message.chat.id)[0][7]/10)+"₽\n"
                "Текушие активные аккаунты: \n"
                ""+getvpnstr(call.message.chat.id,True),reply_markup=markup)

        if call.data == "edit":
            bot.answer_callback_query(call.id)
            BTNmarkup = types.ReplyKeyboardMarkup(True,True)
            #BTNmarkup.row("Профиль","VPN")
            BTNmarkup.add("VPN")
            BTNmarkup.add("Выйти")
            msg = bot.send_message(call.message.chat.id,"Давайте определимся, что вы хотите изменить:",reply_markup=BTNmarkup)
            bot.register_next_step_handler(msg,after_edit)

        if call.data == "vpn":
            #if not (call.data[3:4] == '#'):
            #    bot.answer_callback_query(call.id)
            item1 = types.InlineKeyboardButton(text="Создать(IPSec Xauth PSK)", callback_data="create_vpn")
            ikev2_create_btn = types.InlineKeyboardButton(text="IKEv2(сертификат)", callback_data="vpn_ikev2")
            whichbetter_btn = types.InlineKeyboardButton(text="Что выбрать?", callback_data='whichisbetter')
            item2 = types.InlineKeyboardButton(text="Мои VPN", callback_data="detalizated_account")
            markup.add(item1,item2)
            markup.add(ikev2_create_btn)
            markup.add(whichbetter_btn, main_btn)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите интересующие варианты:",reply_markup=markup)
        if call.data[:10] == "create_vpn":
            if(not call.data[10:11] == "#"):
                bot.answer_callback_query(call.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Я вас понял!")
            markup.add(main_btn)

            
            _user = db.getUser("userid",str(call.message.chat.id))[0]
            _json = json.loads(_user[9])
            _ammount = db.cur.execute("SELECT ammount FROM users WHERE userid = ?",(call.message.chat.id,)).fetchall()[0][0]
            description = "Слишком большого количества vpn(у вас "+str(len(_json['vpnid']))+"). Пожалуйста перейдите в личный кабинет и воспользуйтесь существующими vpn\n\nЛибо купите новый"
            if(len(_json["vpnid"])<int(_ammount)):
                alphabet = string.ascii_letters + string.digits
                #creditals
                #user = str(call.message.chat.id)
                user = str(call.message.chat.id)+''.join(secrets.choice(string.digits) for i in range(10))
                password = ''.join(secrets.choice(alphabet) for i in range(20))  # for a 20-character password
                # protocol = "'IPSec Xauth PSK' / 'L2TP/IPSec PSK'"
                protocol = "'IPSec Xauth PSK'"
                _ip = vpnconfig.ip
                _time = datetime.datetime.now()+datetime.timedelta(hours=config.trialHours)
                #db
                id = db.addVpn(protocol,user,password,vpnconfig.ip,_time.strftime('%Y-%m-%d %H:%M:%S'))
                _json["vpnid"].append(id)
                db.updateUser(str(call.message.chat.id),"vpnids",str(json.dumps(_json)))
                #create vpn user
                vpnconfig.autoadduser(user,password)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=""
                    "Ваши данные: \n"
                    "\ttype protocol: "+protocol+"\n"
                    "\tip: "+_ip+"\n"
                    "\tlogin: "+user+"\n"
                    "\tpassword: "+password+"\n"
                    "\tPSK(pre-shared key): "+ vpnconfig.getPSK()+"\n"
                    ,reply_markup=markup)
            else:
                markup.add(types.InlineKeyboardButton(text="Личный кабинет",callback_data="account"))
                markup.add(types.InlineKeyboardButton(text="Купить", callback_data="buy ammount"))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=""
                "Извините, но мы не можем выдать вам vpn по причине: "+description
                ,reply_markup=markup)
        if call.data[:3] == "buy":
            BTNmarkup = types.ReplyKeyboardMarkup(True)
            BTNmarkup.row("Да","Нет")
            if(call.data[4:] == "ammount"):
                msg = bot.send_message(call.message.chat.id,"вы хотите купить слот впн за {}₽?".format(config.price_slot),reply_markup=BTNmarkup)
                bot.register_next_step_handler(msg,after_buy_ammount)
        if call.data == "destroy":
            bot.answer_callback_query(call.id)
            bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
        #продление vpn
        if call.data[:11] == "vpn_renewal":
            _ide = call.data[11:12]
            isFirst = _ide == "#"
            _ide = " " if _ide == "." else "."
            time = int(call.data[12:])
            if(time <24):
                time = 24
            #inc_btn = types.InlineKeyboardButton(text="+1час",callback_data="vpn_renewal"+_ide+str(time+1))
            #dec_btn = types.InlineKeyboardButton(text="-1час", callback_data="vpn_renewal"+_ide+str(time-1))
            inc10_btn = types.InlineKeyboardButton(text="+1день",callback_data="vpn_renewal"+_ide+str(time+24))
            dec10_btn = types.InlineKeyboardButton(text="-1день", callback_data="vpn_renewal"+_ide+str(time-24))
            inc30_btn = types.InlineKeyboardButton(text="+30дней",callback_data="vpn_renewal"+_ide+str(time+720))
            dec30_btn = types.InlineKeyboardButton(text="-30дней", callback_data="vpn_renewal"+_ide+str(time-720))
            done_btn = types.InlineKeyboardButton(text="Готово!", callback_data="vpn_rendone")
            if(time == 1):
                #dec_btn = types.InlineKeyboardButton(text="-1час",callback_data="vpn_renewal"+_ide+str(time))
                dec10_btn = types.InlineKeyboardButton(text="-1день", callback_data="vpn_renewal"+_ide+str(time))
                dec30_btn = types.InlineKeyboardButton(text="-30дней", callback_data="vpn_renewal"+_ide+str(time))
            #markup.add(inc_btn,dec_btn)
            markup.add(inc10_btn,dec10_btn)
            markup.add(inc30_btn,dec30_btn)
            markup.add(done_btn)
            days = ""
            hours = ""+numeral.get_plural(int(time%24), "час, часа, часов")
            if(time%24 == 0):
                hours = ""
            if(time >= 24):
                days = ""+numeral.get_plural(int(time//24), "день, дня, дней")
            _data = ""+days+" "+hours+"\nЦена: "+get_price(time)+"₽"
            user_data[call.message.chat.id]['buy']['price'] = get_price(time)
            user_data[call.message.chat.id]['buy']['extension']={}
            user_data[call.message.chat.id]['buy']['extension']['raw'] = time
            user_data[call.message.chat.id]['buy']['extension']['value'] = days+" "+hours
            bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text='{}'.format(_data),reply_markup=markup)
            if not isFirst:
                bot.answer_callback_query(call.id)
        if call.data[:11] == "vpn_rendone":
            if call.data == "vpn_rendone":
                try:
                    yes_btn = types.InlineKeyboardButton(text="Да",callback_data="vpn_rendone yes")
                    no_btn = types.InlineKeyboardButton(text="Нет",callback_data="vpn_rendone no")
                    markup.add(yes_btn,no_btn)
                    #data = "userid="+str(call.message.chat.id)+"&vpnid="+str(user_data[call.message.chat.id]['buy']['vpnid'])+"&price="+str(user_data[call.message.chat.id]['buy']['price'])+"&extension="+str(user_data[call.message.chat.id]['buy']['extension']['raw'])
                    bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=""+user_data[call.message.chat.id]['buy']['price']+"₽")
                    bot.send_message(call.message.chat.id,
                        "Вы хотите продлить vpn на "+user_data[call.message.chat.id]['buy']['extension']['value']+"?\n"
                        "С вашего баланса будет списано "+user_data[call.message.chat.id]['buy']['price']+"₽"
                        ,reply_markup=markup
                    )
                    #bot.send_message(call.message.chat.id,'{}'.format(data))
                except IndexError as e:
                    bot.send_message(call.message.chat.id,"Сессия устарела, попробуйте заново.")
            else:
                if call.data[12:] == "yes":
                    try:
                        balance = int(db.getUser("userid",call.message.chat.id)[0][7])
                        print(balance)
                        if(balance - int(float(user_data[call.message.chat.id]['buy']['price'])*10) >=0):
                            db.updateUser(call.message.chat.id,"balance",balance-(int(float(user_data[call.message.chat.id]['buy']['price'])*10)))
                            vpn = db.getVpn(int(user_data[call.message.chat.id]['buy']['vpnid']))[0]
                            vpndate = datetime.datetime.strptime(vpn[5],('%Y-%m-%d %H:%M:%S'))
                            dateToSet = datetime.datetime.now()
                            if(vpndate< datetime.datetime.now()):
                                print("Время окончено\nновый отсчёт")
                                dateToSet = datetime.datetime.now() + datetime.timedelta(hours=int(user_data[call.message.chat.id]['buy']['extension']['raw']))
                                result = vpnconfig.autoadduser(vpn[3],vpn[4])
                                if(not result == 0):
                                    bot.send_message(call.message.chat.id, "Произошла ошибка при активации впн, пожалуйста обратитесь к администрации и перешлите ему это сообщение\n"+"result={},vpnid={},hash={},message.chat.id={}\ncanary=v0.1&(&^&re#hbjebfw&#9hvure".format(result,str(user_data[call.message.chat.id]['buy']['vpnid']),hash(vpn),call.message.chat.id))
                            else:
                                dateToSet = vpndate + datetime.timedelta(hours=int(user_data[call.message.chat.id]['buy']['extension']['raw']))
                            print("новое время: "+str(dateToSet))
                            db.updateVpn(str(user_data[call.message.chat.id]['buy']['vpnid']),"time_delete",dateToSet.strftime('%Y-%m-%d %H:%M:%S'))
                            markup.add(main_btn)
                            bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="VPN продлён!",reply_markup=markup)
                        else:
                            refill_btn = types.InlineKeyboardButton(text="Пополнить баланс", callback_data="refill "+int(float(user_data[call.message.chat.id]['buy']['price'])*10))
                            markup.add(refill_btn)
                            markup.add(main_btn)
                            bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="Недостаточно средств на балансе!",reply_markup=markup)
                    except Exception as e:
                        print(e)
                        bot.send_message(call.message.chat.id,"Что-то сломалося. Попробуйте позже")
                    bot.answer_callback_query(call.id)
                if call.data[12:] == "no":
                    markup.add(main_btn)
                    bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="Оплата отменена!",reply_markup=markup)
                user_data[call.message.chat.id]['buy'].clear()
        if call.data[:6] == "refill":
            BTNmarkup = types.ReplyKeyboardMarkup(True,True)
            BTNmarkup.row("100","150")
            BTNmarkup.row("300","500","1000")
            if(call.data[7:].isdigit()):
                BTNmarkup.row(str(int(call.data[7:])/10))
            msg = bot.send_message(call.message.chat.id,"Пополнить баланс на какую сумму?\nЧтобы выйти напишите 0",reply_markup=BTNmarkup)
            bot.register_next_step_handler(msg,after_refill)
            if(not call.data[6:7] == "#"):
                bot.answer_callback_query(call.id)
        if call.data[:9] == "vpn_ikev2":
            if not (call.data[9:10] == "#"):
                bot.answer_callback_query(call.id)
            ikev2_set_btn = types.InlineKeyboardButton(text="Создать IKEv2(beta)",callback_data="ikev2_buy")
            ikev2_get_btn = types.InlineKeyboardButton(text="Мои IKEv2(beta)",callback_data="get_vpn_ikev2")
            ikev2_config_btn = types.InlineKeyboardButton(text="Настройки IKEv2",callback_data="ikev2_settings")
            _back_btn = types.InlineKeyboardButton(text="Назад",callback_data="vpn")
            alphabet = string.ascii_letters + string.digits
            #creditals
            try:
                len(user_data[call.message.chat.id]['ikev2']['name'])
            except Exception as e:
                user = str(call.message.chat.id)+''.join(secrets.choice(string.digits) for i in range(10))
                user_data[call.message.chat.id] = {}
                user_data[call.message.chat.id]['ikev2'] = {}
                user_data[call.message.chat.id]['ikev2']['timeout'] = 1
                user_data[call.message.chat.id]['ikev2']['price'] = config.ikev2_price
                user_data[call.message.chat.id]['ikev2']['name'] = user+"IKEv2"
            markup.add(ikev2_set_btn,ikev2_get_btn)
            markup.add(ikev2_config_btn)
            markup.add(_back_btn)
            bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="Выберите нужный пункт.",reply_markup=markup)
            #bot.send_message(call.message.chat.id,"Выберите нужный пункт.",reply_markup=markup)
        if call.data[:14] == "ikev2_settings":
            if call.data[15:22] == "timeout":
                _ide = call.data[22:23]
                isFirst = _ide == "#"
                _ide = " " if _ide == "." else "."
                time = int(call.data[23:])
                if(time <1):
                    time = 1
                if(time > 120):
                    time = 120
                inc_btn = types.InlineKeyboardButton(text="+1мес",callback_data="ikev2_settings timeout"+_ide+str(time+1))
                dec_btn = types.InlineKeyboardButton(text="-1мес", callback_data="ikev2_settings timeout"+_ide+str(time-1))
                inc10_btn = types.InlineKeyboardButton(text="+10мес",callback_data="ikev2_settings timeout"+_ide+str(time+10))
                dec10_btn = types.InlineKeyboardButton(text="-10мес", callback_data="ikev2_settings timeout"+_ide+str(time-10))
                success_btn = types.InlineKeyboardButton(text="Готово",callback_data="ikev2_settings success"+_ide+str(time))
                markup.add(inc_btn,dec_btn)
                markup.add(inc10_btn,dec10_btn)
                markup.add(success_btn)
                month = ""+numeral.get_plural(int(time), "месяц, месяца, месяцев")
                price = config.ikev2_price * time
                user_data[call.message.chat.id]['ikev2']['temp_price'] = config.ikev2_price * time
                bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text='{}\nprice: {}₽'.format(month,price),reply_markup=markup)
                if not isFirst:
                    bot.answer_callback_query(call.id)
            elif call.data[15:22] == "success":
                bot.edit_message_reply_markup(chat_id=call.message.chat.id,message_id=call.message.message_id,reply_markup=types.InlineKeyboardMarkup())
                ikev2_config_btn = types.InlineKeyboardButton(text="Назад",callback_data="ikev2_settings")
                user_data[call.message.chat.id]['ikev2']['timeout'] = int(call.data[23:])
                user_data[call.message.chat.id]['ikev2']['price'] = config.ikev2_price * int(call.data[23:])
                markup.add(ikev2_config_btn)
                bot.send_message(call.message.chat.id,"удачно поменяли дату",reply_markup=markup)
            elif call.data[15:] == "name":
                msg = bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="Введите имя IKEv2 профиля:")
                bot.register_next_step_handler(msg,ikev2_config_after)
            else:
                timeout_btn = types.InlineKeyboardButton(text="Время жизни",callback_data="ikev2_settings timeout 1")
                name_btn = types.InlineKeyboardButton(text="Имя IKEv2",callback_data="ikev2_settings name")
                _vpn_btn=types.InlineKeyboardButton(text="Назад",callback_data="vpn_ikev2")
                markup.add(timeout_btn,name_btn)
                markup.add(_vpn_btn)
                try:
                    bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,
                                        text="Вы в меню настроек IKEv2\nтекущие настройки:\n\t\tname: {}\n\t\ttime: {}\n\t\tprice: {}₽".format(
                                            user_data[call.message.chat.id]['ikev2']['name'],
                                            numeral.get_plural(int(user_data[call.message.chat.id]['ikev2']['timeout']), "месяц, месяца, месяцев"),
                                            user_data[call.message.chat.id]['ikev2']['price'])
                                        ,reply_markup=markup)
                except KeyError as e:
                    bot.edit_message_reply_markup(chat_id=call.message.chat.id,message_id=call.message.message_id,reply_markup=types.InlineKeyboardMarkup())
                    bot.send_message(call.message.chat.id,"Сессия устарела!")
                    msg = bot.send_message(call.message.chat.id,"*vpn_ikev2*")
                    class XClass(object):
                        def __init__(self):
                            self.message = msg
                            self.data = 'vpn_ikev2#'
                    callback_inline(XClass())
        
        if call.data[:9] == "ikev2_buy":
            if call.data[10:] == "yes":
                _balance = int(db.execute("SELECT balance FROM Users WHERE userid = {}".format(call.message.chat.id))[0][0])
                print(_balance)
                try:
                    if(_balance-(int(user_data[call.message.chat.id]['ikev2']['price'])*10) >= 0):
                        _balance = _balance-(int(user_data[call.message.chat.id]['ikev2']['price'])*10)
                        db.updateUser(str(call.message.chat.id),"balance",str(_balance))
                        bot.edit_message_reply_markup(chat_id=call.message.chat.id,message_id=call.message.message_id,reply_markup=types.InlineKeyboardMarkup())
                        msg = bot.send_message(call.message.chat.id,"Операция прошла успешно!")
                        class XClass(object):
                            def __init__(self):
                                self.message = msg
                                self.data = "generate_vpn_ikev2"
                        callback_inline(XClass())
                    else:
                        refill_btn = types.InlineKeyboardButton(text="Пополнить баланс", callback_data="refill "+str(int(float(user_data[call.message.chat.id]['ikev2']['price'])*10)))
                        markup.add(refill_btn)
                        markup.add(main_btn)
                        bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="Недостаточно средств на балансе!",reply_markup=markup)
                except Exception as e:
                    print(e)
                    bot.edit_message_reply_markup(chat_id=call.message.chat.id,message_id=call.message.message_id,reply_markup=types.InlineKeyboardMarkup())
                    bot.send_message(call.message.chat.id,"Упс... У нас что-то сломалось. Попробуй ещё раз или позже")
            elif call.data[10:] == "no":
                _vpn_btn=types.InlineKeyboardButton(text="Назад",callback_data="vpn_ikev2")
                markup.add(_vpn_btn)
                bot.edit_message_reply_markup(chat_id=call.message.chat.id,message_id=call.message.message_id,reply_markup=types.InlineKeyboardMarkup())
                bot.send_message(call.message.chat.id,"Операция отклонена!",reply_markup=markup)
            else:
                yes_btn = types.InlineKeyboardButton(text="Да",callback_data="ikev2_buy yes")
                no_btn = types.InlineKeyboardButton(text="Нет",callback_data="ikev2_buy no")
                markup.add(yes_btn,no_btn)
                bot.send_message(call.message.chat.id,
                                "Вы хотите купить IKEv2 Профиль(сертификат):\n\t\tname: {}\n\t\ttime: {}\n\t\tprice: {}₽".format(
                                    user_data[call.message.chat.id]['ikev2']['name'],
                                    numeral.get_plural(int(user_data[call.message.chat.id]['ikev2']['timeout']), "месяц, месяца, месяцев"),
                                    user_data[call.message.chat.id]['ikev2']['price'])
                                ,reply_markup=markup)
            bot.answer_callback_query(call.id)

        if call.data == "generate_vpn_ikev2":
            try:
                bot.send_message(call.message.chat.id,"wait.")
                name = user_data[call.message.chat.id]['ikev2']['name']
                ikev2_set_thread = threading.Thread(target=vpnconfig.set_profiles,args=(name,user_data[call.message.chat.id]['ikev2']['timeout']))
                ikev2_set_thread.start()
                ikev2_set_thread.join()
                if(len(str(data[1]))>len("b''")):
                    bot.send_message(call.message.chat.id,data[1])
                    return 0
                bot.send_message(call.message.chat.id,"done!")
                files = [   types.InputFile(file=open("../{}.p12".format(name),"rb")),
                            types.InputFile(file=open("../{}.mobileconfig".format(name),"rb")),
                            types.InputFile(file=open("../{}.sswan".format(name),'rb'))
                        ]
                for i in files:
                    bot.send_document(call.message.chat.id,i)
                bot.send_message(call.message.chat.id,"{}.p12 (for Windows & Linux)\n{}.sswan (for Android)\n{}.mobileconfig (for iOS & macOS)".format(name,name,name))
                bot.send_message(call.message.chat.id,"Инструкция: https://github.com/hwdsl2/setup-ipsec-vpn/blob/master/docs/ikev2-howto.md#configure-ikev2-vpn-clients \nВыберите вашу систему и проделайте все по инструкции")

                removef = subprocess.getstatusoutput('rm -f ../{}.*'.format(name))
                if(not (removef[0] == 0)):
                    print(removef)
                _data = db.execute("SELECT vpnids FROM Users WHERE userid = {}".format(call.message.chat.id))[0]
                _json = json.loads(_data[0])
                # _json["ikev2"].append(name)
                _json['ikev2'].append({"value":name,"time":user_data[call.message.chat.id]['ikev2']['timeout']})
                db.updateUser(str(call.message.chat.id),"vpnids",json.dumps(_json))
                msg = bot.send_message(call.message.chat.id,"*vpn_ikev2*")
                class XClass(object):
                    def __init__(self):
                        self.message = msg
                        self.data = 'vpn_ikev2#'
                callback_inline(XClass())
            except FileNotFoundError as e:
                print(e)
                bot.send_message(call.message.chat.id,"Я не могу отправить тебе файл, его нет!")
            except IndexError as e:
                print(e)
                bot.send_message(call.message.chat.id,"Кажется возникла проблема с записью в базу данных данного ikev2 vpn. Он работает, но не будет отображаться в профиле. Обратитесь к администрации, чтобы исправить это недоразумение.")
            except KeyError as e:
                bot.send_message(call.message.chat.id,"Сессия устарела!")
                msg = bot.send_message(call.message.chat.id,"*vpn_ikev2*")
                class XClass(object):
                    def __init__(self):
                        self.message = msg
                        self.data = 'vpn_ikev2#'
                callback_inline(XClass())
            except Exception as e:
                print(e)
                bot.send_message(call.message.chat.id,"Что-то сломалося")
        if call.data[:13] == "get_vpn_ikev2":
            try:
                _data = db.execute("SELECT vpnids FROM Users WHERE userid = {}".format(call.message.chat.id))[0]
                _json = json.loads(_data[0])
                if call.data[14:17] == "get":
                    __data = call.data[18:]
                    _id = ""
                    for i,vol in enumerate(_json["ikev2"]):
                        if(i+1 == int(__data)):
                            try:
                                _volJson = vol
                                _vol = _volJson["value"]
                                _voltime = ''+numeral.get_plural(int(_volJson["time"]), "месяц, месяца, месяцев")
                            except Exception as e:
                                _vol = vol
                                _voltime = "null"
                            _id = _vol
                            break
                    if(_id == ""):
                        ikev2_get_btn = types.InlineKeyboardButton(text="Назад",callback_data="vpn_ikev2")
                        markup.add(ikev2_get_btn)
                        bot.send_message(call.message.chat.id,"Выбранный id вне списка!",reply_markup=markup)
                        raise IndexError
                    ikev2_get_thread = threading.Thread(target=vpnconfig.get_profiles,args=(str(_id),))
                    ikev2_get_thread.start()
                    bot.send_message(call.message.chat.id,"wait.")
                    ikev2_get_thread.join()
                    files = [   types.InputFile(file=open("../{}.p12".format(_id),"rb")),
                                types.InputFile(file=open("../{}.mobileconfig".format(_id),"rb")),
                                types.InputFile(file=open("../{}.sswan".format(_id),'rb'))
                            ]
                    for z in files:
                        bot.send_document(call.message.chat.id,z)
                    bot.send_message(call.message.chat.id,"{}.p12 (for Windows & Linux)\n{}.sswan (for Android)\n{}.mobileconfig (for iOS & macOS)".format(_id,_id,_id))
                    bot.send_message(call.message.chat.id,"Инструкция: https://github.com/hwdsl2/setup-ipsec-vpn/blob/master/docs/ikev2-howto.md#configure-ikev2-vpn-clients \nВыберите вашу систему и проделайте все по инструкции")
                    removef = subprocess.getstatusoutput('rm -f ../{}.*'.format(_id))
                    if(not (removef[0] == 0)):
                        print(removef)
                    msg = bot.send_message(call.message.chat.id,"*vpn_ikev2*")
                    class XClass(object):
                        def __init__(self):
                            self.message = msg
                            self.data = 'vpn_ikev2#'
                    callback_inline(XClass())
                else:
                    _name = ""
                    for i,vol in enumerate(_json["ikev2"]):
                        try:
                            _volJson = vol
                            _vol = _volJson["value"]
                            _voltime = ''+numeral.get_plural(int(_volJson["time"]), "месяц, месяца, месяцев")
                        except Exception as e:
                            _vol = vol
                            _voltime = "null"
                        _name += "{}. name: {}\n\t   time: {}\n\n".format(i+1,_vol,_voltime)
                    bot.send_message(call.message.chat.id,"список: \n"+_name)
                    msg = bot.send_message(call.message.chat.id,"Выберите тот, что хотите загрузить: ")
                    bot.register_next_step_handler(msg,get_vpn_ikev2_after)
                # for i in _json["ikev2"]:
                #     ikev2_get_thread = threading.Thread(target=get_profiles,args=(str(i),))
                #     ikev2_get_thread.start()
                #     bot.send_message(call.message.chat.id,"wait.")
                #     ikev2_get_thread.join()
                #     bot.send_message(call.message.chat.id,"print: '"+ i +"' ikev2")
                #     files = [   types.InputFile(file=open("../{}.p12".format(i),"rb")),
                #                 types.InputFile(file=open("../{}.mobileconfig".format(i),"rb")),
                #                 types.InputFile(file=open("../{}.sswan".format(i),'rb'))
                #             ]
                #     for z in files:
                #         bot.send_document(call.message.chat.id,z)
                #     removef = subprocess.getstatusoutput('rm -f ../{}.*'.format(i))
                #     if(not (removef[0] == 0)):
                #         print(removef)
            except IndexError as e:
                pass
        if call.data == "whichisbetter":
            _vpn_btn=types.InlineKeyboardButton(text="Назад",callback_data="vpn")
            markup.add(destroy_btn)
            bot.send_message(call.message.chat.id,
                "Что лучше выбрать?\n"
                "\n"
                "Покупать стоит лучше IKEv2, ибо это новый протокол и считается более безопасным, нежели тот же I2TP/X-auth\n"
                "\n"
                "Мой бот предоставляет возможность выбора того или иного протокола, отнюдь это не значит что они оба безопасны.\n"
                "IKEv2 выдаётся как сертификаты, а не конкретные данные. Так что будте бдительны при покупке!"
            ,reply_markup=markup)
    # Если сообщение из инлайн-режима
    elif call.inline_message_id:
        if call.data == "test":
            bot.edit_message_text(inline_message_id=call.inline_message_id, text="Бдыщь")

@bot.message_handler(commands=['myid'])
def start_message(message):
    bot.send_message(message.chat.id,"Your id is: "+str(message.chat.id))

def after_start(message):
    if(message.text[:4].lower() == "прин"):
        resp = db.getUser("userid",message.chat.id)
        if(len(resp)<=0):
            db.addUser(str(message.chat.id),str(json.dumps({"vpnid":[],"username":message.from_user.username, "ikev2":[]})),message.from_user.first_name,message.from_user.last_name)
            print("im added user",end=" ")
            print(str(message.chat.id),str(json.dumps({"vpnid":[],"username":message.from_user.username})),message.from_user.first_name,message.from_user.last_name)
        BTNmarkup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id,"Классно!",reply_markup=BTNmarkup)
        markup = types.InlineKeyboardMarkup()
        main_btn = types.InlineKeyboardButton(text="В главное меню",callback_data="main")
        markup.add(main_btn)
        bot.send_message(message.chat.id,"Как же хорошо с вами работать! Теперь давайте прололжим, для попадания в главное меню нажмите кнопку под сообщением",reply_markup=markup)
    elif(message.text[:5].lower()=="отказ"):
        bot.send_message(message.chat.id,"Вы отказываетесь соглашаться с правилами. Тогда немедленно отчистите чат и отключите у себя бота(кнопока с ботом и кружочком перечеркнутым). Продолжить без соглашения не получиться!")

def after_edit(message):
    if(message.text.lower() == "vpn"):
        
        msg = bot.send_message(message.chat.id,"Хорошо, давай поменяем настройки vpn. Пожалуйста, укажи номер меняемого vpn(Чтобы выйти, напиши 0):",reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(message.chat.id,""+getvpnstr(message.chat.id))
        bot.register_next_step_handler(msg,after_edit_vpn)
    if(message.text.lower() == "профиль"):
        bot.send_message(message.chat.id,"Да, замечательно. Давай тогда кратко пробежимся о тебе:")
    if(message.text.lower() == "выйти"):
        bot.send_message(message.chat.id,"Вы вышли",reply_markup=types.ReplyKeyboardRemove())
        msg = bot.send_message(message.chat.id,"*menu*")
        class XClass(object):
            def __init__(self):
                self.message = msg
                self.data = 'main#'
        callback_inline(XClass())

def after_edit_vpn(message):
    if(message.text.isdigit()):
        if(int(message.text) == 0):
            bot.send_message(message.chat.id,"Вы вышли",reply_markup=types.ReplyKeyboardRemove())
            msg = bot.send_message(message.chat.id,"*menu*")
            class XClass(object):
                def __init__(self):
                    self.message = msg
                    self.data = 'main#'
            callback_inline(XClass())
            return 0
        try:
            data = db.getUser("userid",message.chat.id)[0]
            jsonfromdata = json.loads(data[9])
            id = jsonfromdata['vpnid'][int(message.text)-1]
            vpns = db.getVpn(id)[0]
            result = "\t\tlogin: "+vpns[3] + "\n\t\tpasswd: "+vpns[4]+"\n\t\tserver/ip: "+vpns[1]+"\n\t\tprotocol: "+vpns[2]+"\n\t\tPSK: "+vpnconfig.getPSK()+"\n\n\t\tdestruction time: "+vpns[5]+"\n\n"
            msg = bot.send_message(message.chat.id,"Этот впн?(да/нет)")
            bot.send_message(message.chat.id,'{}'.format(result))
            #bot.register_next_step_handler(msg,after_edit_vpn2,id)
            after_edit_vpn2(msg,id)
        except IndexError as e:
            msg = bot.send_message(message.chat.id,"Такого Впн в списке нет, извини.")

        except Exception as e:
            print(e)
            bot.send_message(message.chat.id,"У меня возникла ошибка, что-то сломалось")
    else:
        bot.send_message(message.chat.id,"Кажется ты мне отправил вообще не число... Чтобы продолжить начни заново")
def after_edit_vpn2(message,arg):
    if(not message.text[:2].lower() == "да"):
        user_data[message.chat.id] = {}
        user_data[message.chat.id]['buy'] = {}
        user_data[message.chat.id]['buy']["vpnid"] = str(arg)
        markup = types.ReplyKeyboardMarkup(True)
        markup.row("Продлить")
        markup.row("Выйти")
        #markup.row("Сменить пароль","Сменить логин")
        #markup.row("Активировать","Деактивировать")
        msg = bot.send_message(message.chat.id,"Хорошо, давайте дальше. Чего вы хотите?",reply_markup=markup)
        bot.register_next_step_handler(msg,after_edit_vpn3)
    elif(message.text[:2].lower() == "не"):
        msg = bot.send_message("Давайте назад на 1 шаг. ВВедите номер вашего впн из списка ниже")
        bot.send_message(message.chat.id,""+getvpnstr(message.chat.id))
        bot.register_next_step_handler(msg,after_edit_vpn)

def after_edit_vpn3(message):
    if(message.text.lower() == "продлить"):
        bot.send_message(message.chat.id,"На сколько?",reply_markup=types.ReplyKeyboardRemove())
        msg = bot.send_message(message.chat.id, "1 день")
        #костыль отправки коллбека
        class XClass(object):
            def __init__(self):
                self.message = msg
                self.data = 'vpn_renewal#1'
        callback_inline(XClass())
    if(message.text.lower() == "удалить"):
        bot.send_message(message.chat.id,"Вы уверены что хотите удалить?")
    if(message.text.lower() == "выйти"):
        bot.send_message(message.chat.id,"Вы вышли",reply_markup=types.ReplyKeyboardRemove())
        msg = bot.send_message(message.chat.id,"*menu*")
        class XClass(object):
            def __init__(self):
                self.message = msg
                self.data = 'main#'
        callback_inline(XClass())

def after_buy_ammount(message):
    markup = types.InlineKeyboardMarkup()
    if(message.text.lower() == "да"):
        try:
            balance = int(db.getUser("userid",message.chat.id)[0][7])
            if(balance >= config.price_slot*10):
                _ammount = db.cur.execute("SELECT ammount FROM users WHERE userid = ?",(message.chat.id,)).fetchall()[0][0]
                db.updateUser(message.chat.id,"ammount",_ammount+1)
                db.updateUser(message.chat.id,"balance",balance-(config.price_slot*10))
                msg = bot.send_message(message.chat.id,".")
                class XClass(object):
                    def __init__(self):
                        self.message = msg
                        self.data = 'create_vpn#'
                callback_inline(XClass())
            else:
                refill_btn = types.InlineKeyboardButton(text="Пополнить баланс", callback_data="refill "+"")
                main_btn = types.InlineKeyboardButton(text="В главное меню",callback_data="main")
                markup.add(refill_btn)
                markup.add(main_btn)
                bot.send_message(message.chat.id,"Недостаточно средств на балансе!",reply_markup=markup)
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id,"Произошла ошибка на сервере, деньги не были списаны. Попробуйте позже")

def ikev2_config_after(message):
    user_data[message.chat.id]['ikev2']['name'] = str(message.chat.id)+"_"+message.text.replace(" ","_").replace("\\","-").replace("/","-").replace("@","-").replace("#","-").replace("!","-").replace("&","-").replace("^","-").replace("(","_").replace(")","_").replace("<","_").replace(">","_").replace("%%","_").replace("{","_").replace("}","_").replace(":","_").replace(";","_").replace("?","_")
    msg = bot.send_message(message.chat.id,"*ikev2 config*")
    class XClass(object):
        def __init__(self):
            self.message = msg
            self.data = 'ikev2_settings#'
    callback_inline(XClass())

def get_vpn_ikev2_after(message):
    if(is_digit(message.text)):
        msg = bot.send_message(message.chat.id,"*get_vpn_ikev2*")
        class XClass(object):
            def __init__(self):
                self.message = msg
                self.data = 'get_vpn_ikev2#get {}'.format(int(message.text))
        callback_inline(XClass())

def after_refill(message):
    markup = types.InlineKeyboardMarkup()
    main_btn = types.InlineKeyboardButton(text="В главное меню",callback_data="main")
    markup.add(main_btn)
    if(is_digit(message.text)):
        if(float(message.text)==0):
            bot.send_message(message.chat.id,"Вы вышли",reply_markup=types.ReplyKeyboardRemove())
            msg = bot.send_message(message.chat.id,"*menu*")
            class XClass(object):
                def __init__(self):
                    self.message = msg
                    self.data = 'main#'
            callback_inline(XClass())
            return 0
        balance = int(db.getUser("userid",message.chat.id)[0][7])
        if(isReal_payment):
            price = [types.LabeledPrice(label="Руб",amount=int(float(int(float(message.text)*10)/10)*100))]
            bot.send_message(message.chat.id,"Вам был отправлен чек. Пожалуйста оплатите его!",reply_markup=types.ReplyKeyboardRemove())
            bot.send_invoice(
                message.chat.id,        #chat_id
                "Оплата",               #title
                "Пополнение баланса",   #description
                "refill",               #payload
                config.pay_token,       #token
                "RUB",                  #curency
                price,                  #price
                "test"                  #start_parameter
            )
        else:
            db.updateUser(message.chat.id,"balance",balance+(int(float(message.text)*10)))
            bot.send_message(message.chat.id,"Баланс пополнен на сумму: "+message.text+"₽",reply_markup=markup)
    else:
        bot.send_message(message.chat.id,"Вы ввели некоректные данные, попробуйте пополнить баланс заново.",reply_markup=markup)

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Aliens tried to steal your card's CVV, but we successfully protected your credentials,"
                                                " try to pay again in a few minutes, we need a small rest.")

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    markup = types.InlineKeyboardMarkup()
    main_btn = types.InlineKeyboardButton(text="В главное меню",callback_data="main")
    markup.add(main_btn)
    balance = int(db.getUser("userid",message.chat.id)[0][7])
    db.updateUser(message.chat.id,"balance",balance+(int(float(message.successful_payment.total_amount / 100)*10)))
    bot.send_message(message.chat.id,"Баланс пополнен на сумму: "+str(message.successful_payment.total_amount / 100)+"₽",reply_markup=markup)
    
def checker(args):
    while True:
        print("manually check incorrect vpns")
        vpns = db.execute("SELECT time_delete, user, vpnid, status FROM vpns")
        for i in range(0,len(vpns)):
            date = datetime.datetime.strptime(vpns[i][0],('%Y-%m-%d %H:%M:%S'))
            if(date < datetime.datetime.now()):
                _json = json.loads(vpns[i][3])
                if(not _json['status']['value'] == 0):
                    if(vpnconfig.autodeluser(vpns[i][1]) == 0):
                        print("vpn "+vpns[i][1]+" deleted successful")
                    else:
                        print("vpn "+vpns[i][1]+" deleted unsucessful")
                    try:
                    
                        _json['status']['value'] = 0
                        _json['status']['description'] = "disabled by autosystem"

                        db.updateVpn(vpns[i][2],'status',json.dumps(_json))
                    except Exception as e:
                        print("error add status to "+vpns[i][2])
        time.sleep(60*60*2)

thread = threading.Thread(target=checker,args=("1",))
thread.start()
bot.infinity_polling()