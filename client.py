import os
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv
import time

import deploy

# Load environment variables
load_dotenv()

# Set up web3 connection
provider_url = os.getenv("CELO_PROVIDER_URL")
w3 = Web3(HTTPProvider(provider_url))
assert w3.is_connected(), "Not connected to a Celo node"

# Add PoA middleware to web3.py instance
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Get contract ABI and address
abi = deploy.abi
contract_address = deploy.contract_address
contract = w3.eth.contract(address=contract_address, abi=abi)

# Initialize account
account_address = os.getenv("CELO_DEPLOYER_ADDRESS")
private_key = os.getenv("CELO_DEPLOYER_PRIVATE_KEY")


# Function to subscribe to the service
def subscribe(subscriber_address, private_key, subscription_price):
    
    # Fetch the current gas price from the network
    current_gas_price = w3.eth.gas_price
    
    # Prepare the transaction
    transaction = contract.functions.subscribe().build_transaction({
        'chainId': 44787,
        'gas': 2000000,
        'gasPrice': current_gas_price,
        'nonce': w3.eth.get_transaction_count(subscriber_address),
        'value': subscription_price,
    })

    # Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

    # Send the transaction
    return w3.eth.send_raw_transaction(signed_txn.rawTransaction)



# Function to withdraw funds (only callable by owner)
def withdraw_funds(owner_address, private_key, amount):
    # Fetch the current gas price from the network
    current_gas_price = w3.eth.gas_price
    
    # Prepare the transaction
    transaction = contract.functions.withdrawFunds(amount).build_transaction({
        'chainId': 44787,
        'gas': 2000000,
        'gasPrice': current_gas_price,
        'nonce': w3.eth.get_transaction_count(owner_address),
    })
    
    # Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

    # Send the transaction
    return w3.eth.send_raw_transaction(signed_txn.rawTransaction)


# Example Usage:
subscriber_address = "0xcdd1151b2bC256103FA2565475e686346CeFd813" # SUBSCRIBER_ADDRESS
private_key = os.getenv("SUBSCRIBER_PRIVATE_KEY")
subscription_price = w3.to_wei('0.0001', 'ether')  # In wei

# Subscribing
transaction_hash = subscribe(subscriber_address, private_key, subscription_price)
transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
print("Subscription successful, Transaction hash: ", transaction_hash.hex())


# Withdrawing funds as the contract owner (example)
owner_address =  account_address # "OWNER_ADDRESS"
owner_private_key = private_key # "OWNER_PRIVATE_KEY"
withdraw_amount = w3.to_wei('0.00001', 'ether')

transaction_hash = withdraw_funds(owner_address, owner_private_key, withdraw_amount)
transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
print("Withdrawal successful, Transaction hash: ", transaction_hash.hex())


