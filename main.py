import telebot
from telebot import types
import subprocess

from config import *

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.InlineKeyboardMarkup()
    item1=types.InlineKeyboardButton(text="test_btn",callback_data="test")
    item2=types.InlineKeyboardButton(text="Аккаунт",callback_data="account")
    item3=types.InlineKeyboardButton(text="VPN",callback_data="vpn")
    markup.add(item1,item2)
    markup.add(item3)
    bot.send_message(message.chat.id,"Привет ✌️\nЯ предоставляю VPN сервисы за маленькую стоимость(просто поддержание работы сервиса и оплату хостинга).",reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.message:
        if call.data == "test":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Пыщь")
        if call.data == "account":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                text="Вы - '"+str(call.message.chat.id)+"'\n"
                "Ваш баланс - "+str(0)+"₽\n"
                "Текушие активные аккаунты: \n"
                "\t-admin:pass \n\t\tip:192.168.4.1 \n\t\tprotol: p2tp\n\t\ttime detonation: 23.10.2022"
                )
        if call.data == "vpn":
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton(text="Создать",callback_data="create_vpn")
            markup.add(item1)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите интересующие варианты:",reply_markup=markup)
        if call.data == "create_vpn":

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Я вас понял!")
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text="Закрыть",callback_data="destroy"))
            s = subprocess.Popen(["sudo /bin/bash /opt/src/addvpnuser.sh '" +str(call.message.chat.id)+"' '12345678'"],shell=True)
            print(s.returncode)
            print(s.stdout)
            bot.send_message(call.message.chat.id,
                "Ваши данные: \n"
                "\tip: "+"176.124.217.129\n"
                "\tlogin: "+str(call.message.chat.id)+"\n"
                "\tpassword: "+str(12345678)+"\n"
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

@bot.message_handler(commands=['button'])
def button_message(message):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=types.KeyboardButton("Кнопка")
    markup.add(item1)
    bot.send_message(message.chat.id,'Выберите что вам надо',reply_markup=markup)

@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text=="Кнопка":
        bot.send_message(message.chat.id,"https://habr.com/ru/users/lubaznatel/")		

bot.infinity_polling()