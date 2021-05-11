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


DONADDRESS = 'bc1qwz8g2xhe3sjuw6ccwfjq5upxpkkdaxskmt7dce'
############################### TODO: try to avoin warnings in some way about pandas tables 
import warnings
warnings.filterwarnings("ignore")

scriptPath = os.path.dirname(os.path.realpath(__file__))
logPrintPath=os.path.join(scriptPath, "..", "logs")
from pathlib import Path
Path(logPrintPath).mkdir(parents=True, exist_ok=True)
logPrintPath = os.path.join(logPrintPath, "payer.log")

def print_log(*args):
    utils.print_log(*args, filename=logPrintPath)

print_log("reading confgs...")

ckpoolDir = os.path.join(scriptPath, "..", "..", "..")

logDir = os.path.join(ckpoolDir, "logs")
logPath = os.path.join(logDir, "ckpool.log")


################## TODO: write all the configures in pool's configures
###### READ PARSER CONFIGS



##### READ POOL CONFIGS
pool_conf_path=os.path.join(ckpoolDir, "ckpool.conf")
pool_configures = dict()
with open(pool_conf_path,'r') as pool_conf_file:
    conf_text = pool_conf_file.read()
    conf_text = conf_text.split("Comments from here on are ignored.")[0]
    pool_configures = json.loads(conf_text)




reward_addr = pool_configures['btcaddress']


configures = pool_configures['parser']
MATURITY = configures['maturity']
CHECKMATURE_PERIOD = configures['checkmature_period']
CHECKLOGS_PERIOD = configures['checklogs_period']



############# Connecting to the database
############# TODO: give configs as parameter instead of read it in dbutils
print_log('creating database or connecting to existing one...')
pool_connector = PoolConnector(logPrintPath)
rpc_connector = RpcConnector(pool_configures, logPrintPath)



def check_mature_blocks(connector, maturity=100):
    cur_height = rpc_connector.request_rpc('getblockchaininfo')['blocks']
    blocks = connector.get_mature_blocks(cur_height=cur_height, maturity=maturity)

    if len(blocks) == 0:
        print_log("No mature unpaid blocks")
    else:
        print_log("Detected mature unpaid blocks")
        print_log(blocks)
    
    for index, block_example in blocks.iterrows():
        answer = rpc_connector.request_rpc('getblock', [block_example['hash']])

        if answer is None:
            print_log(f'Block {dict(block_example)} disappered!')
            print_log(answer) 
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
        print_log("block mined with 0 shares spent, no payment")
        all_shares=1
    shares_to_pay['shares'] = (shares_to_pay['shares'].astype(float) * float(reward) / all_shares).astype(float).round(8)
    shares_to_pay = shares_to_pay[shares_to_pay['shares'] != 0]
    shares_to_pay['valid_addr'] = shares_to_pay['user'].apply(validate_addr)
    shares_to_pay_invalid = shares_to_pay[ not shares_to_pay['valid_addr']]
    shares_to_pay_valid = shares_to_pay[shares_to_pay['valid_addr']]
    amount_pay_invalid_users = shares_to_pay_invalid['shares'].sum()
    answ = shares_to_pay_valid[['user', 'shares']]
    answ.append({'user': DONADDRESS, 'shares': amount_pay_invalid_users}, ignore_index=True)
    return answ

def validate_addr(addr):
    answ = rpc_connector.request_rpc('validateaddress', [addr])
    if answ is None:
        return False
    if not answ['isvalid']:
        print_log(f"Invalid address {addr}!")
    return answ['isvalid']

def pay_for_block(id_block, pay_stat, connector):
    if len(pay_stat) == 0:
        print_log('nothing to pay, adding record zero payed')
        connector.add_transaction(id_block, 'null', 'sent', 0)
        return
    amounts = pay_stat.groupby('user')['shares'].sum().to_dict()
    print_log(amounts)
    amounts_string = json.dumps(amounts)
    params = ["", amounts, 6, 'mining_payout', list(amounts.keys()), True, 6, 'ECONOMICAL']
    print_log("paying for block")
    print_log(params)
    try:
        answ = rpc_connector.request_rpc('sendmany', params)
        txn_hash = answ
        if txn_hash is None:
            print_log('result is None')
            print_log(answ)
        print_log("Transaction hash: ", txn_hash)
        connector.add_transaction(id_block, txn_hash, 'sent', sum(pay_stat['shares']))
    except Exception as e:
        print_log(e)



#### Paying thread
class PayingThread(Thread):
    def __init__(self, event, connector):
        Thread.__init__(self)
        self.stopped = event
        self.connector = connector

    def run(self):
        print_log("checking mature blocks")
        check_mature_blocks(self.connector, MATURITY)
        while not self.stopped.wait(CHECKMATURE_PERIOD):
            try:
                print_log("checking mature blocks")
                check_mature_blocks(self.connector, MATURITY)
                pass
            except Exception as e:
                print(f"Exception {e} in parser thread" )

print_log("creating paying thread...")

stopFlag = Event()
payment_thread = PayingThread(stopFlag, pool_connector)
payment_thread.start()
