from web3 import Web3
import sys
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Access environment variables using os.getenv()
infura_key = os.getenv("infura_key")
infura_mainnet_url = os.getenv("infura_mainnet_url")

# Set your HTTPS provider URL here or via environment variable
ETH_PROVIDER = infura_mainnet_url

# Aave V3 Pool contract address (Ethereum mainnet)
AAVE_V3_POOL_ADDRESS = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"

# ABI fragment for the LiquidationCall event
LIQUIDATION_CALL_EVENT_ABI = {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "internalType": "address", "name": "collateralAsset", "type": "address"},
        {"indexed": True, "internalType": "address", "name": "debtAsset", "type": "address"},
        {"indexed": True, "internalType": "address", "name": "user", "type": "address"},
        {"indexed": False, "internalType": "uint256", "name": "debtToCover", "type": "uint256"},
        {"indexed": False, "internalType": "uint256", "name": "liquidatedCollateralAmount", "type": "uint256"},
        {"indexed": False, "internalType": "address", "name": "liquidator", "type": "address"},
        {"indexed": False, "internalType": "bool", "name": "receiveAToken", "type": "bool"},
    ],
    "name": "LiquidationCall",
    "type": "event"
}

def get_web3():
    if ETH_PROVIDER == "YOUR_HTTPS_PROVIDER_URL":
        raise Exception("Please set your Ethereum HTTPS provider URL in ETH_PROVIDER env variable or in the script.")
    return Web3(Web3.HTTPProvider(ETH_PROVIDER))

def get_last_eth_block():
    w3 = get_web3()
    if not w3.is_connected():
        raise Exception("Failed to connect to Ethereum mainnnet")
    else:
        print("Connected to Ethereum mainnet")
    return w3.eth.block_number

def get_liquidation_events(w3, from_block, to_block):
    contract = w3.eth.contract(address=AAVE_V3_POOL_ADDRESS, abi=[LIQUIDATION_CALL_EVENT_ABI])
    event = contract.events.LiquidationCall

    logs = event.get_logs(from_block=from_block, to_block=to_block)
    results = []
    for log in logs:
        results.append({
            "blockNumber": log.blockNumber,
            "transactionHash": log.transactionHash.hex(),
            "collateralAsset": log.args.collateralAsset,
            "debtAsset": log.args.debtAsset,
            "user": log.args.user,
            "debtToCover": log.args.debtToCover,
            "liquidatedCollateralAmount": log.args.liquidatedCollateralAmount,
            "liquidator": log.args.liquidator,
            "receiveAToken": log.args.receiveAToken,
        })
    return results

def main():
    N = 100 # default number of blocks starting from last. 
    last_block = get_last_eth_block()
    print(f"last Ethereum block: {last_block}")
    if len(sys.argv) != 2:
        to_block = last_block
        from_block = last_block - 100 # Use last 100 block when no argument is provided
        print(f"Using last 100 blocks in Ethereum mainnet. If you want to specify a number of blocks, follow usage below.")
    else:
        print(f"Usage: python {sys.argv[0]} <N_BLOCKS>")
        N = int(sys.argv[1])
        from_block = max(0, last_block - N + 1)
        to_block = last_block

    print(f"Fetching LiquidationCall events from block {from_block} to {to_block}...")

    w3 = get_web3()
    events = get_liquidation_events(w3, from_block, to_block)
    print(f"Found {len(events)} LiquidationCall events in the last {N} blocks.")
    for e in events:
        print(e)

if __name__ == "__main__":
    main()