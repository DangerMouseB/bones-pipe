# *******************************************************************************
#
#    Copyright (c) 2020-2021 David Briant. All rights reserved.
#
# *******************************************************************************

import itertools

from coppertop import Missing

from bones_data import BType, SV, BSum, BCount, BIndex, BOffset, BNum
from .._at_bones import bones

binary = BType('binary')  # predefined


num = BType('num')
ccy = num['ccy']      # in bones we can use num[`ccy]
fx = num(domestic=ccy, foreign=ccy)

GBP = ccy['GBP']
USD = ccy['USD']

GBP_USD = fx(domestic=GBP, foreign=USD)

@bones(numTypeArgs=2)
def to(d:ccy[D], f:ccy[F], rate:num) -> fx(domestic=ccy[D], foregin=ccy[F]):
    assert f == fx._s.f
    assert d._s == fx._s.d
    return d * fx >> to(f)

@bones(flavour=binary)
def mul(d:ccy[D], fx:fx(domestic=ccy[D], foreign=ccy[F])) -> ccy[F]:
    assert d._s == fx._s.domestic
    return d * fx >> to(fx._s.foreign)

cable = 1.3 >> to(fx(domestic=GBP, foreign=USD))
100 >> to(GBP) >> mul >> cable >> cout


def testFx():
    mySavings = 100 >> to(GBP)
    fxRate = 1.3 >> to(GBP_USD)
    mySavingsInUsd = mySavings * fxRate
    assert mySavingsInUsd._s == USD
    assert mySavingsInUsd._v == 130



def test():
    testVector()
    print("Pass")



if __name__ == '__main__':
    test()