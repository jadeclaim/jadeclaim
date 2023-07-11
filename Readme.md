# Jade Redemption Repository

## Presentation

The goal of the repository is to distribute the jade treasury to its recipients. This is done in two parts:

1. Fetching all the data on chain at a certain height
2. Deploying relevant contracts to have users claim their USDC on arbitrum

## Setup

_Requires python3.9+, jupyter notebook, make, gcc_

The Python requirements are detailed under the [requirement file](./requirements.txt)
Create a new virtual environment (https://docs.python.org/3/library/venv.html)
From a new env install those requirements by running the below. You might get an error with dateutils version, just ignore.
```
pip install --upgrade pip
pip install -r ./requirements.txt
```

Crease a ".env" file from the ".env_example" file.
In the .env file, fill the following environment variables:
-SNOWTRACE_TOKEN
-BSCSCAN_TOKEN
-ARBISCAN_TOKEN
with their respective API keys from each chain explorer. You can get free API Keys by registering with those chain explorers. (Arbiscan is not needed for goal #1)

### Warning

Setting up the workspace for compilation takes space and time, and is unrelated to the data. If you are curious and would like more information, install OpenZeppelin 4.4.2 by using
```
brownie pm install OpenZeppelin/openzeppelin-contracts@4.4.2
```

The `contracts` folder is provided for transparency and is not required for goal #1. It is recommended to delete this if you are only interested in goal #1.


The bsc default rpc behaves strangely sometimes. It is recommended to add a private archiving rpc and you can get one from www.quicknode.com.
Afterwards, you can update the brownie config by running:
```
brownie networks modify bsc-main host=<NEW URL>
```

## Getting the data:

From the root, getting the data is done with:

```
make get_avax_data
make get_bsc_data
```
(note, running both of these will take 2 or more hours...)

After completion, the data  will be in the `/data` folder.

Next we need to clean/parse all the irrelavant contracts. Do this by install tqdm and pandas
```
pip install tqdm
pip install pandas
```
Then run ths scripts to do the parsing by running (IN ORDER!!):

```
python AVAX.py
python BSC.py
python convert_for_website.py
```

## Computation methods:

The accounts holding relevant data are separated in the following categories :

-   users holding jade/sJade
-   stakings
-   liquidity pools
-   airdrops
-   bonds
-   advisor streams

### Users holding tokens

The list of holders is fetched using an API that is indexing the blockchain to keep track on who is holding any token of the Jade ecosystem.
The relevant balances are then computed by quering the data by contract calls to the jade/sjade contract.

### Stakings

Staked amounts fall under the query for sJade since the two amounts are equivalent.

### LP

The quantity of token an user had deposited in a LP is proportional to the balance held in LP token. The holders of token are queries by fetching all events relative to the pool, their balances computed and scaled back into jade.

### Airdrops

Airdrops can be examined by reverse engineering the ABI encoded input of their initial setup transactions. This way, one can get all the allowed amounts for each user.
Then querying the list of claiming transactions, and the total amount filled in the contract, one can further compute the balance still allocated to users who have yet to claim.

### Bonds

The list of bonders regardless of the contract is fetched using the list of transactions for the bond, validating the amount of users to account for potential gnosis safes. The relevant data is then queries for each bond for each user. The bonds are supposed to be fully vested.

### Advisor streams

The list of events relative to stream creations is fetched and the contract is queried for the relevant IDs. The streams are supposed to be fully vested.

### Output

The human readable dataframe/table is `FINAL.csv`
The human readable dataframe/table before excluding all the irrelevant contracts is `FINAL_RAW.csv`
The site export to be displayed on the website on the breakdown page is under `website_export.json`

## Other operations

To fetch all claimer of the airdrop for window 1, run `make fetch_claimers`
The list is generated under `claimed.json`
