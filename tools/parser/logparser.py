import os

from parse import *
import json
from utils import get_reward
from dbutils import PoolConnector
import pandas as pd
import numpy as np
from threading import Thread, Event

############################### TODO: try to avoin warnings in some way about pandas tables 
import warnings
warnings.filterwarnings("ignore")




print("reading confgs...")

scriptPath = os.path.dirname(os.path.realpath(__file__))
ckpoolDir = os.path.join(scriptPath, "..", "..")

logDir = os.path.join(ckpoolDir, "logs")
logPath = os.path.join(logDir, "ckpool.log")


################## TODO: write all the configures in pool's configures
###### READ PARSER CONFIGS
conf_path=os.path.join(scriptPath, "parser.conf")
configures = dict()
with open(conf_path,'r') as conf_file:
    conf_text = conf_file.read()
    conf_text = conf_text.split("Comments from here on are ignored.")[0]
    configures = json.loads(conf_text)
MATURITY = configures['maturity']
CHECKMATURE_PERIOD = configures['checkmature_period']
CHECKLOGS_PERIOD = configures['checklogs_period']


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




########### Good request, reurns message if answer has no results
import requests
def request_rpc(method, params=[], verbosity=1):
    url = f"http://{rpc_url}/"
    payload = json.dumps({"method": method, "params": params})
    headers = {'content-type': "application/json", 'cache-control': "no-cache"}
    if verbosity >=2:
        print("trying to request")
        print("url", rpc_url)
        print('auth', (rpc_auth, rpc_pass)) 
        print('payload', payload)
        print('headers', headers)
    try:
        response = requests.request("POST", url, data=payload, headers=headers, auth=(rpc_auth, rpc_pass))
        if json.loads(response.text)['result'] is None:
            print(f'Got response result None for method {method}:\n{response}')
        return json.loads(response.text)['result']
    except requests.exceptions.RequestException as e:
        print(e)
    except Exception as e:
        print('No response from rpc, check optical Bitcoin is running on this machine')
        print(e)



############# Connecting to the database
############# TODO: give configs as paraeer instead of read it in dbutils
print('creating database or connecting to existing one...')
pool_con = PoolConnector()


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
    block_hash = request_rpc("getblockhash", [height])
    block_info = request_rpc("getblock", [block_hash, 3])
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
    def __init__(self, event, curs):
        Thread.__init__(self)
        self.stopped = event
        self.curs = curs
        self.counter = 0
        self.print_period = 1 if (30 //  CHECKLOGS_PERIOD) == 0 else 30 //  CHECKLOGS_PERIOD

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

print("creating log reading thread...")

##Event to stop parsing thread
stopFlag = Event()


############## TODO: do something if file is too big. Make file cleaning
with open(logPath,'r') as infile:
    lines = infile.readlines()
    curs = infile.tell()
parser_thread = ParserThread(stopFlag, curs)




#### Paying thread
class PayingThread(Thread):
    def __init__(self, event, connector):
        Thread.__init__(self)
        self.stopped = event
        self.connector = connector

    def run(self):
        print("checking mature blocks")
        check_mature_blocks(self.connector, MATURITY)
        while not self.stopped.wait(CHECKMATURE_PERIOD):
            print("checking mature blocks")
            check_mature_blocks(self.connector, MATURITY)
            pass

print("creating paying thread...")

stopFlag = Event()
payment_thread = PayingThread(stopFlag, pool_con)





def check_mature_blocks(connector, maturity=100):
    cur_height = request_rpc('getblockchaininfo')['blocks']
    blocks = connector.get_mature_blocks(cur_height=cur_height, maturity=maturity)
    print(blocks)
    for index, block_example in blocks.iterrows():
        answer = request_rpc('getblock', [block_example['hash']])

        if answer is None:
            print(f'Block {dict(block_example)} disappered!')
            print(answer) 
            connector.add_transaction(block_example['id'], 'null', 'disappeared', 'null')
            continue
        pay_stat = get_pay_info(block_example, connector)
        pay_for_block(block_example['id'],  pay_stat, connector)
        

def get_pay_info(block_example, connector):
    reward = block_example['reward']
    prev_block = connector.get_prev_block(block_example['id'])
    cur_shares = connector.get_shares(block_example['id'])
    if prev_block is None:
        shares_to_pay = cur_shares
    else:
        prev_shares = connector.get_shares(prev_block['id'])
        shares_diff = cur_shares.merge(prev_shares, how="left", on="user", suffixes=['_cur', '_prev']).fillna(0)
        shares_diff['shares'] = shares_diff['shares_cur'] - shares_diff['shares_prev']
        shares_to_pay = shares_diff[['user', 'shares']]
    

    all_shares = shares_to_pay['shares'].sum()

    if all_shares == 0:
        print("block mined with 0 shares spent, no payment")
        all_shares=1
    shares_to_pay['shares'] = (shares_to_pay['shares']* reward / all_shares).astype(float).round(8)
    shares_to_pay = shares_to_pay[shares_to_pay['shares'] != 0]
    shares_to_pay['valid_addr'] = shares_to_pay['user'].apply(validate_addr)
    print(shares_to_pay)
    shares_to_pay = shares_to_pay[shares_to_pay['valid_addr']]
    return shares_to_pay[['user', 'shares']]

def validate_addr(addr):
    answ = request_rpc('validateaddress', [addr])
    if answ is None:
        return False
    if not answ['isvalid']:
        print(f"Invalid address {addr}!")
    return answ['isvalid']

def pay_for_block(id_block, pay_stat, connector):
    if len(pay_stat) == 0:
        print('nothing to pay, adding record zero payed')
        connector.add_transaction(id_block, 'null', 'sent', 0)
        return
    amounts = pay_stat.set_index('user')['shares'].to_dict()
    print(amounts)
    amounts_string = json.dumps(amounts)
    params = ["", amounts, 6, 'mining_payout', list(amounts.keys()), True, 6, 'ECONOMICAL']
    print("paying for block")
    print(params)
    try:
        answ = request_rpc('sendmany', params)
        txn_hash = answ
        if txn_hash is None:
            print('result is None')
            print(answ)
        print("Transaction hash: ", txn_hash)
        connector.add_transaction(id_block, txn_hash, 'sent', sum(pay_stat['shares']))
    except Exception as e:
        print(e)



print("starting threads...")
print("parser thread...")
parser_thread.start()
print("payment thread...")
payment_thread.start()
# print("testing")
# print(request_rpc('getblockchaininfo', [], verbosity=2))