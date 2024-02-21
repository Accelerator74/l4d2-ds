import sys
import socket
import time
import os
import urllib.request
import json
from subprocess import check_output

server_adr = "127.0.0.1:27015"
server_dir = "~/srcds"
screen_name = "SRCDS"
game_dir = "left4dead2"
steamcmd_dir = "~/steamcmd"

def socket_query(ip, port):
    response = None
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(5)
    try:
        s.connect((ip,port))
    except:
        response = None
    else:
        s.send(b'\xFF\xFF\xFF\xFFTSource Engine Query\0')
    try:
        response = s.recv(1024)
    except socket.error:
        response = None
    s.close()
    return response

def UpToDateCheck(dir, subdir):
    appid = 0
    patch_version = 0
    up_to_date = True
    with open(os.path.join(dir, 'steam_appid.txt'), 'r') as file:
        appid = int(file.readline().strip())
    with open(os.path.join(dir, subdir, 'steam.inf'), 'r') as file:
        for line in file:
            key_value_pair = line.strip().split("=")
            if len(key_value_pair) == 2 and key_value_pair[0] == "PatchVersion":
                patch_version = int(key_value_pair[1].replace(".", ""))
                break
    if appid == 0 or patch_version == 0:
        return up_to_date
    params = {
        "appid": appid,
        "version": patch_version
    }
    url = "https://api.steampowered.com/ISteamApps/UpToDateCheck/v0001/?"+urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url) as response:
            json_data = json.loads(response.read().decode())
            if 'response' in json_data:
                response_data = json_data['response']
                if 'up_to_date' in response_data:
                    up_to_date = response_data['up_to_date']
    except urllib.error.URLError as e:
        up_to_date = True
    return up_to_date

if __name__ == '__main__':
    if not "."+screen_name+"\t(" in check_output(["screen -ls; true"],shell=True).decode('utf-8'):
        sys.exit(1)
    if UpToDateCheck(server_dir, game_dir) is False:
        file = open("watchdog.log", "a")
        file.write("[{}] {} server restarted for update\n".format(time.ctime(), server_adr))
        file.close()
        os.system("screen -S {} -X quit".format(screen_name))
        os.system("cd {} && ./update.sh".format(steamcmd_dir))
        sys.exit(1)
    ip,port = server_adr.split(":")
    result = None
    req = 0
    while True:
        result = socket_query(ip, int(port))
        req += 1
        if result is None and req < 5:
            if not "."+screen_name+"\t(" in check_output(["screen -ls; true"],shell=True).decode('utf-8'):
                sys.exit(1)
            time.sleep(10)
        else:
            break
    if result is None:
        file = open("watchdog.log", "a")
        file.write("[{}] {} server did not respond {} times\n".format(time.ctime(), server_adr, req))
        file.close()
        os.system("screen -S {} -X quit".format(screen_name))
        os.system("cd {} && ./start.sh".format(server_dir))