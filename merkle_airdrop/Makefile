init-hooks: 
	pre-commit install -c .tool_configurations/.pre-commit-config.yaml --install-hooks --overwrite
format-contracts:
	prettier --write '*/contracts/**/*.sol' -c .prettierrc.yaml
format-interfaces:
	prettier --write '*/interfaces/**/*.sol'
isort:
	isort --settings-file .tool_configurations/isort.cfg .

autopep8:
	autopep8 -j 0 --in-place --global-config .tool_configurations/autopep8 --ignore-local-config .

format-python: isort autopep8

format-all: format-contracts format-python

avax-fork-legacy:
	ganache-cli --fork https://api.avax.network/ext/bc/C/rpc \
	--allowUnlimitedContractSize True -m brownie -d brownie

fuji-fork-legacy:
	ganache-cli -f https://api.avax-test.network/ext/bc/C/rpc -a 11 -m brownie -d brownie \
	--allowUnlimitedContractSize True

fuji-fork:
	ganache-cli --fork https://api.avax-test.network/ext/bc/C/rpc -a 11 -m brownie \
	--chain.allowUnlimitedContractSize true -k istanbul

fuji-fork-past:
	ganache-cli -f https://api.avax-test.network/ext/bc/C/rpc@12615630 -a 11 -m brownie -d brownie \
	--allowUnlimitedContractSize True

avax-fork:
	ganache-cli --fork https://api.avax.network/ext/bc/C/rpc --wallet.totalAccounts 10 \
	-m brownie \
	 --chain.allowUnlimitedContractSize true -k istanbul --miner.blockTime 0 --miner.instamine=eager --chain.vmErrorsOnRPCResponse

metis-fork:
	ganache-cli --fork https://andromeda.metis.io/?owner=1088 --wallet.totalAccounts 10 \
	-m brownie \
	 --chain.allowUnlimitedContractSize true -k istanbul --miner.blockTime 0 --miner.instamine=eager --chain.vmErrorsOnRPCResponse

avax-fork-exploit:
	ganache-cli --fork https://api.avax.network/ext/bc/C/rpc@26343613 --wallet.totalAccounts 10 \
	-m brownie \
	 --chain.allowUnlimitedContractSize true -k istanbul --miner.blockTime 0 --miner.instamine=eager --chain.vmErrorsOnRPCResponse
generate-interfaces:
	python py_vector/py_vector/common/interface_generation.py all
	make format-interfaces

clear-build_metis:
	rm -rf metis/build

clear-build_vector:
	rm -rf vector/build

run-slither:
	make clear-build
	rm -f slither.sarif
	export IS_ALTERNATIVE_COMPILATION=True
	slither .
	export IS_ALTERNATIVE_COMPILATION=False

run-slither-silent:
	run-slither 2> /dev/null

run-slither-windows:
	clear-build
	rm -f slither.sarif
	set IS_ALTERNATIVE_COMPILATION=True
	slither .
	set IS_ALTERNATIVE_COMPILATION=False

add-metis-mainnet:
	brownie networks add Metis metis-main host=https://andromeda.metis.io/?owner=1088 chainid=1088 explorer=https://andromeda-explorer.metis.io/api
add-metis-fork:
	brownie networks add Metis metis-fork host=http://127.0.0.1:8545 chainid=1088 explorer=https://andromeda-explorer.metis.io/api
