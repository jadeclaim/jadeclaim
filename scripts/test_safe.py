from brownie import SignatureStorage, accounts, interface

SAFE = "0x48752A9e64B6Ca04064E53941f3Dae0299319a00"


def main():
    safe = interface.IGnosis(SAFE)
    owner1 = accounts.load("jade", "jade")
    msg = "lapin"
    msg = owner1.sign_defunct_message(msg)
    safe_sig = "0xf78e97488c79656d2ffd11cc404a6c60b5a7ab7ce06db1c8523d642fbad1936a57ef5b2a508d0e2a1fa59795f48095a17938ee45b578ef6fbe1a5431e2bacd3c1b94c83e5418b965fb555ed8ab5062ce5e54145186b7596305d3c7255e8ea38be933b691e0a0883182b9ef275d0db1ce8c56f73d5882ea636136460e5cd61ee6c01b"
    print(len(safe_sig))
    msg_hash = msg.messageHash.hex()
    print(msg_hash)
    storage = SignatureStorage.deploy(msg_hash, {"from": owner1})
    print(safe.isValidSignature(msg_hash, safe_sig))
    # print(storage.checkGnosis2(msg_hash, safe_sig, safe, {"from": owner1}))
    print(storage.checkSignature(msg_hash, "0x11", safe, {"from": owner1}))
    print(
        storage.checkSignature(msg_hash, msg.messageHash.hex(), safe, {"from": owner1})
    )

    print(storage.checkSignature(msg_hash, safe_sig, safe, {"from": safe}))
    print(storage.checkSignature(msg_hash, msg.signature.hex(), safe, {"from": safe}))
    print(storage.checkSignature(msg_hash, msg.signature.hex(), owner1, {"from": safe}))
