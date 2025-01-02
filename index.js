const axios = require('axios');

axios.post('https://arbitrum-mainnet.infura.io/v3/361fb02d372b4a59b98a7c8d36c05bc4', {
  jsonrpc: '2.0',
  method: 'eth_blockNumber',
  params: [],
  id: 1
})
.then(response => {
  console.log(response.data);
})
.catch(error => {
  console.error(error);
});