from bones.tests import test_types
from bones._pybones2 import bones, _globalScope
from bones.tests.to_for_test import to
from bones._core import TV
from bones.types import BType, tNull, tUTF8, tNullary, tN, tPyStr, BTypeEquals
# BSumType, BTupleType, BArrayType, BProductType, BUnnamedType,

from coppertop import cout, AssertEqual


tEntity = BType("entity", "tEntity")
tAsteroid = BType("asteroid", "tAsteroid")
tShip = BType("ship", "tShip")
tCollision = BType("collision", "tCollision")
tEvent = BType("event", "tEvent")


@bones(numTypeArgs=1, unwrap=False)
def to(t: tShip, v: str) -> tShip:
    return TV(tShip, v)

@bones(numTypeArgs=1, unwrap=False)
def to(t: tAsteroid, v: str) -> tAsteroid:
    return TV(tAsteroid, v)

@bones(numTypeArgs=1, unwrap=False)
def to(t: tEvent, v: str) -> tEvent:
    return TV(tEvent, v)

@bones
def collide(a: tAsteroid, b: tAsteroid) -> (tEvent+tNull):
    return [f'{a} split {b} (collide<:asteroid,asteroid:>)' >> to(tEvent)]

@bones
def collide(a: tShip, b: tAsteroid) -> (tEvent+tNull):
    return [
        f'{a} tried to ram {b} (collide<:ship,asteroid:>)' >> to(tEvent),
        'game over' >> to(tEvent)
    ]

@bones
def collide(a: tAsteroid, b: tShip) -> (tEvent+tNull):
    return [f'{a} destroyed {b} (collide<:asteroid,ship:>)' >> to(tEvent)]

@bones
def collide(a: tShip, b: tShip) -> (tEvent+tNull):
    return [
        TV(tNull, None),
        f'{a} bounced {b} (collide<:ship,ship:>)' >> to(tEvent)
    ]

@bones(unwrap=False)
def process(events: (tEvent+tNull)) -> tUTF8:
    descriptions = []
    # for i in range(len(events.v)):
    #     e = events.v[i]
    for e in events.v:
        descriptions += ['nothing' if e.t == tNull else e.v]
    return '\n'.join(descriptions)



tLinear = BType("linear", "tLinear")
tNormal = BType("normal", "tNormal")
tNum = BType("num", "tNum")

@bones(numTypeArgs=1, unwrap=False, flavour=tNullary)
def rand(dist: tLinear) -> tNum:
    return TV(tNum, 'linear')

@bones(numTypeArgs=1, unwrap=False, flavour=tNullary)
def rand(dist: tNormal) -> tNum:
    return TV(tNum, 'normal')



def testCollide():
    # TODO
    # BStructType('entityCore', 'tEntityCore', dict(id=tID, x=tNum, y=tNum))
    # BStructType('ship', 'tShip', dict(entity=tEntity, lives=tU8))
    # BSumType('collidable', 'tCollideable', [tEntityCore, tShip])
    # BSimpleTaggedType(tEntityCore, "tAsteroid", "tAsteroid")
    # BSimpleTaggedType(tEvent, "collision", "tCollision")

    ship1 = 'ship1' >> to(tShip)
    ship2 = 'ship2' >> to(tShip)
    ast1 = 'big asteroid' >> to(tAsteroid)
    ast2 = 'small asteroid' >> to(tAsteroid)

    cout << (ship1 >> collide(..., ship2) >> process) << '\n'
    cout << (ship1 >> collide(..., ast1) >> process) << '\n'
    cout << (ship2 >> collide(ast2, ...) >> process) << '\n'
    cout << (ast1 >> collide(..., ast2) >> process) << '\n'


def test_importedToWorks():
    _globalScope
    a = 'hello' >> to(tPyStr)
    b = TV(tPyStr, 'hello')
    'hello' >> to(tPyStr) >> AssertEqual >> TV(tPyStr, 'hello')


def testCompoundBTypes():
    # MUSTDO handle compound types + use types.d
    # WONTDO code types.d in pyd or directly in python api
    a = {}
    a[tN**(tUTF8+tNull)] = 1
    a[tN**(tUTF8+tNull)] >> AssertEqual >> 1

    # could solve this by wrapping types.d with BType in python - then all the identity checking is implemented in d
    # the dispatch (figuring out which fn to call from the sig) can be done be done in d
    # add tPy, tPyList, tPyTuple, tPyNumpy
    # also can add tNP for numpy arrays NPN**tF64, NPN**(tF64*tI32), NPM**NPN**F64 for an n x m numpy matix
    # the type descriptions can allow boxing to be done behind the scenes



# we provide multi dispatch, an algebraic type system and a pipe operator that is nullary, unary, binary,
# rmu and adverb aware together with a framework for wrapping and unwrapping tagged unions

def testTypeArgs():
    rand(tLinear)() >> AssertEqual >> TV(tNum, 'linear')
    rand(tNormal)() >> AssertEqual >> TV(tNum, 'normal')


@bones(unwrap=False)
def fred(a: int) -> int:
    return 1

@bones(unwrap=False)
def fred(a: int, d: int) -> int:
    return 2

def testFred1And2():
    fred(1) >> AssertEqual >> 1
    fred(1, 1) >> AssertEqual >> 2

def test_TV():
    x = TV(tPyStr._d(), "hello")
    print(x.getT())
    y = x.getT()
    a = x.getT()
    BTypeEquals(tPyStr, x.getT()) >> AssertEqual >> True
    x.getPyV() >> AssertEqual >> "hello"

def main():
    test_TV()
    test_importedToWorks()
    test_types.test()
    testFred1And2()
    testTypeArgs()
    testCollide()
    testCompoundBTypes()
    print("pass")


if __name__ == '__main__':
    main()
