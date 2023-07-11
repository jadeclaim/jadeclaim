import brownie
from brownie import Contract, chain

ids = [1086, 1087]
import time


def main():
    furo = Contract.from_explorer("0x4ab2fc6e258a0ca7175d05ff10c5cf798a672cae")

    time.sleep(2)
    bento = Contract.from_explorer("0xf5bce5077908a1b7370b9ae04adc565ebd643966")
    streams_balances = [furo.streamBalanceOf(i) for i in ids]
    streams_infos = [furo.streams(i) for i in ids]
    print(streams_balances)
    print(streams_infos)


#     0xc29fd306af08520aa902b57b1985fc042b249fe9
#  0x8d214bdeaf75d7b849e6a7172201caa4170eb07a
# 0x0941489115adccaa85187daa2d94b298c402abdf
#
# 0x8e2311ca48b52649fc2f0535c504ddc07c654f70
#
# 0x14a5b1024d705f5a65ed04e78467deaeb2568f4e
# 0x63ebd83e6d44187fe24010fac973e3f073a988a9
# 0x2c6ca13a52613936a66f0e7b065528eba702e017
# 0xABFc7d11564771540302608d9f79f3875f43299D
# 0x92f28d85cc17818c043e6465b5c40068025cf760
#
# 0x12a202040eef8ced7a3d0305b081e51d902feab1
#
# 0x5a921caa437e84b2220de551b7fd64fdbfff8cc7
#
# 0xf8c65b810b194a3834213a601e32078a212f7e5a
#
# 0x3f395bc86abe61bc67b40f6c607270447773072d
#
# 0x18812d8f4622ae3dbc6581950f2d2d4c02b527fa
#
# 0x429a523342c79fcf5c75ffc42b60da0b7750f222
#
# 0xf8173c007c27f54a753b97eaa6fdfbde3491ae39
#
# 0x35dae5ed3ced773f9e8c99cacb6af8710ad1833a
#
# 0xa72f4624dfdfa8de935e4f6fe5538d6fc76dfb32
#
# 0x22111a30eef559238710e70bbf3d66f82ec47f1d
#
# 0xa12cdd911f8eb828c38fe0e9487deb19dffe02e0x02D0369F908DC5ff918A6B8242d87334903aa3d81
#
# 0xa12cdd911f8eb828c38fe0e9487deb19dffe02e1
#
