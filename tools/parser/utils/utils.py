
import os

PRINT_LOG_TO_CONSOLE=True

def get_reward(block_info, reward_addr):
    def is_coinbase(txn):
        try:
            return 'coinbase' in txn['vin'][0].keys()
        except:
            return False
    coinbase_txn = next(obj for obj in block_info['tx'] if is_coinbase(obj))


    def is_reward(vout1, reward_addr):
        try:
            vout = vout1['scriptPubKey']
            if len(vout['addresses']) != 1:
                return False
            if reward_addr != vout['addresses'][0]:
                return False
            return True
        except:
            return False
    try:
        reward = next(obj['value'] for obj in coinbase_txn['vout'] if is_reward(obj, reward_addr))
    except:
        raise Exception("Seems like wrong address mentioned")
    return reward

import sys
import datetime

def print_log(*args, filename):
    original_stdout = sys.stdout # Save a reference to the original standard output
    with open(filename, 'a') as f:
        sys.stdout = f 
        print(f'[{datetime.datetime.utcnow()}]', *args)
        sys.stdout = original_stdout
    if PRINT_LOG_TO_CONSOLE:
        print(f'[{datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}]', *args)


