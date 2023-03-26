from time import sleep, time
from config import *
from decimal import Decimal
from zksync_sdk import ZkSync, HttpJsonRPCTransport, ZkSyncProviderV01, network, ZkSyncSigner, ZkSyncLibrary, EthereumSignerWeb3, EthereumProvider, Wallet
from zksync_sdk.types import ChangePubKeyEcdsa
from datetime import datetime
from datetime import date
from web3 import Web3, HTTPProvider, Account
import asyncio, json, random, base58, binascii, requests

# Zksync-farm-lite script by @Pearlsome https://t.me/legalcrypt

async def getContractsAddress(provider):
    contracts = await provider.get_contract_address()
    return contracts
    
async def getVerifiedETHBalance(wallet):
    ethBalance = await wallet.get_balance("ETH", "verified")
    return ethBalance
    
def connectWallet(account, w3):
    # This ZkSyncLibrary is predefined for Linux system. Use https://github.com/zksync-sdk/zksync-crypto-c/releases to download library for your system
    library = ZkSyncLibrary(library_path="crypto/zks-crypto-x86_64-unknown-linux-gnu.so")
    provider = ZkSyncProviderV01(provider=HttpJsonRPCTransport(network=network.mainnet))
    
    # get all contracts in Zksync network
    loop = asyncio.new_event_loop()
    task = loop.create_task(getContractsAddress(provider))
    loop.run_until_complete(task)
    contracts = task.result()
    
    # create wallet object
    zksync = ZkSync(account=account, web3=w3, zksync_contract_address=contracts.main_contract)
    ethereum_provider = EthereumProvider(w3, zksync)
    ethereum_signer = EthereumSignerWeb3(account=account)
    signer = ZkSyncSigner.from_account(account, library, network.mainnet.chain_id)
    wallet = Wallet(ethereum_provider=ethereum_provider, zk_signer=signer, eth_signer=ethereum_signer, provider=provider)
    return wallet
    
def checkBalance(wallet, account):
    loop = asyncio.new_event_loop()
    task = loop.create_task(getVerifiedETHBalance(wallet))
    loop.run_until_complete(task)
    ethBalance = task.result()
    return ethBalance
    
async def createAccInZksync(wallet):
    if not await wallet.is_signing_key_set():
        tx = await wallet.set_signing_key("ETH", eth_auth_data=ChangePubKeyEcdsa())
        status = await tx.await_committed()
    
def getLastTransactionDate(address):
    #get last tx date from API
    lastTX = requests.get(f'https://api.zksync.io/api/v0.1/account/{address}/history/0/1')
    txDate = lastTX.json()[0]['created_at']
    
    #calculate time delta from now
    date_format = "%Y-%m-%dT%H:%M:%S.%f%z" 
    dateTX = datetime.strptime(txDate[ 0 : txDate.index(".")], "%Y-%m-%dT%H:%M:%S")
    dateNOW = datetime.today()
    delta = dateNOW - dateTX
    return delta
    
def sendTransaction(wallet, to_address):
    amount = Decimal('%.6f'%(random.uniform(float(sendETH)-0.000003, float(sendETH)+0.000003)))
    print(f"--------------- I gonna send {amount} ETH to ---> {to_address}")
    async def txSendAsync(wallet, to_address, amount):
        tx = await wallet.transfer(to_address, amount=amount, token="ETH")
        status = await tx.await_committed()
        return status
    loop = asyncio.new_event_loop()
    task = loop.create_task(txSendAsync(wallet, to_address, amount))
    loop.run_until_complete(task)
    txStatus = task.result().status
    return txStatus
    
def chooseAction():
    # claimNFT is more expensive so we want to do it more rare
    actions = ['sendTx', 'claimNFT', 'sendTx', 'sendTx']
    random.shuffle(actions)
    action = random.choice(actions)
    return action
    
def generateTX(wallet, account, to_address, action):
    if action == 'sendTx':
        try:
            txStatus = sendTransaction(wallet, to_address)
            print(f"Sent some ETH: {txStatus}")
            return txStatus
        except:
            return False
    elif action == 'claimNFT':
        try:
            txStatus = claimNFT(wallet, account)
            print(f"Claimed NFT: {txStatus}")
            return txStatus
        except:
            return "Failed to send TX"
    else:
        txStatus = 'Unexpected error'
    return txStatus
    
def claimNFT(wallet, account):
    # use NFT images of top ETH collections from here https://etherscan.io/nft-top-contracts that provide ipfs CID as expected
    nftContractsTop15 = ['0x60e4d786628fea6478f785a6d7e704777c86a7c6', '0xed5af388653567af2f388e6224dc7c4b3241c544', '0xd774557b647330c91bf44cfeab205095f7e6c367', '0x0bb12d00709ae3b02b90091e0475b8b0ddb7621d', '0x97d135231ffbc6a89779c456ca4cb803a7ea248e']
    random.shuffle(nftContractsTop15)
    contractAddress = random.choice(nftContractsTop15)
    url = f"{RPC_URL}/getNFTsForCollection?contractAddress={contractAddress}&withMetadata=true"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    nfts = response.json()["nfts"]
    medias = [item.get('metadata') for item in nfts]
    images = [item.get('image') for item in medias]
    random.shuffle(images)
    randomImage = random.choice(images).split('ipfs://')[1].split('/')[0]
    
    def ipfscidv0_to_byte32(cid):
        # Convert ipfscidv0 to 32 bytes hex string.
        decoded = base58.b58decode(cid)
        sliced_decoded = decoded[2:]
        return binascii.b2a_hex(sliced_decoded).decode("utf-8")
    
    randomImage0x = f"0x{ipfscidv0_to_byte32(randomImage)}"
    async def sendNftTX(wallet, account, randomImage0x):
        tx = await wallet.mint_nft(randomImage0x, account.address, "ETH")
        status = await tx.await_committed()
        account_state = await wallet.get_account_state()
        return status
    loop = asyncio.new_event_loop()
    task = loop.create_task(sendNftTX(wallet, account, randomImage0x))
    loop.run_until_complete(task)
    txStatus = task.result()
    return txStatus
    
if __name__ == "__main__":
    _RPC_URL = RPC_URL
    w3 = Web3(Web3.HTTPProvider(_RPC_URL))
    print("")
    with open('data.txt', 'r') as f:
        data = f.read().splitlines()

    balances_file = open('balances.txt', 'w')
    for row in data:
        private_key = row.split(';')[0]
        to_address = row.split(';')[1]
        account = Account.from_key(private_key)
        
        # generate wallet object in Zksync
        wallet = connectWallet(account, w3)
        
        # check ethereum balance in Zksync
        etherBalance = Decimal(w3.fromWei(checkBalance(wallet, account),'ether'))
        if etherBalance > Decimal(0.0001):
            print(f"==> \033[92m{account.address}\033[0m balance is: {etherBalance} ETH")
            # check if Zksync is activated by one-time payment
            loop = asyncio.new_event_loop()
            task = loop.create_task(createAccInZksync(wallet))
            loop.run_until_complete(task)
            
            # get to know how long ago was executed last transaction
            dateDeltaFromLastTx = getLastTransactionDate(account.address)
            if (Decimal(dateDeltaFromLastTx.total_seconds()) / 86400) > Decimal(DAYS):
                print(f"--------------- Last tx was: {dateDeltaFromLastTx} ago")
                action = chooseAction()
                print(f"--------------- I gonna {action} this time")
                txStatus = generateTX(wallet, account, to_address, action)
            else:
                print(f"--------------- Last TX was: {dateDeltaFromLastTx}")
                print(f"--------------- Need to wait more time!")
            print("")
        else:
            print(f"==> \033[92m{account.address}\033[0m balance is: {etherBalance} ETH. \033[93mYou need to add more!\033[0m")
            print("")
        
        # write current balances in file
        etherBalance = Decimal('%.6f'%(w3.fromWei(checkBalance(wallet, account),'ether')))
        balances_file.write(f'{etherBalance}\t{account.address}\n')
    balances_file.close()