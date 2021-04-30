########### Good request, reurns message if answer has no results
import requests
import json

class RpcConnector:
    def __init__(self, config):
        self.config = config
    
    def request_rpc(self, method, params=[], verbosity=1):
        config = self.config

        rpc_url = config['btcd'][0]['url']
        rpc_auth = config['btcd'][0]['auth']
        rpc_pass = config['btcd'][0]['pass']

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