import json
import telebot
from telebot import types

import vpnconfig
import database
from config import *


bot = telebot.TeleBot(token)
db = database.databaseVPN()
@bot.message_handler(commands=['start'])
def start_message(message):
    resp = db.getUser("userid",message.from_user.id)
    if(len(resp)<=0):
        db.addUser(str(message.from_user.id),str(json.dumps({"vpnid":[],"username":message.from_user.username})),message.from_user.first_name,message.from_user.last_name)
    markup = types.InlineKeyboardMarkup()
    item1=types.InlineKeyboardButton(text="test_btn",callback_data="test")
    item2=types.InlineKeyboardButton(text="Личный кабинет",callback_data="account")
    item3=types.InlineKeyboardButton(text="VPN",callback_data="vpn")
    markup.add(item1,item2)
    markup.add(item3)
    bot.send_message(message.chat.id,"Привет ✌️\nЯ предоставляю VPN сервисы за маленькую стоимость(просто поддержание работы сервиса и оплату хостинга).",reply_markup=markup)

def getvpnstr(userid:str)->str:
    result = ""
    try:
        data = db.getUser("userid",userid)[0]
        jsonfromdata = json.loads(data[9])
        for i in range(0,len(jsonfromdata['vpnid'])):
            vpns = db.getVpn(jsonfromdata['vpnid'][i])[0]
            result += str(i+1)+".\t\tlogin: "+vpns[3] + "\n\t\tpasswd: "+vpns[4]+"\n\t\tserver/ip: "+vpns[1]+"\n\t\tprotocol: "+vpns[2]+"\n\t\tPSK: "+vpnconfig.getPSK()+"\n\t\tdestruction time: "+vpns[5]+"\n\n"
    except Exception as e:
        print(data)
    return result

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.message:
        if call.data == "test":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Пыщь")
        if call.data == "account":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                text="Вы - '"+str(call.message.chat.id)+"'\n"
                "Ваш баланс - "+str(db.getUser("userid",call.message.chat.id)[0][7])+"₽\n"
                "Текушие активные аккаунты: \n"
                ""+getvpnstr(call.message.chat.id))
        if call.data == "vpn":
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton(text="Создать",callback_data="create_vpn")
            markup.add(item1)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите интересующие варианты:",reply_markup=markup)
        if call.data == "create_vpn":

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Я вас понял!")
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text="Закрыть",callback_data="destroy"))

            
            _user = db.getUser("userid",str(call.message.chat.id))[0]
            _json = json.loads(_user[9])
            description = "Слишком большого количесва vpn(у вас "+str(len(_json['vpnid']))+"). Пожалуйста перейдите в личный кабинет и воспользуйтесь существующими vpn"
            if(len(_json["vpnid"])<2):
                #creditals
                user = str(call.message.chat.id)
                password = "12345678"
                protocol = "'IPSec Xauth PSK' / 'L2TP/IPSec PSK'"
                _ip = vpnconfig.ip
                #db
                id = db.addVpn(protocol,user,password,ip)
                _json["vpnid"].append(id)
                db.updateUser(str(call.message.chat.id),"vpnids",str(json.dumps(_json)))
                #create vpn user
                vpnconfig.autoadduser(user,password)
                bot.send_message(call.message.chat.id,
                    "Ваши данные: \n"
                    "\ttype protocol: "+protocol+"\n"
                    "\tip: "+_ip+"\n"
                    "\tlogin: "+user+"\n"
                    "\tpassword: "+password+"\n"
                    "\tPSK(pre-shared key): "+ vpnconfig.getPSK()+"\n"
                    ,reply_markup=markup)
            else:
                markup.add(types.InlineKeyboardButton(text="Личный кабинет",callback_data="account"))
                bot.send_message(call.message.chat.id,
                "Извините, но мы не можем выдать вам vpn по причине: "+description
                ,reply_markup=markup)
        if call.data == "destroy":
            bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)
    # Если сообщение из инлайн-режима
    elif call.inline_message_id:
        if call.data == "test":
            bot.edit_message_text(inline_message_id=call.inline_message_id, text="Бдыщь")

@bot.message_handler(commands=['myid'])
def start_message(message):
    bot.send_message(message.chat.id,"Your id is: "+str(message.chat.id))


bot.infinity_polling()