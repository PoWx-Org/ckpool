########### Good request, reurns message if answer has no results
import requests
import json
from utils import print_log

class RpcConnector:
    def __init__(self, config, log_file):
        self.config = config
        self.log_file = log_file
    
    def print_log(*args):
        print_log(*args, filename=self.log_file)
    
    def request_rpc(self, method, params=[], verbosity=1):
        config = self.config

        rpc_url = config['btcd'][0]['url']
        rpc_auth = config['btcd'][0]['auth']
        rpc_pass = config['btcd'][0]['pass']

        url = f"http://{rpc_url}/"
        payload = json.dumps({"method": method, "params": params})
        headers = {'content-type': "application/json", 'cache-control': "no-cache"}
        if verbosity >=2:
            self.print_log("trying to request")
            self.print_log("url", rpc_url)
            self.print_log('auth', (rpc_auth, rpc_pass)) 
            self.print_log('payload', payload)
            self.print_log('headers', headers)
        try:
            response = requests.request("POST", url, data=payload, headers=headers, auth=(rpc_auth, rpc_pass))
            if json.loads(response.text)['result'] is None:
                self.print_log(f'Got response result None for method {method}:\n{response}')
            return json.loads(response.text)['result']
        except requests.exceptions.RequestException as e:
            self.print_log(e)
        except Exception as e:
            self.print_log('No response from rpc, check optical Bitcoin is running on this machine')
            self.print_log(e)