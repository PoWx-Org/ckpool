import os

from parse import *
import json



from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException





logDir = os.path.join("..", "logs")
logPath = os.path.join(logDir, "ckpool.log")


confPath=os.path.join("..", "ckpool.conf")

configures = dict()
with open(confPath,'r') as conf_file:
    conf_text = conf_file.read()
    conf_text = conf_text.split("Comments from here on are ignored.")[0]
    configures = json.loads(conf_text)

print(configures)
rpc_url = configures['btcd'][0]['url']
rpc_auth = configures['btcd'][0]['auth']
rpc_pass = configures['btcd'][0]['pass']

rpc_connection = AuthServiceProxy(f"http://{rpc_auth}:{rpc_pass}@{rpc_url}")



if os.path.isfile(logPath):
    print(f"path {logPath} is a file, everyhting ok")
else:
    print(f"paht {logPath} is not a file!")
    exit(0)

def found_block(line):
    print("Block found, doing something usefull")
    block_number = parse("[{time:ti}] Solved and confirmed block {height:d} {}", line)
    print(block_number)
    read_shares()
    height = block_number['height']
    block_hash = rpc_connection.getblockhash(block_number)
    block_info = rpc_connection.getblock(block_number, 3)
    print(blockinfo)

def read_shares():
    usersDir = os.path.join(logDir, 'users')
    print(usersDir)
    print(os.listdir(usersDir))
    for user in os.listdir(usersDir):
        user_file_path = os.path.join(usersDir, user)
        print(user_file_path)
        with open(user_file_path,'r') as user_file:
            cur_stat = user_file.read()
            info = json.loads(cur_stat)
            print(info)


with open(logPath,'r') as infile:
    lines = infile.readlines()
    while True:
        lines = infile.readlines()
        if len(lines) > 0:
            for line in lines:
                print( line.rstrip())
                if 'Solved and confirmed block' in line:
                    found_block(line)
