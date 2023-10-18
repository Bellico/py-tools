#!/usr/bin/env python3
import os
import paramiko
import logging
from time import sleep
RED = '\033[31m'
GREEN = '\033[32m'
GREENB = '\033[32m\033[1m'
YELLOW = '\033[33m'
EC = '\033[0m'

IP_LIST_FILE = r"ip.txt"
COMMAND_LIST_FILE = r"commands.txt"
LOG_FILE = r"log.txt"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', filemode='a')
logger = logging.getLogger()

# Check if the files exist
if not os.path.exists(IP_LIST_FILE):
    print(IP_LIST_FILE, "is not found. Please verify path ou create it")
    exit(0)

if not os.path.exists(COMMAND_LIST_FILE):
    print(COMMAND_LIST_FILE, "not found")
    exit(0)

with open(IP_LIST_FILE) as f:
    ip_list = [ip.strip() for ip in f.readlines()]
    f.close()

with open(COMMAND_LIST_FILE) as f:
    command_list = [c.strip() for c in f.readlines()]
    f.close()


def get_ssh_shell_client(ip):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username="toto", password="toto")
    #client.connect(ip, username='azureuser', key_filename='fmradius_key.pem')
    return client.invoke_shell()


for ip in ip_list:
    try:
        shell = get_ssh_shell_client(ip)
        print(GREEN + 'Successfully connected to', ip, EC)
        logger.info("Successfully connected to " + ip)

        # Send commands
        for command in command_list:
            print(GREENB + ip + EC, ':', command)
            shell.send(command + '\n')

        output = ""
        while not shell.recv_ready():
            sleep(0.5)

        while shell.recv_ready():
            output += shell.recv(4096).decode("utf-8")

        print(output)

    except Exception as inst:
        logger.error("Failed to connect to " + ip + " => " + str(inst))
        continue


