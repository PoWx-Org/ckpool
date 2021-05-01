import os

from parse import *
import json
from utils import get_reward
from dbutils import PoolConnector
from rpcutils import RpcConnector
import pandas as pd
import numpy as np
from threading import Thread, Event
import utils
############################### TODO: try to avoin warnings in some way about pandas tables 
import warnings
warnings.filterwarnings("ignore")


scriptPath = os.path.dirname(os.path.realpath(__file__))
logPrintPath=os.path.join(scriptPath, "..", "logs")
from pathlib import Path
Path(logPrintPath).mkdir(parents=True, exist_ok=True)
logPrintPath=os.path.join(logPrintPath, "accounter.log")

PRINT_PERIOD = 120

def print_log(*args):
    utils.print_log(*args, filename=logPrintPath)

print_log("reading confgs...")

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
print_log('creating database or connecting to existing one...')
pool_con = PoolConnector(logPrintPath)
rpc_connector = RpcConnector(pool_configures, logPrintPath)

############ Check if logs exist
if os.path.isfile(logPath):
    print_log(f"path {logPath} is a file, will try to parse it...")
else:
    print_log(f"path {logPath} is not a file!")
    exit(0)


#### Function what to do in case block is found

def found_block(line):
    print_log("Block found, doing something usefull")
    parsed_info = parse("[{time:ti}] Solved and confirmed block {height:d}{}", line)
    print_log(parsed_info)
    height = parsed_info['height']
    block_hash = rpc_connector.request_rpc("getblockhash", [height])
    block_info = rpc_connector.request_rpc("getblock", [block_hash, 3])
    reward = get_reward(block_info, reward_addr)
    share_stats = read_shares()
    pool_con.add_mined_block(block_hash, str(parsed_info['time']), height, reward)
    block_id = pool_con.get_block_id_by_hash(block_hash)
    pool_con.set_stats(block_id, share_stats)
    print_log(share_stats)
    print_log(f"Reward: {reward}")


######## Get current share statistics about users
######## TODO: check if current shares account difficulty
def read_shares():
    share_stats = dict()
    usersDir = os.path.join(logDir, 'users')
    print_log(usersDir)
    print_log(os.listdir(usersDir))
    for user in os.listdir(usersDir):
        user_file_path = os.path.join(usersDir, user)
        print_log(user_file_path)
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
        self.print_period = 1 if (PRINT_PERIOD //  CHECKLOGS_PERIOD) == 0 else PRINT_PERIOD // CHECKLOGS_PERIOD
        ############## TODO: do something if file is too big. Make file cleaning
        with open(logPath,'w') as infile:
            infile.write("")

    def run(self):
        while not self.stopped.wait(CHECKLOGS_PERIOD):
            try:
                self.counter += 1
                if (self.counter % self.print_period) == 0:
                    print_log(f'checked logs {self.print_period} times')
                with open(logPath,'r') as infile:
                    lines = infile.readlines()
                    if len(lines) > 0:
                        for line in lines:
                            if 'Solved and confirmed block' in line:
                                try:
                                    found_block(line)
                                except Exception as e:
                                    print_log(f"Ecxception \n{str(e)}\n occured during handling line:\n {line}\n")
                                    raise e
            except Exception as e:
                print(f"Exception \n{str(e)} \nin parser thread" )
            with open(logPath,'w') as infile:
                infile.write("")

stopFlag = Event()
parser_thread = ParserThread(stopFlag)
parser_thread.start()


