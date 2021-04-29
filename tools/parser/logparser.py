import os

from parse import *
import json
from utils import get_reward
from dbutils import PoolConnector
import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings("ignore")

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
scriptPath = os.path.dirname(os.path.realpath(__file__))
ckpoolDir = os.path.join(scriptPath, "..", "..")

logDir = os.path.join(ckpoolDir, "logs")
logPath = os.path.join(logDir, "ckpool.log")

conf_path=os.path.join(scriptPath, "parser.conf")

configures = dict()
with open(conf_path,'r') as conf_file:
    conf_text = conf_file.read()
    conf_text = conf_text.split("Comments from here on are ignored.")[0]
    configures = json.loads(conf_text)

MATURITY = configures['maturity']

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
rpc_connection = AuthServiceProxy(f"http://{rpc_auth}:{rpc_pass}@{rpc_url}")

pool_con = PoolConnector()

if os.path.isfile(logPath):
    print(f"path {logPath} is a file, everyhting ok")
else:
    print(f"path {logPath} is not a file!")
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
    block_id = pool_con.get_block_id_by_hash(block_hash)
    pool_con.set_stats(block_id, share_stats)

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
            share_stats.update({user: shares})
    return share_stats
        


from threading import Thread, Event

class ParserThread(Thread):
    def __init__(self, event, curs):
        Thread.__init__(self)
        self.stopped = event
        self.curs = curs

    def run(self):
        while not self.stopped.wait(0.5):
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

with open(logPath,'r') as infile:
    lines = infile.readlines()
    curs = infile.tell()
parser_thread = ParserThread(stopFlag, curs)





class PayingThread(Thread):
    def __init__(self, event, connector):
        Thread.__init__(self)
        self.stopped = event
        self.connector = connector

    def run(self):
        while not self.stopped.wait(2):
            print("checking mature blocks")
            check_mature_blocks(self.connector, rpc_connection, MATURITY)
            pass
            

stopFlag = Event()


payment_thread = PayingThread(stopFlag, pool_con)

def check_mature_blocks(connector, rpc_connection, maturity=100):
    print("checking mature blocks")
    cur_height = rpc_connection.getblockchaininfo()['blocks']
    blocks = connector.get_mature_blocks(cur_height=cur_height, maturity=maturity)
    print(blocks)
    for index, block_example in blocks.iterrows():
        answer = request_rpc('getblock', [block_example['hash']])

        if answer['result'] is None:
            print(f'Block {dict(block_example)} disappered!')
            connector.add_transaction(block_example['id'], 'null', 'disappeared', 'null')
            continue
        pay_stat = get_pay_info(block_example, connector, rpc_connection)
        pay_for_block(block_example['id'],  pay_stat, connector, rpc_connection)
        

def get_pay_info(block_example, connector, rpc_connection):
    reward = block_example['reward']
    prev_block = connector.get_prev_block(block_example['id'])
    cur_shares = connector.get_shares(block_example['id'])
    if prev_block is None:
        shares_to_pay = cur_shares
    else:
        prev_shares = connector.get_shares(prev_block['id'])
        shares_diff = cur_shares.merge(prev_shares, how="left", on="user", suffixes=['_cur', '_prev'])
        shares_diff['shares'] = shares_diff['shares_cur'] - shares_diff['shares_prev']
        shares_to_pay = shares_diff[['user', 'shares']]
    all_shares = shares_to_pay['shares'].sum()
    if all_shares == 0:
        print("block mined with 0 shares spent, no payment")
        all_shares=1
    shares_to_pay['shares'] = (shares_to_pay['shares']* reward / all_shares).astype(float).round(8)
    shares_to_pay = shares_to_pay[shares_to_pay['shares'] != 0]
    print(shares_to_pay)
    return shares_to_pay[['user', 'shares']]

def pay_for_block(id_block, pay_stat, connector, rpc_connection):
    if len(pay_stat) == 0:
        print('nothing to pay, adding record zero payed')
        connector.add_transaction(id_block, 'null', 'sent', 0)
        return
    amounts = pay_stat.set_index('user')['shares'].to_dict()
    print(amounts)
    amounts_string = json.dumps(amounts)
    params = ["", amounts, 6, 'mining_payout', list(amounts.keys()), True, 6, 'ECONOMICAL']
    print(params)
    try:
        txn_hash = request_rpc('sendmany', params)['result']
        print(txn_hash)
        connector.add_transaction(id_block, txn_hash, 'sent', sum(pay_stat['shares']))
    except Exception as e:
        print(e)

import requests
def request_rpc(method, params):
    url = "http://127.0.0.1:19998/"
    payload = json.dumps({"method": method, "params": params})
    headers = {'content-type': "application/json", 'cache-control': "no-cache"}
    try:
        response = requests.request("POST", url, data=payload, headers=headers, auth=(rpc_auth, rpc_pass))
        return json.loads(response.text)
    except requests.exceptions.RequestException as e:
        print(e)
    except:
        print('No response from rpc, check Bitcoin is running on this machine')


payment_thread.start()
parser_thread.start()