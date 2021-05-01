# oBTC-pool with Payout system

oBTC Pool is a pool for Optical Bitcoin (oBTC).  oBTC is an experimental
currency based on Bitcoin. Using low-energy miners will enable mining all
over the globe. See more on https://powx.org.

oBTC Pool is based on CKPOOL by Con Kolivas.

Ultra low overhead massively scalable multi-process, multi-threaded modular
oBTC mining pool, proxy, passthrough, and library in c for Linux.

CKPOOL is code provided free of charge under the GPLv3 license.



This repository is based on https://github.com/rsksmart/ckpool which is based on [CKPool original](https://bitbucket.org/ckolivas/ckpool)
Install the ckpool following these instructions:
[Install on ](README_original.md)

## What is the payout system

The problem was that Pool does not have any payouts at all

It has current users statistics(haw many shares each use submitted) and displays in log files when block is mined. So the solution is:
- (Accounting) Create System that monitors logs and when block is mined writes o the database:
Current users statistics per each user (and mention what is the block)
Block, reward for the block (no donation included)
- (Payments) Create other system that monitors databases and blockchain’s height and when it detects mature blocks, makes payouts due to written statistics about this block. Statistics compared with the previous !payed! block’s statistics and making conclusion which amount of work was done. Before paying system checks if block with such hash is in blockchain. If some block has rejected from chain after acceptance, it writes that this block is disappeared and later on will use statistics of the previous block.

	The processes are separate because if something is broken in payments, it souldn’t stop accounting as accounting is the most crucial part as far as we know how much should we pay to each miner even when automation of payment if down.  



## How to install payout system


```
sudo apt-get install python3-pip
```

go to the cloned repository 

```
pip3 install -r requirments.txt
```

edit `ckpool.conf`. Set essential cofigures here:
(write root's password for maysql db)

```
"parser":{
		"sql":
		{
			"auth": "root",
			"pass": "<root-password>",
			"host": "localhost"
		},
```
go to the `tools/parse`

run
```
./accounting.sh
```


Note that you can run acountig system only if ckpool and bitcoin node are active.
If you are running it on the net which has an empty mempool, you need to run your bitcoin node with the following paramener:
```
bitcoind --fallbackfee=0.000001
```

Here is also some code from 
