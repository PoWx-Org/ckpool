import json
import pymysql
import os
# def insert_stats

# install_db()
# add_mined_block('qwer', '2015-11-05 14:29:36', 21, 0.12345)
# execute_query('SELECT * FROM pool_base.mined_blocks;')

class PoolConnector:
    def __init__(self,):
        scriptPath = os.path.dirname(os.path.realpath(__file__))
        sql_conf_file_name=os.path.join(scriptPath, "parser.conf")
        with open(sql_conf_file_name, "r") as sql_conf_file:
            sql_conf_str = sql_conf_file.read()
            sql_conf = json.loads(sql_conf_str)['sql']
        self.username = sql_conf['auth']
        self.password = sql_conf['pass']
        self.hostname = sql_conf['host']
        self.install_db()

    def install_db(self):
        install_query_path = os.path.join('scripts', 'install.sql')
        with open(install_query_path, 'r') as query_file:
            install_query = query_file.read()
        self.execute_query(install_query)

    def execute_complex_query(self, cur, general_query):
        queries = [query.strip() for query in general_query.split(';') if len(query) > 0]
        for subquery in queries:
            cur.execute(subquery)

    def execute_query(self, query):
        conn = pymysql.connect( host=self.hostname, user=self.username, passwd=self.password)
        print(query)
        cur = conn.cursor()
        self.execute_complex_query(cur, query)
        conn.commit()
        conn.close()

    def add_mined_block(self, hash, date, height, reward):
        query = f'''USE `pool_base`; INSERT INTO `mined_blocks` 
                (`hash`, `date_mined`, `height`, `reward`) 
                VALUES ('{hash}', '{date}', {height}, {reward});'''
        self.execute_query(query)

    def get_query_results(self, query):
        conn = pymysql.connect( host=self.hostname, user=self.username, passwd=self.password)
        print(query)
        cur = conn.cursor()
        self.execute_complex_query(cur, query)
        res = list(cur.fetchall())
        conn.close()
        return res

    def get_block_id_by_hash(self, hash):
        query = f'''SELECT id_block FROM pool_base.mined_blocks
                    WHERE hash='{hash}';'''
        return self.get_query_results(query)[0][0]

    def get_user_id_by_name(self, name):
        query = f'''SELECT id_miner FROM pool_base.miners
                    WHERE name='{name}';'''
        return self.get_query_results(query)[0][0]

    def insert_single_stat(self, id_block, id_miner, shares):
        query = f'''USE `pool_base`; INSERT INTO `blocks_sats` 
                (`id_block`, `id_miner`, `shares`) 
                VALUES ({id_block}, {id_miner}, {shares});'''
        self.execute_query(query)


    def set_stats(self, block_id, users_stats):
        self.update_users(users_stats)
        for user, shares in users_stats.items():
            u_id = self.get_user_id_by_name(user)
            insert_single_stat(id_block, u_id, shares)


    def add_user(self, user):
        query = f'''USE `pool_base`; INSERT INTO `miners` 
                (`name`) 
                VALUES ('{user}');'''
        self.execute_query(query)

    def update_users(self, users_stats):
        cur_users = list(users_stats.keys())
        users_db = [i[0] for i in self.get_query_results("SELECT name FROM pool_base.miners")]
        new_users = [i for i in cur_users if i not in users_db]
        for user in new_users:
            self.add_user(user)
        
