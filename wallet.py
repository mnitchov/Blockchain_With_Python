# Import dependencies
import subprocess
import json
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import geth_poa_middleware


# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("mnemonic")

# Import constants.py and necessary functions from bit and web3
from constants import *
 
 
# Create a function called `derive_wallets`
def derive_wallets(coin, mnemonic=mnemonic, depth=3):
    command = f'./derive -g --mnemonic='{mnemonic}' --coin={coin} --numderive=3 --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {ETH: derive_wallets(coin=ETH),
    BTCTEST: derive_wallets(coin=BTCTEST)}

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)

# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, to, amount):
    if coin == ETH:
        value = w3.toWei(amount, "ether") 
        gasEstimate = w3.eth.estimateGas({ "to": to, "from": account.address, "amount": value })
        return {
            "to": to,
            "from": account.address,
            "value": value,
            "gas": gasEstimate,
            "gasPrice": w3.eth.generateGasPrice(),
            "nonce": w3.eth.getTransactionCount(account.address),
            "chainId": w3.net.chainId
        }
    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, to, amount):
    if coin == ETH:
        raw_tx = create_tx(coin, account, to, amount)
        signed = account.signTransaction(raw_tx)
        return w3.eth.sendRawTransaction(signed.rawTransaction)
    if coin == BTCTEST:
        raw_tx = create_tx(coin, account, to, amount)
        signed = account.sign_transaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed)

