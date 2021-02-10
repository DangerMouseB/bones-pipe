# *******************************************************************************
#
#    Copyright (c) 2020-2021 David Briant. All rights reserved.
#
# *******************************************************************************

import itertools

from coppertop import Missing

from bones_data import BType, SV, BSum, BCount, BIndex, BOffset, BNum
from .._at_bones import bones



anon = BType('anon')             # unbound data structure - we are free to modify it inplace without consequence
named = BType('named')          # named data structure - can be converted to an anonymous struct just before
                                    # last access before a rebind, e.g. A = B * A * A' * C can be anonned after the '
                                    # and just before the * of A * A' and that * C can overwrite too
aliased = BType('aliased')       # we could keep a ref count but instead let's simplify by saying the type is now
                                    # aliased, e.g. B = A

vector = BType('vector')
fragmentedvector = BType('fragmentedvector')
offset = BType('offset')


@bones(numTypeArgs=1, unbox=True)
def to(t:vector[anon], l:list) -> vector[anon]:
    return l

@bones(numTypeArgs=1, unbox=True)
def to(t:vector[named], v:vector[anon]) -> vector[named]:
    return v

@bones(numTypeArgs=1, unbox=True)
def to(t:vector[anon], v:named[named]) -> vector[anon]:
    return v

@bones(numTypeArgs=1, unbox=True)
def to(t:vector[aliased], v:named[named]) -> vector[aliased]:
    return v

@bones(numTypeArgs=1, unbox=True)
def to(t:fragmentedvector[anon], fragments:tuple) -> fragmentedvector[anon]:
    return fragments


@bones
def atput(v:vector[anon], i:offset+int, x:int) -> vector[anon]:
    v._v[i] = x
    return v

@bones
def atput(v:vector[named]+vector[aliased], i:offset+int, x:int) -> vector[anon]:
    newv = list(v._v)
    newv[i] = x
    return newv >> to(vector[anon])

@bones
def at(v:vector[anon]+vector[named]+vector[aliased], i:offset+int) -> int:
    return v._v[i]

@bones
def fragmentedatput(v:vector[named]+vector[aliased], i:offset+int, x:int) -> fragmentedvector[anon]:
    old = v._v
    fragments = (old[:i], [x], old[i+1:])
    return fragments >> to(fragmentedvector[anon])

@bones
def at(v:fragmentedvector[anon]+fragmentedvector[named]+fragmentedvector[aliased], i:offset+int) -> int:
    o = i
    for fragment in v._v:
        if o > (len(fragment) - 1):
            o -= len(fragment)
        else:
            return fragment[o]


def testVector():
    # create an anonymous vector from a list (i.e. not bound to a name)
    v1 = [1,2,3] >> to(vector[anon])
    assert v1 >> at(...,0) == 1
    # since it's not bound to a name it can be modified in place
    v2 = v1 >> atput(..., 0, 3)
    assert v1 >> at(...,0) == 3
    assert v2 >> at(...,0) == 3
    # simulate binding it to a name and modify - answers a modified copy
    v3 = v2 >> to(vector[named])
    v4 = v3 >> atput(..., 0, 1)
    assert v3 >> at(..., 0) == 3
    assert v4 >> at(..., 0) == 1
    # and this time we use a memory efficient copy
    v5 = v3 >> fragmentedatput(..., 0, 1)
    assert v3 >> at(..., 0) == 3
    assert v5 >> at(..., 0) == 1



def test():
    testVector()
    print("Pass")



if __name__ == '__main__':
    test()
