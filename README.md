# zksync-lite-farmer
Python script to send ETH transactions and mint NFTs in Zksync Lite network every X days. Keeps your accounts active on a regular basis.

Created by Riko https://t.me/legalcrypt

### Features

- There are 2 types of randomly selected transactions: sending ETH or minting NFT;
- Images for minting NFTs are randomly selected from popular ETH collections;
- Can be used as balance checker, you can find all ETH balances in balances.txt
- Gas fee check is not implemented, so tx costs can be unexpected in some unexpected network conditions;
- NFT mints can sometimes fail due to bugs in image parsing function :)

### Requirements
-------------
**1.** You need **Alchemy** account for ETH RPC link.

	Register here https://dashboard.alchemy.com/
	Create new ETH mainnet app
	Get https rpc link
	
**2.** You need to manually add ETH balance to your Zksync lite accounts. 

	Go to https://lite.zksync.io/account/top-up
	Add more than 0.00011 ETH per account
**3.** You need Python 3

### Installation
-------------

`git clone https://github.com/Kizliak/zksync-lite-farmer`

`apt install python3-pip, git`

`pip install git+https://github.com/zksync-sdk/zksync-python.git`

`pip install -r requirements.txt`

Edit config.py with your values

`nano config.py`

Add pairs private_key;spare wallets to data.txt

`nano data.txt`

Finally run the script

`python3 main.py`

When it finishes you will probably want like to check the remaining balances of all your accs:

`cat balances.txt`

Run the script manually every 5-7 days or use cron to schedule autorun.
