import requests
import json

url = 'https://arbitrum-mainnet.infura.io/v3/361fb02d372b4a59b98a7c8d36c05bc4'

payload = {
    "jsonrpc": "2.0",
    "method": "eth_blockNumber",
    "params": [],
    "id": 1
}

headers = {'content-type': 'application/json'}

response = requests.post(url, data=json.dumps(payload), headers=headers).json()

print(response)