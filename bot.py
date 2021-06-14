#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys
import config
import time
import datetime
import subprocess
import tty
import pty
import psutil
import numpy as np
import pandas as pd
import logging
import threading
import re
import telebot
from telebot import types
from telebot import util
from dotenv import load_dotenv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import gettext
import socket


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


host_ip = get_ip()
host_name = config.hostname

# ##### TONTgBot

# API Token
bot = telebot.TeleBot(config.api_key)
# /API Token

root_folder = os.path.dirname(__file__)
db_folder = os.path.join(root_folder, 'db')

# ##### TONTgBot

lang_translations = gettext.translation('base', localedir=os.path.join(root_folder, "locales"), languages=['en'])
lang_translations.install()
_ = lang_translations.gettext

# dotenv_path = (os.path.join(config.tf, "script/env.sh"))
# load_dotenv(dotenv_path)

# Log
logger = telebot.logger
telebot.logger.setLevel(logging.ERROR) # Outputs Error messages to console.
# /Log

#hostn = os.uname()[1]
#hostn = (hostn[0:hostn.find('.')])

# Menu vars
lt_cpu = _("CPU")
lt_cpu = "\U0001F39B " + lt_cpu
lt_ram = _("RAM")
lt_ram = "\U0001F39A " + lt_ram
lt_disks = _("Disk usage")
lt_disks = "\U0001F4BE " + lt_disks
lt_linuxtools = _("Linux tools")
lt_linuxtools = "\U0001F9F0 " + lt_linuxtools
lt_minatools = _("Mina tools")
lt_minatools = "\U0001F9F0 " + lt_minatools
#----
lt_ping = _("Ping test")
lt_ping =  "\U0001F7E2 " + lt_ping
lt_topproc = _("Top processes")
lt_topproc =  "\U0001F7E2 " + lt_topproc
lt_ssvalid = _("Port check")
lt_ssvalid =  "\U0001F7E2 " + lt_ssvalid
lt_currntwrkload = _("Current network load")
lt_currntwrkload =  "\U0001F7E2 " + lt_currntwrkload
lt_currntdiskload = _("Current disk i/o")
lt_currntdiskload = "\U0001F7E2 " + lt_currntdiskload
lt_starttime = _("Uptime")
lt_starttime = "\U0001F7E2 " + lt_starttime
lt_mainmenu = _("Main menu")
lt_mainmenu =  "\U0001F3E1 " + lt_mainmenu
#----
node_status = _("Node status")
node_status = "\U0001F48E " + node_status
exect_restart_status = _("???Restart Node???")
exect_restart_status = "\U0001F48E " + exect_restart_status
block_producer_status = _("Block producer status")
block_producer_status = "\U0001F48E " + block_producer_status
restart_node = _("Restart node")
restart_node = "\U0001F48E " + restart_node
check_sidecard_logs = _("Check sidecard logs")
check_sidecard_logs = "\U0001F48E " + check_sidecard_logs

# Default markup
markup = types.ReplyKeyboardMarkup()
cpu = types.KeyboardButton(lt_cpu)
ram = types.KeyboardButton(lt_ram)
disks = types.KeyboardButton(lt_disks)
minatools = types.KeyboardButton(lt_minatools)
linuxtools = types.KeyboardButton(lt_linuxtools)
markup.row(cpu,ram, disks)
markup.row(minatools,linuxtools)
# /Default markup

# Linux markup
markuplinux = types.ReplyKeyboardMarkup()
ping = types.KeyboardButton(lt_ping)
topproc = types.KeyboardButton(lt_topproc)
ssvalid = types.KeyboardButton(lt_ssvalid)
starttime = types.KeyboardButton(lt_starttime)
currntwrkload = types.KeyboardButton(lt_currntwrkload)
currntdiskload = types.KeyboardButton(lt_currntdiskload)
mainmenu = types.KeyboardButton(lt_mainmenu)
markuplinux.row(ssvalid, ping)
markuplinux.row(topproc, starttime)
markuplinux.row(currntwrkload,currntdiskload)
markuplinux.row(mainmenu)
# /Linux markup


markupmina = types.ReplyKeyboardMarkup()
node_status_markup = types.KeyboardButton(node_status)
block_producer_status_markup = types.KeyboardButton(block_producer_status)
restart_node_markup = types.KeyboardButton(restart_node)
check_sidecard_logs_markup = types.KeyboardButton(check_sidecard_logs)
mainmenu = types.KeyboardButton(lt_mainmenu)
markupmina.row(node_status_markup, block_producer_status_markup)
markupmina.row(restart_node_markup, check_sidecard_logs_markup)
markupmina.row(mainmenu)


restartmina = types.ReplyKeyboardMarkup()
exect_restart = types.KeyboardButton(exect_restart_status)
node_status_markup = types.KeyboardButton(node_status)
mainmenu = types.KeyboardButton(lt_mainmenu)
restartmina.row(node_status_markup, exect_restart)
restartmina.row(mainmenu)

# Get id for tg value
@bot.message_handler(commands=["id"])
def get_id(i):
    id = i.from_user.id
    msg = "Id: " + str(id)
    bot.reply_to(i, msg)
# /Get id for tg value


# Start
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    if message.from_user.id == config.user_id:
        bot.send_message(config.user_id, _("Hello") + "\U0001F44B\n" + _("I'm here to help you with your Mina server ") + " \U0001F9BE\n" + _("Let's choose what you want?"),reply_markup=markup)
    else:
        pass
# /Start

# InlineKeyboards
#CPU
cpuloadhist = types.InlineKeyboardMarkup()
cpuloadhist.row(
    types.InlineKeyboardButton(text=_("30m"), callback_data="cpuhist_30m"),
    types.InlineKeyboardButton(text=_("1h"), callback_data="cpuhist_1h"),
    types.InlineKeyboardButton(text=_("3h"), callback_data="cpuhist_3h"),
    types.InlineKeyboardButton(text=_("6h"), callback_data="cpuhist_6h"),
    types.InlineKeyboardButton(text=_("12h"), callback_data="cpuhist_12h"),
    types.InlineKeyboardButton(text=_("1d"), callback_data="cpuhist_1d"),
    types.InlineKeyboardButton(text=_("+"), callback_data="cpuhistmore"))

cpuhistmore = types.InlineKeyboardMarkup()
cpuhistmore.row(
    types.InlineKeyboardButton(text="\U00002190", callback_data="cpuloadhist"),
    types.InlineKeyboardButton(text=_("3d"), callback_data="cpuhist_3d"),
    types.InlineKeyboardButton(text=_("5d"), callback_data="cpuhist_5d"),
    types.InlineKeyboardButton(text=_("7d"), callback_data="cpuhist_7d"),
    types.InlineKeyboardButton(text=_("14d"), callback_data="cpuhist_14d"),
    types.InlineKeyboardButton(text=_("21d"), callback_data="cpuhist_21d"),
    types.InlineKeyboardButton(text=_("30d"), callback_data="cpuhist_30d"))
#CPU

#RAM
ramloadhist = types.InlineKeyboardMarkup()
ramloadhist.row(
    types.InlineKeyboardButton(text=_("30m"), callback_data="ramhist_30m"),
    types.InlineKeyboardButton(text=_("1h"), callback_data="ramhist_1h"),
    types.InlineKeyboardButton(text=_("3h"), callback_data="ramhist_3h"),
    types.InlineKeyboardButton(text=_("6h"), callback_data="ramhist_6h"),
    types.InlineKeyboardButton(text=_("12h"), callback_data="ramhist_12h"),
    types.InlineKeyboardButton(text=_("1d"), callback_data="ramhist_1d"),
    types.InlineKeyboardButton(text=_("+"), callback_data="ramhistmore"))

ramhistmore = types.InlineKeyboardMarkup()
ramhistmore.row(
    types.InlineKeyboardButton(text=_("\U00002190"), callback_data="ramloadhist"),
    types.InlineKeyboardButton(text=_("3d"), callback_data="ramhist_3d"),
    types.InlineKeyboardButton(text=_("5d"), callback_data="ramhist_5d"),
    types.InlineKeyboardButton(text=_("7d"), callback_data="ramhist_7d"),
    types.InlineKeyboardButton(text=_("14d"), callback_data="ramhist_14d"),
    types.InlineKeyboardButton(text=_("21d"), callback_data="ramhist_21d"),
    types.InlineKeyboardButton(text=_("30d"), callback_data="ramhist_30d"))
#RAM

# Time Diff
timediffhist = types.InlineKeyboardMarkup()
timediffhist.row(
    types.InlineKeyboardButton(text=_("30m"), callback_data="timediffhist_30m"),
    types.InlineKeyboardButton(text=_("1h"), callback_data="timediffhist_1h"),
    types.InlineKeyboardButton(text=_("3h"), callback_data="timediffhist_3h"),
    types.InlineKeyboardButton(text=_("6h"), callback_data="timediffhist_6h"),
    types.InlineKeyboardButton(text=_("12h"), callback_data="timediffhist_12h"),
    types.InlineKeyboardButton(text=_("1d"), callback_data="timediffhist_1d"),
    types.InlineKeyboardButton(text=_("+"), callback_data="timediffhistmore"))

timediffhistmore = types.InlineKeyboardMarkup()
timediffhistmore.row(
    types.InlineKeyboardButton(text=_("\U00002190"), callback_data="timediffhist"),
    types.InlineKeyboardButton(text=_("3d"), callback_data="timediffhist_3d"),
    types.InlineKeyboardButton(text=_("5d"), callback_data="timediffhist_5d"),
    types.InlineKeyboardButton(text=_("7d"), callback_data="timediffhist_7d"),
    types.InlineKeyboardButton(text=_("14d"), callback_data="timediffhist_14d"),
    types.InlineKeyboardButton(text=_("21d"), callback_data="timediffhist_21d"),
    types.InlineKeyboardButton(text=_("30d"), callback_data="timediffhist_30d"))
# Time Diff

#PING
pingcheckhist = types.InlineKeyboardMarkup()
pingcheckhist.row(
    types.InlineKeyboardButton(text=_("30m"), callback_data="pinghist_30m"),
    types.InlineKeyboardButton(text=_("1h"), callback_data="pinghist_1h"),
    types.InlineKeyboardButton(text=_("3h"), callback_data="pinghist_3h"),
    types.InlineKeyboardButton(text=_("6h"), callback_data="pinghist_6h"),
    types.InlineKeyboardButton(text=_("12h"), callback_data="pinghist_12h"),
    types.InlineKeyboardButton(text=_("1d"), callback_data="pinghist_1d"),
    types.InlineKeyboardButton(text=_("+"), callback_data="pinghistmore"))

pinghistmore = types.InlineKeyboardMarkup()
pinghistmore.row(
    types.InlineKeyboardButton(text=_("\U00002190"), callback_data="pingcheckhist"),
    types.InlineKeyboardButton(text=_("3d"), callback_data="pinghist_3d"),
    types.InlineKeyboardButton(text=_("5d"), callback_data="pinghist_5d"),
    types.InlineKeyboardButton(text=_("7d"), callback_data="pinghist_7d"),
    types.InlineKeyboardButton(text=_("14d"), callback_data="pinghist_14d"),
    types.InlineKeyboardButton(text=_("21d"), callback_data="pinghist_21d"),
    types.InlineKeyboardButton(text=_("30d"), callback_data="pinghist_30d"))
#PING

# Network
networkcheckhist = types.InlineKeyboardMarkup()
networkcheckhist.row(
    types.InlineKeyboardButton(text=_("30m"), callback_data="networkhist_30m"),
    types.InlineKeyboardButton(text=_("1h"), callback_data="networkhist_1h"),
    types.InlineKeyboardButton(text=_("3h"), callback_data="networkhist_3h"),
    types.InlineKeyboardButton(text=_("6h"), callback_data="networkhist_6h"),
    types.InlineKeyboardButton(text=_("12h"), callback_data="networkhist_12h"),
    types.InlineKeyboardButton(text=_("1d"), callback_data="networkhist_1d"),
    types.InlineKeyboardButton(text=_("+"), callback_data="networkhistmore"))

networkhistmore = types.InlineKeyboardMarkup()
networkhistmore.row(
    types.InlineKeyboardButton(text=_("\U00002190"), callback_data="networkcheckhist"),
    types.InlineKeyboardButton(text=_("3d"), callback_data="networkhist_3d"),
    types.InlineKeyboardButton(text=_("5d"), callback_data="networkhist_5d"),
    types.InlineKeyboardButton(text=_("7d"), callback_data="networkhist_7d"),
    types.InlineKeyboardButton(text=_("14d"), callback_data="networkhist_14d"),
    types.InlineKeyboardButton(text=_("21d"), callback_data="networkhist_21d"),
    types.InlineKeyboardButton(text=_("30d"), callback_data="networkhist_30d"))
# Network

# Disk io
diskiocheckhist = types.InlineKeyboardMarkup()
diskiocheckhist.row(
    types.InlineKeyboardButton(text=_("30m"), callback_data="diskiohist_30m"),
    types.InlineKeyboardButton(text=_("1h"), callback_data="diskiohist_1h"),
    types.InlineKeyboardButton(text=_("3h"), callback_data="diskiohist_3h"),
    types.InlineKeyboardButton(text=_("6h"), callback_data="diskiohist_6h"),
    types.InlineKeyboardButton(text=_("12h"), callback_data="diskiohist_12h"),
    types.InlineKeyboardButton(text=_("1d"), callback_data="diskiohist_1d"),
    types.InlineKeyboardButton(text=_("+"), callback_data="diskiohistmore"))

diskiohistmore = types.InlineKeyboardMarkup()
diskiohistmore.row(
    types.InlineKeyboardButton(text=_("\U00002190"), callback_data="diskiocheckhist"),
    types.InlineKeyboardButton(text=_("3d"), callback_data="diskiohist_3d"),
    types.InlineKeyboardButton(text=_("5d"), callback_data="diskiohist_5d"),
    types.InlineKeyboardButton(text=_("7d"), callback_data="diskiohist_7d"),
    types.InlineKeyboardButton(text=_("14d"), callback_data="diskiohist_14d"),
    types.InlineKeyboardButton(text=_("21d"), callback_data="diskiohist_21d"),
    types.InlineKeyboardButton(text=_("30d"), callback_data="diskiohist_30d"))
# Disk io


# InlineKeyboards

# F

# History load welcome
def historyget(f,t,lbl,ptitle,poutf,rm):
    try:
        bot.send_chat_action(config.user_id, "upload_photo")
        df = pd.read_csv(os.path.join(root_folder, f), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(minutes=t)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[12, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel(lbl)
        plt.title(ptitle)
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig(poutf)
        plt.close()
        load = open(poutf, 'rb')
        bot.send_message(config.user_id, text=_("History of {} {}".format(host_ip, host_name)))
        bot.send_photo(config.user_id, load, reply_markup=rm)
    except:
        bot.send_message(config.user_id, text = _("{] {} History load error".format(host_ip, host_name)))
# History load welcome

# History load welcome Time Diff
def historygettd(f,t,lbl,ptitle,poutf,rm):
    try:
        bot.send_chat_action(config.user_id, "upload_photo")
        df = pd.read_csv(os.path.join(root_folder, f), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = (df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(minutes=t)) & (df.iloc[:,1] < 0)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[12, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel(lbl)
        plt.title(ptitle)
        plt.grid(True)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig(poutf)
        plt.close()
        load = open(poutf, 'rb')
        bot.send_message(config.user_id, text=_("History of {} {}".format(host_ip, host_name)))
        bot.send_photo(config.user_id, load, reply_markup=rm)
    except:
        bot.send_message(config.user_id, text = _("{} {} History load error".format(host_ip, host_name)))
# History load welcome Time Diff

# History load welcome Ping
def historygetping(f,t,lbl,ptitle,poutf,rm):
    try:
        bot.send_chat_action(config.user_id, "upload_photo")
        df = pd.read_csv(os.path.join(root_folder, f), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(minutes=t)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[12, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel(lbl)
        plt.title(ptitle)
        plt.grid(True)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig(poutf)
        plt.close()
        load = open(poutf, 'rb')
        bot.send_message(config.user_id, text=_("History of {} {}".format(host_ip, host_name)))
        bot.send_photo(config.user_id, load, reply_markup=rm)
    except:
        bot.send_message(config.user_id, text = _("{} {} Ping History load error".format(host_ip, host_name)))
# History load welcome Ping

# History load welcome Network Bandwidth
def historygetnb(f,t,lbl,dptitle,uptitle,poutf,rm):
    try:
        bot.send_chat_action(config.user_id, "upload_photo")
        df = pd.read_csv(os.path.join(root_folder, f), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=t)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[12, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel(lbl)
        plt.title(dptitle)
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel(lbl)
        plt.title(uptitle)
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig(poutf)
        plt.close()
        load = open(poutf, 'rb')
        bot.send_message(config.user_id, text=_("History of {} {}".format(host_ip, host_name)))
        bot.send_photo(config.user_id, load, reply_markup=rm)
    except:
        bot.send_message(config.user_id, text = _("{} {} Ping History load error".format(host_ip, host_name)))
# History load welcome Network Bandwidth

# History load welcome Disk I/O
def historygetdio(f,t,lbl,rptitle,wptitle,poutf,rm):
    try:
        bot.send_chat_action(config.user_id, "upload_photo")
        df = pd.read_csv(os.path.join(root_folder, f), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024
        df.iloc[:,2] = df.iloc[:,2]/1024/1024
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=t)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[12, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel(lbl)
        plt.title(rptitle)
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel(lbl)
        plt.title(wptitle)
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig(poutf)
        plt.close()
        load = open(poutf, 'rb')
        bot.send_message(config.user_id, text=_("History of {} {}".format(host_ip, host_name)))
        bot.send_photo(config.user_id, load, reply_markup=rm)
    except:
        bot.send_message(config.user_id, text = _("{} {}Disk I/O Utilization history load error".format(host_ip, host_name)))
# History load welcome Disk I/O

# History load welcome
def historygetslowlog(f,t,lbl,ptitle,poutf,rm):
    try:
        bot.send_chat_action(config.user_id, "upload_photo")
        df = pd.read_csv(os.path.join(root_folder, f), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(minutes=t)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,2].loc[period]
        plt.figure(figsize=[12, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel(lbl)
        plt.title(ptitle)
        plt.grid(True)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig(poutf)
        plt.close()
        load = open(poutf, 'rb')
        bot.send_message(config.user_id, text=_("History of {} {}".format(host_ip, host_name)))
        bot.send_photo(config.user_id, load, reply_markup=rm)
    except:
        bot.send_message(config.user_id, text = _("{} {} History load error".format(host_ip, host_name)))
#/History load welcome


# CPU
@bot.message_handler(func=lambda message: message.text == lt_cpu)
def command_cpu(message):
    if message.from_user.id == config.user_id:
        try:
            sysload = str(psutil.getloadavg())
            cpuutil = str(psutil.cpu_percent(percpu=True))
            cpu = _("*System load (1,5,15 min):* _") + sysload + _("_\n*CPU utilization %:* _") + cpuutil + "_"
            bot.send_message(config.user_id, text=_("CPU of {} {}".format(host_ip, host_name)))
            bot.send_message(config.user_id, text=cpu, parse_mode="Markdown")
            historyget("db/cpuload.dat",30,_("Utilization"),_("CPU Utilization"),"/tmp/cpuload.png",cpuloadhist)
        except:
            bot.send_message(config.user_id, text=_("{} {} Can't get CPU info".format(host_ip, host_name)))
    else:
        pass
# /CPU

# RAM
@bot.message_handler(func=lambda message: message.text == lt_ram)
def command_ram(message):
    if message.from_user.id == config.user_id:
        try:
            ram = _("*RAM, Gb.*\n_Total: ") + str(subprocess.check_output(["free -mh | grep Mem | awk '{print $2}'"], shell = True,encoding='utf-8')) + _("Available: ") + str(subprocess.check_output(["free -mh | grep Mem | awk '{print $7}'"], shell = True,encoding='utf-8')) + _("Used: ") + str(subprocess.check_output(["free -mh | grep Mem | awk '{print $3}'"], shell = True,encoding='utf-8')) + "_"
            swap = _("*SWAP, Gb.*\n_Total: ") + str(subprocess.check_output(["free -mh | grep Swap | awk '{print $2}'"], shell = True,encoding='utf-8')) + _("Available: ") + str(subprocess.check_output(["free -mh | grep Swap | awk '{print $7}'"], shell = True,encoding='utf-8')) + _("Used: ") + str(subprocess.check_output(["free -mh | grep Swap | awk '{print $3}'"], shell = True,encoding='utf-8')) + "_"
            bot.send_message(config.user_id, text=_("RAM of {} {}".format(host_ip, host_name)))
            bot.send_message(config.user_id, text=ram + swap, parse_mode="Markdown")
            historyget("db/ramload.dat",30,_("Utilization"),_("RAM Utilization"),"/tmp/ramload.png",ramloadhist)
        except:
            bot.send_message(config.user_id, text=_("{} {} Can't get RAM info".format(host_ip, host_name)), parse_mode="Markdown")
    else:
        pass
# /RAM

# Disk
@bot.message_handler(func=lambda message: message.text == lt_disks)
def command_disk(message):
    if message.from_user.id == config.user_id:
        try:
            disk = str(subprocess.check_output(["df -h -t ext4"], shell = True,encoding='utf-8'))
            bot.send_message(config.user_id, text=_("Disk Info of {} {}".format(host_ip, host_name)))
            bot.send_message(config.user_id, text=disk, parse_mode="Markdown", reply_markup=markup)
        except:
            bot.send_message(config.user_id, text=_("{} {} Can't get disk info".format(host_ip, host_name)), parse_mode="Markdown", reply_markup=markup)
    else:
        pass
# /Disk


#######################################################
# Mina tools


# Node status
@bot.message_handler(func=lambda message: message.text == node_status)
def command_node_status(message):
    if message.from_user.id == config.user_id:
        try:
            cmd = config.node_status_command
            output = str(subprocess.check_output(cmd, shell=True, encoding='utf-8').rstrip())
            block_height = re.search(r'Block height:\s*\d+', output)
            max_observed_block_height = re.search(r'Max observed block height:\s*\d+', output)
            max_observed_unvalidated_block_height = re.search(r'Max observed unvalidated block height:\s*\d+', output)
            local_time = re.search(r'Local uptime:\s+.*', output)
            sync_status = re.search(r'Sync status:\s*(\w+|\w+\s*\w+)', output)
            output_string = str()
            for i in (block_height, max_observed_block_height, max_observed_unvalidated_block_height, local_time, sync_status):
                if i is not None:
                    output_string+='{}\n'.format(i.group(0))
            bot.send_message(config.user_id, text=_("Node Status of {} {}".format(host_ip, host_name)))
            bot.send_message(config.user_id, text=output_string, reply_markup=markupmina)
        except:
            bot.send_message(config.user_id, text=_("{} {} Can't get node status".format(host_ip, host_name)), reply_markup=markupmina)
    else:
        pass
# /Node status

# Block producer status
@bot.message_handler(func=lambda message: message.text == block_producer_status)
def command_block_status(message):
    if message.from_user.id == config.user_id:
        try:
            cmd = config.node_status_command
            output = str(subprocess.check_output(cmd, shell=True, encoding='utf-8').rstrip())
            block_time = re.search(r'Next block will be produced in:\s*.+', output)
            consensus_time_now = re.search(r'Consensus time now:\s*.+', output)
            output_string = str()
            for i in (block_time, consensus_time_now):
                if i is not None:
                    output_string += '{}\n'.format(i.group(0))
            bot.send_message(config.user_id, text=_("Block producer status of {} {}".format(host_ip, host_name)))
            bot.send_message(config.user_id, text=output_string, reply_markup=markupmina)
        except:
            bot.send_message(config.user_id, text=_("{} {} Can't get node status".format(host_ip, host_name)), reply_markup=markupmina)
    else:
        pass
# /Block producer status


# Restart node
@bot.message_handler(func=lambda message: message.text == restart_node)
def command_restart_node(message):
    if message.from_user.id == config.user_id:
        try:
            bot.send_message(config.user_id, text=_("Restart node status of {} {}. Do you really want to restart it?".format(host_ip, host_name)), reply_markup=restartmina)
        except:
            bot.send_message(config.user_id, text=_("{} {} Can't restart node".format(host_ip, host_name)), reply_markup=restartmina)
    else:
        pass
# /Restart node


# Restart node
@bot.message_handler(func=lambda message: message.text == exect_restart_status)
def command_restart_node(message):
    if message.from_user.id == config.user_id:
        try:
            cmd = config.restart_node_command
            output = str(subprocess.check_output(cmd, shell=True, encoding='utf-8').rstrip())
            bot.send_message(config.user_id, text=output, reply_markup=restartmina)
        except:
            bot.send_message(config.user_id, text=_("{} {} Can't restart node".format(host_ip, host_name)), reply_markup=restartmina)
    else:
        pass
# /Restart node

# Check sidecard logs
@bot.message_handler(func=lambda message: message.text == check_sidecard_logs)
def command_check_logs(message):
    if message.from_user.id == config.user_id:
        try:
            cmd = config.check_sidecard_logs_command
            output = str(subprocess.check_output(cmd, shell=True, encoding='utf-8').rstrip())
            bot.send_message(config.user_id, text=_("Sidecard logs of {} {}".format(host_ip, host_name)))
            bot.send_message(config.user_id, text=output, reply_markup=markupmina)
        except:
            bot.send_message(config.user_id, text=_("{} {} Can't get sidecard logs".format(host_ip, host_name)), reply_markup=markupmina)
    else:
        pass
# /Check sidecard logs


@bot.callback_query_handler(func = lambda call: True)
def inlinekeyboards(call):
    if call.from_user.id == config.user_id:
        # CPU graph
        if call.data == "cpuloadhist":
            bot.edit_message_reply_markup(config.user_id, message_id=call.message.message_id, reply_markup=cpuloadhist)
        if call.data == "cpuhistmore":
            bot.edit_message_reply_markup(config.user_id, message_id=call.message.message_id, reply_markup=cpuhistmore)
        if call.data == "cpuhist_30m":
            try:
                df = pd.read_csv(os.path.join(db_folder, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(minutes=30)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[12, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Utilization')
                plt.title('CPU Utilization')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/cpuload.png')
                plt.close()
                cpuload_1h = open('/tmp/cpuload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_1h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuloadhist)
            except:
                bot.send_message(config.user_id, text = _("CPU Utilization history load error"))
        if call.data == "cpuhist_1h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=1)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[15, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Utilization')
                plt.title('CPU Utilization')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/cpuload.png')
                plt.close()
                cpuload_1h = open('/tmp/cpuload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_1h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuloadhist)
            except:
                bot.send_message(config.user_id, text = _("CPU Utilization history load error"))
        if call.data == "cpuhist_3h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=3)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Utilization')
                plt.title('CPU Utilization')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/cpuload.png')
                plt.close()
                cpuload_3h = open('/tmp/cpuload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_3h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuloadhist)
            except:
                bot.send_message(config.user_id, text = _("CPU Utilization history load error"))
        if call.data == "cpuhist_6h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=6)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Utilization')
                plt.title('CPU Utilization')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/cpuload.png')
                plt.close()
                cpuload_6h = open('/tmp/cpuload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_6h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuloadhist)
            except:
                bot.send_message(config.user_id, text = _("CPU Utilization history load error"))
        if call.data == "cpuhist_12h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=12)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Utilization')
                plt.title('CPU Utilization')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/cpuload.png')
                plt.close()
                cpuload_12h = open('/tmp/cpuload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_12h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuloadhist)
            except:
                bot.send_message(config.user_id, text = _("CPU Utilization history load error"))
        if call.data == "cpuhist_1d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=24)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Utilization')
                plt.title('CPU Utilization')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/cpuload.png')
                plt.close()
                cpuload_1d = open('/tmp/cpuload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_1d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuloadhist)
            except:
                bot.send_message(config.user_id, text = _("CPU Utilization history load error"))
        if call.data == "cpuhist_3d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=72)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Utilization')
                plt.title('CPU Utilization')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/cpuload.png')
                plt.close()
                cpuload_3d = open('/tmp/cpuload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_3d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuhistmore)
            except:
                bot.send_message(config.user_id, text = _("CPU Utilization history load error"))
        if call.data == "cpuhist_5d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=120)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Utilization')
                plt.title('CPU Utilization')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/cpuload.png')
                plt.close()
                cpuload_5d = open('/tmp/cpuload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_5d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuhistmore)
            except:
                bot.send_message(config.user_id, text = _("CPU Utilization history load error"))
        if call.data == "cpuhist_7d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=168)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Utilization')
                plt.title('CPU Utilization')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/cpuload.png')
                plt.close()
                cpuload_7d = open('/tmp/cpuload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_7d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuhistmore)
            except:
                bot.send_message(config.user_id, text = _("CPU Utilization history load error"))
        if call.data == "cpuhist_14d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=336)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Utilization')
                plt.title('CPU Utilization')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/cpuload.png')
                plt.close()
                cpuload_14d = open('/tmp/cpuload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_14d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuhistmore)
            except:
                bot.send_message(config.user_id, text = _("CPU Utilization history load error"))
        if call.data == "cpuhist_21d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=504)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Utilization')
                plt.title('CPU Utilization')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/cpuload.png')
                plt.close()
                cpuload_21d = open('/tmp/cpuload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_21d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuhistmore)
            except:
                bot.send_message(config.user_id, text = _("CPU Utilization history load error"))
        if call.data == "cpuhist_30d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=720)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Utilization')
                plt.title('CPU Utilization')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/cpuload.png')
                plt.close()
                cpuload_30d = open('/tmp/cpuload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_30d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuhistmore)
                bot.send
            except:
                bot.send_message(config.user_id, text = _("CPU Utilization history load error"))
        # CPU graph

        # RAM graph
        if call.data == "ramloadhist":
            bot.edit_message_reply_markup(config.user_id, message_id=call.message.message_id, reply_markup=ramloadhist)
        if call.data == "ramhistmore":
            bot.edit_message_reply_markup(config.user_id, message_id=call.message.message_id, reply_markup=ramhistmore)
        if call.data == "ramhist_30m":
            try:
                df = pd.read_csv(os.path.join(db_folder, "ramload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(minutes=30)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[12, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Load')
                plt.title('RAM Load')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/ramload.png')
                plt.close()
                ramload_30m = open('/tmp/ramload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_30m),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramloadhist)
            except:
                bot.send_message(config.user_id, text = _("RAM Load history load error"))
        if call.data == "ramhist_1h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "ramload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=1)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[15, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Load')
                plt.title('RAM Load')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/ramload.png')
                plt.close()
                ramload_1h = open('/tmp/ramload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_1h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramloadhist)
            except:
                bot.send_message(config.user_id, text = _("RAM Load history load error"))
        if call.data == "ramhist_3h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "ramload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=3)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Load')
                plt.title('RAM Load')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/ramload.png')
                plt.close()
                ramload_3h = open('/tmp/ramload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_3h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramloadhist)
            except:
                bot.send_message(config.user_id, text = _("RAM Load history load error"))
        if call.data == "ramhist_6h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "ramload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=6)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Load')
                plt.title('RAM Load')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/ramload.png')
                plt.close()
                ramload_6h = open('/tmp/ramload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_6h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramloadhist)
            except:
                bot.send_message(config.user_id, text = _("RAM Load history load error"))
        if call.data == "ramhist_12h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "ramload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=12)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Load')
                plt.title('RAM Load')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/ramload.png')
                plt.close()
                ramload_12h = open('/tmp/ramload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_12h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramloadhist)
            except:
                bot.send_message(config.user_id, text = _("RAM Load history load error"))
        if call.data == "ramhist_1d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "ramload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=24)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Load')
                plt.title('RAM Load')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/ramload.png')
                plt.close()
                ramload_1d = open('/tmp/ramload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_1d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramloadhist)
            except:
                bot.send_message(config.user_id, text = _("RAM Load history load error"))
        if call.data == "ramhist_3d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "ramload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=72)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Load')
                plt.title('RAM Load')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/ramload.png')
                plt.close()
                ramload_3d = open('/tmp/ramload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_3d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramhistmore)
            except:
                bot.send_message(config.user_id, text = _("RAM Load history load error"))
        if call.data == "ramhist_5d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "ramload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=120)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Load')
                plt.title('RAM Load')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/ramload.png')
                plt.close()
                ramload_5d = open('/tmp/ramload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_5d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramhistmore)
            except:
                bot.send_message(config.user_id, text = _("RAM Load history load error"))
        if call.data == "ramhist_7d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "ramload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=168)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Load')
                plt.title('RAM Load')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/ramload.png')
                plt.close()
                ramload_7d = open('/tmp/ramload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_7d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramhistmore)
            except:
                bot.send_message(config.user_id, text = _("RAM Load history load error"))
        if call.data == "ramhist_14d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "ramload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=336)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Load')
                plt.title('RAM Load')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/ramload.png')
                plt.close()
                ramload_14d = open('/tmp/ramload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_14d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramhistmore)
            except:
                bot.send_message(config.user_id, text = _("RAM Load history load error"))
        if call.data == "ramhist_21d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "ramload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=504)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Load')
                plt.title('RAM Load')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/ramload.png')
                plt.close()
                ramload_21d = open('/tmp/ramload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_21d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramhistmore)
            except:
                bot.send_message(config.user_id, text = _("RAM Load history load error"))
        if call.data == "ramhist_30d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "ramload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=720)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('Load')
                plt.title('RAM Load')
                plt.yticks(np.arange(0, 100, step=5))
                plt.grid(True)
                plt.ylim(top=100)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/ramload.png')
                plt.close()
                ramload_30d = open('/tmp/ramload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_30d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramhistmore)
                bot.send
            except:
                bot.send_message(config.user_id, text = _("RAM Load history load error"))
        # RAM graph

        # PING graph
        if call.data == "pingcheckhist":
            bot.edit_message_reply_markup(config.user_id, message_id=call.message.message_id, reply_markup=pingcheckhist)
        if call.data == "pinghistmore":
            bot.edit_message_reply_markup(config.user_id, message_id=call.message.message_id, reply_markup=pinghistmore)
        if call.data == "pinghist_30m":
            try:
                df = pd.read_csv(os.path.join(db_folder, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(minutes=30)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[12, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('ms')
                plt.title('Ping Check')
                plt.grid(True)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/pingcheck.png')
                plt.close()
                pingcheck_30m = open('/tmp/pingcheck.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_30m),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pingcheckhist)
            except:
                bot.send_message(config.user_id, text = _("Ping check history load error"))
        if call.data == "pinghist_1h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=1)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[15, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('ms')
                plt.title('Ping Check')
                plt.grid(True)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/pingcheck.png')
                plt.close()
                pingcheck_1h = open('/tmp/pingcheck.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_1h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pingcheckhist)
            except:
                bot.send_message(config.user_id, text = _("Ping check history load error"))
        if call.data == "pinghist_3h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=3)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('ms')
                plt.title('Ping Check')
                plt.grid(True)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/pingcheck.png')
                plt.close()
                pingcheck_3h = open('/tmp/pingcheck.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_3h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pingcheckhist)
            except:
                bot.send_message(config.user_id, text = _("Ping check history load error"))
        if call.data == "pinghist_6h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=6)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('ms')
                plt.title('Ping Check')
                plt.grid(True)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/pingcheck.png')
                plt.close()
                pingcheck_6h = open('/tmp/pingcheck.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_6h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pingcheckhist)
            except:
                bot.send_message(config.user_id, text = _("Ping check history load error"))
        if call.data == "pinghist_12h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=12)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('ms')
                plt.title('Ping Check')
                plt.grid(True)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/pingcheck.png')
                plt.close()
                pingcheck_12h = open('/tmp/pingcheck.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_12h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pingcheckhist)
            except:
                bot.send_message(config.user_id, text = _("Ping check history load error"))
        if call.data == "pinghist_1d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=24)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('ms')
                plt.title('Ping Check')
                plt.grid(True)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/pingcheck.png')
                plt.close()
                pingcheck_1d = open('/tmp/pingcheck.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_1d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pingcheckhist)
            except:
                bot.send_message(config.user_id, text = _("Ping check history load error"))
        if call.data == "pinghist_3d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=72)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('ms')
                plt.title('Ping Check')
                plt.grid(True)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/pingcheck.png')
                plt.close()
                pingcheck_3d = open('/tmp/pingcheck.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_3d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pinghistmore)
            except:
                bot.send_message(config.user_id, text = _("Ping check history load error"))
        if call.data == "pinghist_5d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=120)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('ms')
                plt.title('Ping Check')
                plt.grid(True)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/pingcheck.png')
                plt.close()
                pingcheck_5d = open('/tmp/pingcheck.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_5d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pinghistmore)
            except:
                bot.send_message(config.user_id, text = _("Ping check history load error"))
        if call.data == "pinghist_7d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=168)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('ms')
                plt.title('Ping Check')
                plt.grid(True)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/pingcheck.png')
                plt.close()
                pingcheck_7d = open('/tmp/pingcheck.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_7d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pinghistmore)
            except:
                bot.send_message(config.user_id, text = _("Ping check history load error"))
        if call.data == "pinghist_14d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=336)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('ms')
                plt.title('Ping Check')
                plt.grid(True)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/pingcheck.png')
                plt.close()
                pingcheck_14d = open('/tmp/pingcheck.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_14d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pinghistmore)
            except:
                bot.send_message(config.user_id, text = _("Ping check history load error"))
        if call.data == "pinghist_21d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=504)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('ms')
                plt.title('Ping Check')
                plt.grid(True)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/pingcheck.png')
                plt.close()
                pingcheck_21d = open('/tmp/pingcheck.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_21d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pinghistmore)
            except:
                bot.send_message(config.user_id, text = _("Ping check history load error"))
        if call.data == "pinghist_30d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=720)
                x = df.iloc[:,0].loc[period]
                y = df.iloc[:,1].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.xlabel('Time')
                plt.ylabel('ms')
                plt.title('Ping Check')
                plt.grid(True)
                plt.plot(x, y)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/pingcheck.png')
                plt.close()
                pingcheck_30d = open('/tmp/pingcheck.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_30d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pinghistmore)
                bot.send
            except:
                bot.send_message(config.user_id, text = _("Ping check history load error"))
        # PING graph

        # Network graph
        if call.data == "networkcheckhist":
            bot.edit_message_reply_markup(config.user_id, message_id=call.message.message_id, reply_markup=networkcheckhist)
        if call.data == "networkhistmore":
            bot.edit_message_reply_markup(config.user_id, message_id=call.message.message_id, reply_markup=networkhistmore)
        if call.data == "networkhist_30m":
            try:
                df = pd.read_csv(os.path.join(db_folder, "networkload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(minutes=30)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[12, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Upload speed')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Download speed')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/networkload.png')
                plt.close()
                networkload_1h = open('/tmp/networkload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_1h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkcheckhist)
            except:
                bot.send_message(config.user_id, text = _("Network Utilization history load error"))
        if call.data == "networkhist_1h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "networkload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=1)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[15, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Upload speed')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Download speed')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/networkload.png')
                plt.close()
                networkload_1h = open('/tmp/networkload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_1h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkcheckhist)
            except:
                bot.send_message(config.user_id, text = _("Network Utilization history load error"))
        if call.data == "networkhist_3h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "networkload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=3)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Upload speed')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Download speed')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/networkload.png')
                plt.close()
                networkload_3h = open('/tmp/networkload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_3h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkcheckhist)
            except:
                bot.send_message(config.user_id, text = _("Network Utilization history load error"))
        if call.data == "networkhist_6h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "networkload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=6)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Upload speed')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Download speed')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/networkload.png')
                plt.close()
                networkload_6h = open('/tmp/networkload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_6h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkcheckhist)
            except:
                bot.send_message(config.user_id, text = _("Network Utilization history load error"))
        if call.data == "networkhist_12h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "networkload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=12)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Upload speed')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Download speed')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/networkload.png')
                plt.close()
                networkload_12h = open('/tmp/networkload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_12h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkcheckhist)
            except:
                bot.send_message(config.user_id, text = _("Network Utilization history load error"))
        if call.data == "networkhist_1d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "networkload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=24)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Upload speed')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Download speed')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/networkload.png')
                plt.close()
                networkload_24h = open('/tmp/networkload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_24h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkcheckhist)
            except:
                bot.send_message(config.user_id, text = _("Network Utilization history load error"))
        if call.data == "networkhist_3d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "networkload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=72)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Upload speed')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Download speed')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/networkload.png')
                plt.close()
                networkload_72h = open('/tmp/networkload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_72h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkhistmore)
            except:
                bot.send_message(config.user_id, text = _("Network Utilization history load error"))
        if call.data == "networkhist_5d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "networkload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=120)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Upload speed')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Download speed')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/networkload.png')
                plt.close()
                networkload_120h = open('/tmp/networkload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_120h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkhistmore)
            except:
                bot.send_message(config.user_id, text = _("Network Utilization history load error"))
        if call.data == "networkhist_7d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "networkload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=168)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Upload speed')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Download speed')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/networkload.png')
                plt.close()
                networkload_168h = open('/tmp/networkload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_168h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkhistmore)
            except:
                bot.send_message(config.user_id, text = _("Network Utilization history load error"))
        if call.data == "networkhist_14d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "networkload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=336)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Upload speed')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Download speed')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/networkload.png')
                plt.close()
                networkload_336h = open('/tmp/networkload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_336h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkhistmore)
            except:
                bot.send_message(config.user_id, text = _("Network Utilization history load error"))
        if call.data == "networkhist_21d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "networkload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=504)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Upload speed')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Download speed')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/networkload.png')
                plt.close()
                networkload_504h = open('/tmp/networkload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_504h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkhistmore)
            except:
                bot.send_message(config.user_id, text = _("Network Utilization history load error"))
        if call.data == "networkhist_30d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "networkload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=720)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Upload speed')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('Mb/s')
                plt.title('Download speed')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/networkload.png')
                plt.close()
                networkload_720h = open('/tmp/networkload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_720h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkhistmore)
            except:
                bot.send_message(config.user_id, text = _("Network Utilization history load error"))
        # Network graph

        # diskio graph
        if call.data == "diskiocheckhist":
            bot.edit_message_reply_markup(config.user_id, message_id=call.message.message_id, reply_markup=diskiocheckhist)
        if call.data == "diskiohistmore":
            bot.edit_message_reply_markup(config.user_id, message_id=call.message.message_id, reply_markup=diskiohistmore)
        if call.data == "diskiohist_30m":
            try:
                df = pd.read_csv(os.path.join(db_folder, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024
                df.iloc[:,2] = df.iloc[:,2]/1024/1024
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(minutes=30)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[12, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Read')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Write')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/diskioload.png')
                plt.close()
                diskioload_1h = open('/tmp/diskioload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_1h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiocheckhist)
            except:
                bot.send_message(config.user_id, text = _("Disk I/O Utilization history load error"))
        if call.data == "diskiohist_1h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=1)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[15, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Read')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Write')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/diskioload.png')
                plt.close()
                diskioload_1h = open('/tmp/diskioload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_1h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiocheckhist)
            except:
                bot.send_message(config.user_id, text = _("Disk I/O Utilization history load error"))
        if call.data == "diskiohist_3h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=3)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Read')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Write')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/diskioload.png')
                plt.close()
                diskioload_3h = open('/tmp/diskioload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_3h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiocheckhist)
            except:
                bot.send_message(config.user_id, text = _("Disk I/O Utilization history load error"))
        if call.data == "diskiohist_6h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=6)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Read')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Write')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/diskioload.png')
                plt.close()
                diskioload_6h = open('/tmp/diskioload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_6h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiocheckhist)
            except:
                bot.send_message(config.user_id, text = _("Disk I/O Utilization history load error"))
        if call.data == "diskiohist_12h":
            try:
                df = pd.read_csv(os.path.join(db_folder, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=12)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Read')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Write')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/diskioload.png')
                plt.close()
                diskioload_12h = open('/tmp/diskioload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_12h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiocheckhist)
            except:
                bot.send_message(config.user_id, text = _("Disk I/O Utilization history load error"))
        if call.data == "diskiohist_1d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=24)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Read')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Write')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/diskioload.png')
                plt.close()
                diskioload_24h = open('/tmp/diskioload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_24h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiocheckhist)
            except:
                bot.send_message(config.user_id, text = _("Disk I/O Utilization history load error"))
        if call.data == "diskiohist_3d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=72)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[20, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Read')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Write')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/diskioload.png')
                plt.close()
                diskioload_72h = open('/tmp/diskioload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_72h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiohistmore)
            except:
                bot.send_message(config.user_id, text = _("Disk I/O Utilization history load error"))
        if call.data == "diskiohist_5d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=120)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Read')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Write')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/diskioload.png')
                plt.close()
                diskioload_120h = open('/tmp/diskioload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_120h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiohistmore)
            except:
                bot.send_message(config.user_id, text = _("Disk I/O Utilization history load error"))
        if call.data == "diskiohist_7d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=168)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Read')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Write')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/diskioload.png')
                plt.close()
                diskioload_168h = open('/tmp/diskioload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_168h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiohistmore)
            except:
                bot.send_message(config.user_id, text = _("Disk I/O Utilization history load error"))
        if call.data == "diskiohist_14d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=336)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Read')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Write')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/diskioload.png')
                plt.close()
                diskioload_336h = open('/tmp/diskioload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_336h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiohistmore)
            except:
                bot.send_message(config.user_id, text = _("Disk I/O Utilization history load error"))
        if call.data == "diskiohist_21d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=504)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Read')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Write')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/diskioload.png')
                plt.close()
                diskioload_504h = open('/tmp/diskioload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_504h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiohistmore)
            except:
                bot.send_message(config.user_id, text = _("Disk I/O Utilization history load error"))
        if call.data == "diskiohist_30d":
            try:
                df = pd.read_csv(os.path.join(db_folder, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
                df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
                df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
                df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
                period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=720)
                x = df.iloc[:,0].loc[period]
                y1 = df.iloc[:,1].loc[period]
                y2 = df.iloc[:,2].loc[period]
                plt.figure(figsize=[30, 9], dpi=100)
                plt.subplot(2, 1, 1)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Read')
                plt.grid(True)
                plt.plot(x, y1)
                plt.subplot(2, 1, 2)
                plt.xlabel('Time')
                plt.ylabel('MB/s')
                plt.title('Write')
                plt.grid(True)
                plt.plot(x, y2)
                plt.gcf().autofmt_xdate()
                plt.tight_layout()
                plt.savefig('/tmp/diskioload.png')
                plt.close()
                diskioload_720h = open('/tmp/diskioload.png', 'rb')
                bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_720h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiohistmore)
            except:
                bot.send_message(config.user_id, text = _("Disk I/O Utilization history load error"))
    # diskio graph
    else:
        pass

# /Menu tools
#######################################################


#######################################################
# Linux tools

# Linux tools start
@bot.message_handler(func=lambda message: message.text == lt_linuxtools)
def command_linuxtools(message):
    if message.from_user.id == config.user_id:
        bot.send_message(config.user_id, text=_("Be careful. Some processes need time. ") + "\U000023F3", reply_markup=markuplinux)
    else:
        pass
# /Linux tools start

# Mina tools start
@bot.message_handler(func=lambda message: message.text == lt_minatools)
def command_linuxtools(message):
    if message.from_user.id == config.user_id:
        bot.send_message(config.user_id, text=_("Be careful. Some processes need time. ") + "\U000023F3", reply_markup=markupmina)
    else:
        pass
# /Mina tools start

# restart start
@bot.message_handler(func=lambda message: message.text == restart_node)
def command_linuxtools(message):
    if message.from_user.id == config.user_id:
        bot.send_message(config.user_id, text=_("Node is restarting, check it's status"), reply_markup=restartmina)
    else:
        pass
# /restart start

# Ping test
@bot.message_handler(func=lambda message: message.text == lt_ping)
def command_pingcheck(message):
    if message.from_user.id == config.user_id:
        try:
            bot.send_chat_action(config.user_id, "typing")
            pingcheck = "ping -c 5 " + config.srvping
            pingcheck = str(subprocess.check_output(pingcheck, shell = True,encoding='utf-8'))
            bot.send_message(config.user_id, text=_("Ping test of {} {}".format(host_ip, host_name)))
            bot.send_message(config.user_id, text=pingcheck, reply_markup=markuplinux)
            historygetping("db/pingcheck.dat",30,_("ms"),_("Ping test"),"/tmp/pingcheck.png",pingcheckhist)
        except:
            bot.send_message(config.user_id, text=_("{} {} Can't execute ping test".format(host_ip, host_name)), reply_markup=markuplinux)
    else:
        pass
# /Ping test

# Top processes
@bot.message_handler(func=lambda message: message.text == lt_topproc)
def command_timediff(message):
    if message.from_user.id == config.user_id:
        try:
            topps = "ps -eo pid,ppid,user,start,%mem,pcpu,cmd --sort=-%mem | head"
            topps = str(subprocess.check_output(topps, shell = True,encoding='utf-8'))
            bot.send_message(config.user_id, text=_("Top processes of {} {}".format(host_ip, host_name)))
            bot.send_message(config.user_id, text=topps, reply_markup=markuplinux)
        except:
            bot.send_message(config.user_id, text=_("{} {} Can't get top processes".format(host_ip, host_name)), reply_markup=markuplinux)
    else:
        pass
# /Top processes

# Server start date/time
@bot.message_handler(func=lambda message: message.text == lt_starttime)
def command_srvstart(message):
    if message.from_user.id == config.user_id:
        try:
            startt = _("System start: ") + str(datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%b/%d/%Y %H:%M:%S"))
            bot.send_message(config.user_id, text=_("Server start time of {} {}".format(host_ip, host_name)))
            bot.send_message(config.user_id, text=startt, reply_markup=markuplinux)
        except:
            bot.send_message(config.user_id, text=_("{} {} Can't get system start date".format(host_ip, host_name)), reply_markup=markuplinux)
    else:
        pass
# /Server start date/time

# Current network load
@bot.message_handler(func=lambda message: message.text == lt_currntwrkload)
def command_currntwrkload(message):
    if message.from_user.id == config.user_id:
        try:
            bot.send_chat_action(config.user_id, "typing")
            currentloadn = psutil.net_io_counters()
            bytes_sent = getattr(currentloadn, 'bytes_sent')
            bytes_recv = getattr(currentloadn, 'bytes_recv')
            time.sleep(1)
            currentloadn1 = psutil.net_io_counters()
            bytes_sent1 = getattr(currentloadn1, 'bytes_sent')
            bytes_recv1 = getattr(currentloadn1, 'bytes_recv')
            sentspd = (bytes_sent1-bytes_sent)/1024/1024*8
            recvspd = (bytes_recv1-bytes_recv)/1024/1024*8
            sentspd = str((round(sentspd, 2)))
            recvspd = str((round(recvspd, 2)))
            bot.send_message(config.user_id, text=_("Network load of {} {}".format(host_ip, host_name)))
            bot.send_message(config.user_id, text=_("*Current network load\nIncoming:* _") + recvspd + _(" Mb/s_\n*Outgoing:* _") + sentspd + _(" Mb/s_"), parse_mode="Markdown", reply_markup=markuplinux)
            historygetnb("db/networkload.dat",0.5,_("Mb/s"),_("Upload"),_("Download"),"/tmp/networkload.png",networkcheckhist)
        except:
            bot.send_message(config.user_id, text=_("{} {} Can't get current network load".format(host_ip, host_name)), parse_mode="Markdown", reply_markup=markuplinux)
    else:
        pass
# /Current network load

# Disk I/O
@bot.message_handler(func=lambda message: message.text == lt_currntdiskload)
def command_currdiskload(message):
    if message.from_user.id == config.user_id:
        try:
            bot.send_chat_action(config.user_id, "typing")
            currentloadd = psutil.disk_io_counters()
            bytes_read = getattr(currentloadd, 'read_bytes')
            bytes_writ = getattr(currentloadd, 'write_bytes')
            time.sleep(1)
            currentloadd1 = psutil.disk_io_counters()
            bytes_read1 = getattr(currentloadd1, 'read_bytes')
            bytes_writ1 = getattr(currentloadd1, 'write_bytes')
            readio = (bytes_read1-bytes_read)/1024/1024
            writio = (bytes_writ1-bytes_writ)/1024/1024
            readio = str((round(readio, 2)))
            writio = str((round(writio, 2)))
            bot.send_message(config.user_id, text=_("Disk load of {} {}".format(host_ip, host_name)))
            bot.send_message(config.user_id, text=_("*Current disk load\nRead:* _") + readio + _(" MB/s_\n*Write:* _") + writio + _(" MB/s_"), parse_mode="Markdown")
            historygetdio("db/diskioload.dat",0.5,_("MB/s"),_("Read"),_("Write"),"/tmp/diskioload.png",diskiocheckhist)
        except:
            bot.send_message(config.user_id, text=_("{} {} Can't get current disk load".format(host_ip, host_name)), parse_mode="Markdown")
    else:
        pass
# /Disk I/O

# Mina ports listen check
@bot.message_handler(func=lambda message: message.text == lt_ssvalid)
def command_timediff(message):
  if message.from_user.id == config.user_id:
    try:
      ssmina = "ss -tlunp4 | grep -i ':{}'".format(config.port_to_check)
      ssmina = str(subprocess.check_output(ssmina, shell = True,encoding='utf-8'))
      bot.send_message(config.user_id, text=_("Port '{}' check of {} {}".format(config.port_to_check, host_ip, host_name)))
      bot.send_message(config.user_id, text=ssmina, reply_markup=markuplinux)
    except:
      bot.send_message(config.user_id, text=_("{} {} Can't check Mina '{}' port listening".format(host_ip, host_name, config.port_to_check)), reply_markup=markuplinux)
  else:
    pass
# /Mina ports listen check

# /Linux tools
#######################################################


# Main menu
@bot.message_handler(func=lambda message: message.text == lt_mainmenu)
def command_srvstart(message):
    if message.from_user.id == config.user_id:
        bot.send_message(config.user_id, text=_("Start menu"), reply_markup=markup)
    else:
        pass
# /Main menu

# Except proc kill
def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


# RAM Monitoring
def AlertsNotificationsRam():
    td = 0
    alrtprdmem = 5
    while True:
        if td == 5:
            try:
                td = 0
                memload = "free -m | grep Mem | awk '/Mem/{used=$3} /Mem/{total=$2} END {printf (used*100)/total}'"
                memload = str(subprocess.check_output(memload, shell = True, encoding='utf-8'))
                # History data
                with open(os.path.join(db_folder, "ramload.dat"), "a") as i:
                    i.write(str(int(time.time())) + ";" + memload + "\n")
                # Notification
                if int(float(memload)) >= config.memloadalarm:
                    if alrtprdmem in config.repeattimealarmsrv:
                        try:
                            bot.send_message(config.user_id, text="\U0001F6A8 " + _("{} {} High memory load!!! ".format(host_ip, host_name)) + memload + _("% I recommend you to restart your *validator* node "),  parse_mode="Markdown")
                        except:
                            pass
                        alrtprdmem +=5
                    else:
                        alrtprdmem +=5
                if int(float(memload)) < config.memloadalarm:
                    alrtprdmem = 5
                time.sleep(config.alerts_time_period)
                td += 5
            except:
                time.sleep(5)
                td += 5
        else:
            time.sleep(5)
            td += 5

# CPU Monitoring
def AlertsNotificationsCPU():
    td = 0
    alrtprdcpu = 5
    while True:
        if td == 5:
            try:
                td = 0
                cpuutilalert = str(psutil.cpu_percent())
                with open(os.path.join(db_folder, "cpuload.dat"), "a") as i:
                    i.write(str(int(time.time())) + ";" + cpuutilalert + "\n")
                if int(float(cpuutilalert)) >= config.cpuutilalarm:
                    if alrtprdcpu in config.repeattimealarmsrv:
                        try:
                            bot.send_message(config.user_id,"\U000026A1" + _("{} {} High CPU Utilization! ".format(host_ip, host_name)) + cpuutilalert + "%")
                        except:
                            pass
                        alrtprdcpu +=5
                    else:
                        alrtprdcpu +=5
                if int(float(cpuutilalert)) < config.cpuutilalarm:
                    alrtprdcpu = 5
                time.sleep(config.alerts_time_period)
                td += 5
            except:
                time.sleep(5)
                td += 5
        else:
            time.sleep(5)
            td += 5


def AlertsNotificationsping():
    td = 0
    alrtprdpng = 5
    while True:
        if td == 5:
            try:
                td = 0
                pingc = "ping -c 1 " + config.srvping + " | tail -1 | awk '{printf $4}' | cut -d '/' -f 1 | tr -d $'\n'"
                pingc = str(subprocess.check_output(pingc, shell = True, encoding='utf-8'))
                with open(os.path.join(db_folder, "pingcheck.dat"), "a") as i:
                    i.write(str(int(time.time())) + ";" + pingc + "\n")
                if int(float(pingc)) >= config.pingcalarm:
                    if alrtprdpng in config.repeattimealarmsrv:
                        try:
                            bot.send_message(config.user_id,"\U000026A1 " + _("{} {} High ping! ".format(host_ip, host_name)) + pingc + " ms")
                        except:
                            pass
                        alrtprdpng +=5
                    else:
                        alrtprdpng +=5
                if int(float(pingc)) < config.pingcalarm:
                    alrtprdpng = 5
                time.sleep(config.alerts_time_period)
                td += 5
            except:
                time.sleep(5)
                td += 5
        else:
            time.sleep(5)
            td += 5



def monitoringnetwork():
    td = 0
    while True:
        if td == 5:
            td = 0
            try:
                currentloadn = psutil.net_io_counters()
                bytes_sent = getattr(currentloadn, 'bytes_sent')
                bytes_recv = getattr(currentloadn, 'bytes_recv')
                time.sleep(config.alerts_time_period)
                currentloadn1 = psutil.net_io_counters()
                bytes_sent1 = getattr(currentloadn1, 'bytes_sent')
                bytes_recv1 = getattr(currentloadn1, 'bytes_recv')
                sentspd = (bytes_sent1-bytes_sent)
                recvspd = (bytes_recv1-bytes_recv)
                with open(os.path.join(db_folder, "networkload.dat"), "a") as i:
                    i.write(str(int(time.time())) + ";" + str(int(sentspd)) + ";" + str(int(recvspd)) + "\n")
            except:
                pass
        else:
            time.sleep(4)
            td += 5

def monitoringdiskio():
    td = 0
    while True:
        if td == 5:
            td = 0
            try:
                currentloadd = psutil.disk_io_counters()
                bytes_read = getattr(currentloadd, 'read_bytes')
                bytes_writ = getattr(currentloadd, 'write_bytes')
                time.sleep(config.alerts_time_period)
                currentloadd1 = psutil.disk_io_counters()
                bytes_read1 = getattr(currentloadd1, 'read_bytes')
                bytes_writ1 = getattr(currentloadd1, 'write_bytes')
                readio = (bytes_read1-bytes_read)
                writio = (bytes_writ1-bytes_writ)
                readio = str((round(readio, 2)))
                writio = str((round(writio, 2)))
                with open(os.path.join(db_folder, "diskioload.dat"), "a") as i:
                    i.write(str(int(time.time())) + ";" + str(int(readio)) + ";" + str(int(writio)) + "\n")
            except:
                pass
        else:
            time.sleep(4)
            td += 5


# Node status Monitoring
def AlertsNotificationsNodeStatus():
    while True:
        try:
            cmd = config.node_status_command
            output = str(subprocess.check_output(cmd, shell=True, encoding='utf-8').rstrip())
            sync_status = re.search(r'Sync status:\s*(\w+|\w+\s*\w+)', output)
            if sync_status:
                if 'synced' not in sync_status.group(0).lower():
                    current_status = sync_status.group(0).replace('Sync status:', '').strip()
                    bot.send_message(config.user_id, text="\U0001F6A8 " + _("Alert! Your node status is now '{}'!".format(current_status)), parse_mode="Markdown")
            time.sleep(config.alerts_time_period)
        except:
            time.sleep(5)

# Block difference Monitoring
def AlertsNotificationsBlocksDifference():
    while True:
        try:
            cmd = config.node_status_command
            output = str(subprocess.check_output(cmd, shell=True, encoding='utf-8').rstrip())
            block_height = re.search(r'Block height:\s*(\d+)', output)
            max_observed_block_height = re.search(r'Max observed block height:\s*(\d+)', output)
            max_observed_unvalidated_block_height = re.search(r'Max observed unvalidated block height:\s*(\d+)', output)
            sync_status = re.search(r'Sync status:\s*(\w+|\w+\s*\w+)', output)
            int_block_height = 0
            int_max_observed_block_height = 0
            int_max_observed_unvalidated_block_height = 0
            if block_height:
                int_block_height = int(block_height.group(1))
            if max_observed_block_height:
                int_max_observed_block_height = int(max_observed_block_height.group(1))
            if max_observed_unvalidated_block_height:
                int_max_observed_unvalidated_block_height = int(max_observed_unvalidated_block_height.group(1))
            if any(abs(int_block_height - x) > config.allowed_block_difference for x in (int_max_observed_block_height, int_max_observed_unvalidated_block_height)) \
                    and not 'synced' not in sync_status.group(0).lower():
                bot.send_message(config.user_id,
                                 text="\U0001F6A8 " + _("Block heights are different!\n"
                                                        "Block height: {}\n"
                                                        "Max observed block heigh: {}\n"
                                                        "Max observed unvalidated block height: {}".format(int_block_height, int_max_observed_block_height, int_max_observed_unvalidated_block_height)),
                                 parse_mode="Markdown")
            time.sleep(config.alerts_time_period)
        except:
            time.sleep(5)


if __name__ == '__main__':
    if config.cfgmonitoring_node_status == 1:
        AlertsNotificationsNodeStatus = threading.Thread(target = AlertsNotificationsNodeStatus)
        AlertsNotificationsNodeStatus.start()

    if config.cfgmonitoring_block_difference == 1:
        AlertsNotificationsBlocksDifference = threading.Thread(target = AlertsNotificationsBlocksDifference)
        AlertsNotificationsBlocksDifference.start()

    if config.cfgAlertsNotificationsRam == 1:
        AlertsNotificationsRam = threading.Thread(target = AlertsNotificationsRam)
        AlertsNotificationsRam.start()

    if config.cfgAlertsNotificationsCPU == 1:
        AlertsNotificationsCPU = threading.Thread(target = AlertsNotificationsCPU)
        AlertsNotificationsCPU.start()

    if config.cfgmonitoringnetwork == 1:
        monitoringnetwork = threading.Thread(target = monitoringnetwork)
        monitoringnetwork.start()

    if config.cfgAlertsNotificationsping == 1:
        AlertsNotificationsping = threading.Thread(target = AlertsNotificationsping)
        AlertsNotificationsping.start()

    if config.cfgmonitoringdiskio == 1:
        monitoringdiskio = threading.Thread(target = monitoringdiskio)
        monitoringdiskio.start()
    else:
        pass
        # /Alerts monitoringadnlkey

    if config.cfgAlertsNotificationsping == 1:
        AlertsNotificationsping = threading.Thread(target=AlertsNotificationsping)
        AlertsNotificationsping.start()

    if config.cfgmonitoringdiskio == 1:
        monitoringdiskio = threading.Thread(target=monitoringdiskio)
        monitoringdiskio.start()

    else:
        pass
    # /Alerts monitoringadnlkey

    while True:
        try:
            bot.polling(none_stop=True, timeout=10)  # constantly get messages from Telegram
        except:
            bot.stop_polling()
            time.sleep(5)
