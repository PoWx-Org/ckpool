
import os

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


import json
import pymysql
sql_conf_file_name="parser.conf"

with open(sql_conf_file_name, "r") as sql_conf_file:
    sql_conf_str = sql_conf_file.read()
    sql_conf = json.loads(sql_conf_str)['sql']

username = sql_conf['auth']
password = sql_conf['pass']
hostname = sql_conf['host']


def read_users:

        
def execute_query(query):
    myConnection = pymysql.connect( host=hostname, user=username, passwd=password)
    print(query)
    cur = myConnection.cursor()
    execute_complex_query(cur, query)
    myConnection.commit()
    myConnection.close()

def execute_complex_query(cur, general_query):
    queries = [query.strip() for query in general_query.split(';') if len(query) > 0]
    for subquery in queries:
        cur.execute(subquery)

def install_db():
    install_query_path = os.path.join('scripts', 'install.sql')
    with open(install_query_path, 'r') as query_file:
        install_query = query_file.read()
    execute_query(install_query)

def add_mined_block(hash, date, height, reward):
    query = f'''USE `pool_base`; INSERT INTO `mined_blocks` 
            (`hash`, `date_mined`, `height`, `reward`) 
            VALUES ('{hash}', '{date}', {height}, {reward});'''
    execute_query(query)

def insert_stats

install_db()
add_mined_block('qwer', '2015-11-05 14:29:36', 21, 0.12345)
execute_query('SELECT * FROM pool_base.mined_blocks;')

