get_avax_data:
	brownie run scripts/avax_data.py --network avax-main

get_bsc_data:
	brownie run scripts/bsc_data.py --network bsc-main

fetch_claimers:
	brownie run scripts/fetch_all_claimed.py --network arbitrum-main

