import os

from parse import *
import json
from utils import get_reward
from dbutils import PoolConnector


from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
scriptPath = os.path.dirname(os.path.realpath(__file__))
ckpoolDir = os.path.join(scriptPath, "..", "..", "ckpool")

logDir = os.path.join(ckpoolDir, "logs")
logPath = os.path.join(logDir, "ckpool.log")

confPath=os.path.join(ckpoolDir, "ckpool.conf")

configures = dict()
with open(confPath,'r') as conf_file:
    conf_text = conf_file.read()
    conf_text = conf_text.split("Comments from here on are ignored.")[0]
    configures = json.loads(conf_text)

print(configures)
rpc_url = configures['btcd'][0]['url']
rpc_auth = configures['btcd'][0]['auth']
rpc_pass = configures['btcd'][0]['pass']
reward_addr = configures['btcaddress']
rpc_connection = AuthServiceProxy(f"http://{rpc_auth}:{rpc_pass}@{rpc_url}")

pool_con = PoolConnector

if os.path.isfile(logPath):
    print(f"path {logPath} is a file, everyhting ok")
else:
    print(f"paht {logPath} is not a file!")
    exit(0)



def found_block(line):
    print("Block found, doing something usefull")
    parsed_info = parse("[{time:ti}] Solved and confirmed block {height:d} {}", line)
    print(parsed_info)
    read_shares()
    height = parsed_info['height']
    block_hash = rpc_connection.getblockhash([height])
    block_info = rpc_connection.getblock([block_hash, 3])
    reward = get_reward(block_info, reward_addr)
    share_stats = read_shares()
    pool_con.add_mined_block(block_hash, str(parsed_info['time']), height, reward)
    print(share_stats)
    print(f"Reward: {reward}")




def read_shares():
    share_stats = dict()
    usersDir = os.path.join(logDir, 'users')
    print(usersDir)
    print(os.listdir(usersDir))
    for user in os.listdir(usersDir):
        user_file_path = os.path.join(usersDir, user)
        print(user_file_path)
        with open(user_file_path,'r') as user_file:
            cur_stat = user_file.read()
            info = json.loads(cur_stat)
            shares = info['shares']
            share_stats.update(user, shares)
    return share_stats
        





with open(logPath,'r') as infile:
    lines = infile.readlines()
    while True:
        lines = infile.readlines()
        if len(lines) > 0:
            for line in lines:
                if 'Solved and confirmed block' in line:
                    found_block(line)
