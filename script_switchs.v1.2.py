#!/usr/bin/env python
import os
import paramiko
import time
RED = '\033[31m'
GREEN = '\033[32m'
GREENB = '\033[32m\033[1m'
YELLOW = '\033[33m'
EC = '\033[0m'
ENTER = "\n"

IP_LIST_FILE = r"ip.txt"
COMMAND_LIST_FILE = r"commands.txt"

# Check if the files exist
if not os.path.exists(IP_LIST_FILE):
    print(IP_LIST_FILE, "is not found. Please verify path ou create it")
    exit(0)

if not os.path.exists(COMMAND_LIST_FILE):
    print(COMMAND_LIST_FILE, "is not found. Please verify path ou create it")
    exit(0)

with open(IP_LIST_FILE) as f:
    ip_list = [ip.strip() for ip in f.readlines()]
    f.close()

command_list = []
with open(COMMAND_LIST_FILE) as f:
    for c in f.readlines():
        value = c.strip()

        if value.startswith('>>'):
            x = command_list[-1]
            command_list[-1].get('sub').append(value.removeprefix('>>'))
        else:
            command_list.append({'name': value, 'sub': []})

    f.close()


def get_ssh_client(ip):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #client.connect(ip, username="toto", password="toto")
    client.connect(ip, username='azureuser', key_filename='fmradius_key.pem')
    return client


def test_session(transport, c):
    sleeptime = 0.001
    outdata, errdata = '', ''

    chan = transport.open_session()
    #chan.settimeout(3 * 60 * 60)
    #chan.setblocking(0)
    chan.sendall(c + '\n')
    while True:  # monitoring process
        # Reading from output streams
        if chan.exit_status_ready():  # If completed
            break
        time.sleep(sleeptime)
    retcode = chan.recv_exit_status()
    chan.close()

    print(retcode)
    print(outdata)
    print(errdata)


for ip in ip_list:
    client = get_ssh_client(ip)
    transport = client.get_transport()
    print(GREEN + 'Successfully connected to', ip, EC)

    for command in command_list:
        print(GREENB + f'{transport.get_username()}@{ip}' + EC, ':', command.get('name'))

        stdin, stdout, stderr = client.exec_command(command.get('name'))

        for sub_name in command.get('sub'):
            stdin.write(f"{sub_name}{ENTER}")

        stdin.channel.shutdown_write()

        for line in stdout.readlines():
            print(' ' + line.strip())

        for line in stderr.readlines():
            print(RED + ' ' + line.strip())

    client.close()
    print(YELLOW + ip, 'connection closed', EC)
    print()


#for ip in ip_list:
#    client = get_ssh_client(ip)
#    shh = get_ssh_client_shell(client)
#    print(GREEN + 'Successfully connected to', ip, EC)
#
#    shh.send(f"python3{enter_key}")
#    shh.send(f"print('ok'){enter_key}")
#    shh.send(f"exit(){enter_key}")
#
#    router_output = shh.recv(10000).decode("utf-8")
#    print(router_output)

# print(f'Return code: {stdout.channel.recv_exit_status()}')
