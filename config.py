#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ##### TONTgBot Config
# Edit starts here
api_key = '' # API Keythat you get from @BotFather
user_id =  # Your id, you can get it by sending command /id to bot @TONTgIDBot
port_to_check = 80 # Port number which you want to check that it is listening
disk_folder = '/home' # Folder to check disk size in 'Disk' check
hostname = 'Server1' # Hostname used to print it in messages

node_status_command = 'docker exec mina mina client status'
restart_node_command = 'docker restart mina'
check_sidecard_logs_command = 'sudo docker logs --follow mina-sidecar -f --tail 50'
# Edit ends here


# Other
elogc = '250' # Row count for the error log
slogc = '250' # Row count for the slow log

srvping = '1.1.1.1' # Ping test server

nodelogressave = 1 # Save node.log before restart with TONTgBot

# Alarms
memloadalarm = 90 # RAM Utilization alarm starts at
pingcalarm = 20 # When ping will be more than X ms, you will get alarm.
cpuutilalarm = 90 # CPU Utilization alarm starts at
minstakes = 10001 # Min Stake
balchecks = 1800 # How often to check your balance, in seconds. 300 = 5 min, 1200 = 20min, 3600 = 1 hour.
stakecheck = 60 # Stake check every minute
stakesendcheck = 9000 # When first stake send check do after election stars. 1800=30min after election start, 3600 = 1hour, 7200 = 2 hours, 9000 = 2.5 hours
repeattimealarmtd = [5,15,25,30,60,90,120,180,320, 640, 1280, 2560, 5120, 10240, 20480, 40960, 81920] # Notify every x second about time diff check failed
repeattimealarmnode = [5,15,25,30,60,90,120,180,320, 640, 1280, 2560, 5120, 10240, 20480, 40960, 81920] # Notify every x second about validator node down
repeattimealarmsrv = [5,15,25,30,60,90,120,180,320, 640, 1280, 2560, 5120, 10240, 20480, 40960, 81920] # Notify every x second about high CPU, RAM load and ping

# DB Scans
cfgAlertsNotifications = 1 # Validator engine Monitopring
cfgAlertsNotificationsRam = 1 # RAM Monitoring + history
cfgAlertsNotificationsCPU = 1 # CPU Monitoring + history
cfgAlertsNotificationst = 1 # Time Diff Monitopring
cfgmonitoringnetwork = 1 # Netowrk Monitopring
cfgAlertsNotificationsping = 1 # RAM, Ping & CPU Monitopring
cfgmonitoringdiskio = 1 # Disk I/O Monitopring
cfgmonitoring_node_status = 1

cfgmonitoring_block_difference = 1
allowed_block_difference = 5

alerts_time_period = 300 # time slot for alerts sending
# ##### /TONTgBot Config
