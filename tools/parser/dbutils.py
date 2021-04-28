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

