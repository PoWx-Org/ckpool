import os

from parse import *
import json
from utils import get_reward
from dbutils import PoolConnector
from rpcutils import RpcConnector
import pandas as pd
import numpy as np
from threading import Thread, Event

############################### TODO: try to avoin warnings in some way about pandas tables 
import warnings
warnings.filterwarnings("ignore")
 



print("reading confgs...")

scriptPath = os.path.dirname(os.path.realpath(__file__))
ckpoolDir = os.path.join(scriptPath, "..", "..", "..")

logDir = os.path.join(ckpoolDir, "logs")
logPath = os.path.join(logDir, "ckpool.log")


##### READ POOL CONFIGS
pool_conf_path=os.path.join(ckpoolDir, "ckpool.conf")
pool_configures = dict()
with open(pool_conf_path,'r') as pool_conf_file:
    conf_text = pool_conf_file.read()
    conf_text = conf_text.split("Comments from here on are ignored.")[0]
    pool_configures = json.loads(conf_text)
rpc_url = pool_configures['btcd'][0]['url']
rpc_auth = pool_configures['btcd'][0]['auth']
rpc_pass = pool_configures['btcd'][0]['pass']
reward_addr = pool_configures['btcaddress']


configures = pool_configures['parser']
MATURITY = configures['maturity']
CHECKMATURE_PERIOD = configures['checkmature_period']
CHECKLOGS_PERIOD = configures['checklogs_period']




############# Connecting to the database
############# TODO: give configs as parameter instead of read it in dbutils
print('creating database or connecting to existing one...')
pool_con = PoolConnector()
rpc_connector = RpcConnector(pool_configures)

############ Check if logs exist
if os.path.isfile(logPath):
    print(f"path {logPath} is a file, will try to parse it...")
else:
    print(f"path {logPath} is not a file!")
    exit(0)


#### Function what to do in case block is found

def found_block(line):
    print("Block found, doing something usefull")
    parsed_info = parse("[{time:ti}] Solved and confirmed block {height:d} {}", line)
    print(parsed_info)
    read_shares()
    height = parsed_info['height']
    block_hash = rpc_connector.request_rpc("getblockhash", [height])
    block_info = rpc_connector.request_rpc("getblock", [block_hash, 3])
    reward = get_reward(block_info, reward_addr)
    share_stats = read_shares()
    pool_con.add_mined_block(block_hash, str(parsed_info['time']), height, reward)
    block_id = pool_con.get_block_id_by_hash(block_hash)
    pool_con.set_stats(block_id, share_stats)
    print(share_stats)
    print(f"Reward: {reward}")


######## Get current share statistics about users
######## TODO: check if current shares account difficulty
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
            share_stats.update({user: shares})
    return share_stats
        




###### Parsing thread
class ParserThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event
        self.counter = 0
        self.print_period = 1 if (30 //  CHECKLOGS_PERIOD) == 0 else 30 //  CHECKLOGS_PERIOD
        ############## TODO: do something if file is too big. Make file cleaning
        with open(logPath,'r') as infile:
            lines = infile.readlines()
            self.curs = infile.tell()

    def run(self):
        while not self.stopped.wait(CHECKLOGS_PERIOD):
            self.counter += 1
            if (self.counter % self.print_period) == 0:
                print(f'checked logs {self.print_period} times')
            with open(logPath,'r') as infile:
                infile.seek(self.curs)
                lines = infile.readlines()
                if len(lines) > 0:
                    for line in lines:
                        if 'Solved and confirmed block' in line:
                            try:
                                found_block(line)
                            except Exception as e:
                                print(f"Ecxception {e} occured during handling line:\n {line}\n")
                self.curs = infile.tell()

stopFlag = Event()
parser_thread = ParserThread(stopFlag)
parser_thread.start()


