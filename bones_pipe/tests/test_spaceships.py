# *******************************************************************************
#
#    Copyright (c) 2020-2021 David Briant. All rights reserved.
#
# *******************************************************************************

from .._at_bones import bones
from .to_for_tests import to
from bones_data import SV, BType
from bones_data.predefined import tNull, tUTF8, tNullary, tN, tPyStr, tNum

from coppertop import cout, AssertEqual


tEntity = BType("entity")
tAsteroid = BType("asteroid")
tShip = BType("ship")
tCollision = BType("collision")
tEvent = BType("event")


@bones(numTypeArgs=1, unbox=True)
def to(t: tShip, v: str) -> tShip:
    return v

@bones(numTypeArgs=1, unbox=True)
def to(t: tAsteroid, v: str) -> tAsteroid:
    return v

@bones(numTypeArgs=1, unbox=True)
def to(t: tEvent, v: str) -> tEvent:
    return v

@bones(numTypeArgs=1, unbox=True)
def to(t: tUTF8, v: str) -> tUTF8:
    return v

@bones(numTypeArgs=1)
def to(t: tUTF8, v: tEvent) -> tUTF8:
    return SV(t, v._v)


@bones
def collide(a: tAsteroid, b: tAsteroid) -> tEvent+tNull:
    return f'{a._v} split {b._v} (collide<:asteroid,asteroid:>)' >> to(tEvent)

@bones
def collide(a: tShip, b: tAsteroid) -> tEvent+tNull:
    return f'{a._v} tried to ram {b._v} (collide<:ship,asteroid:>)' >> to(tEvent)

@bones
def collide(a: tAsteroid, b: tShip) -> tEvent+tNull:
    return f'{a._v} destroyed {b._v} (collide<:asteroid,ship:>)' >> to(tEvent)

@bones
def collide(a: tShip, b: tShip) -> tEvent+tNull:
    return SV(tNull, None)
#    return f'{a} bounced {b} (collide<:ship,ship:>)' >> to(tEvent)


@bones
def process(e: tEvent+tNull) -> tUTF8:
    return 'nothing' >> to(tUTF8) if e._s == tNull else (e >> to(tUTF8))






def testCollide():

    ship1 = 'ship1' >> to(tShip)
    ship2 = 'ship2' >> to(tShip)
    ast1 = 'big asteroid' >> to(tAsteroid)
    ast2 = 'small asteroid' >> to(tAsteroid)

    cout << (ship1 >> collide(..., ship2) >> process)._v << '\n'
    cout << (ship1 >> collide(..., ast1) >> process)._v << '\n'
    cout << (ship2 >> collide(ast2, ...) >> process)._v << '\n'
    cout << (ast1 >> collide(..., ast2) >> process)._v << '\n'



def test_SV():
    x = SV(tPyStr, "hello")
    tPyStr >> AssertEqual >> x._s
    x._v >> AssertEqual >> "hello"



@bones
def fred(a: int) -> int:
    return 1
@bones
def fred(a: int, d: int) -> int:
    return 2

def testFred1And2():
    fred(1) >> AssertEqual >> 1
    fred(1, 1) >> AssertEqual >> 2



tLinear = BType("linear")
tNormal = BType("normal")

@bones(numTypeArgs=1, flavour=tNullary)
def rand(dist: tLinear) -> tNum:
    return SV(tNum, 'linear')
@bones(numTypeArgs=1, flavour=tNullary)
def rand(dist: tNormal) -> tNum:
    return SV(tNum, 'normal')

def testTypeArgs():
    rand(tLinear)() >> AssertEqual >> SV(tNum, 'linear')
    rand(tNormal)() >> AssertEqual >> SV(tNum, 'normal')


def test_importedToWorks():
    a = 'hello' >> to(tPyStr)
    b = SV(tPyStr, 'hello')
    'hello' >> to(tPyStr) >> AssertEqual >> SV(tPyStr, 'hello')




def main():
    test_SV()
    testFred1And2()
    testTypeArgs()
    test_importedToWorks()
    testCollide()
    print("pass")


if __name__ == '__main__':
    main()
