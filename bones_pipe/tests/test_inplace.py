# *******************************************************************************
#
#    Copyright (c) 2020-2021 David Briant. All rights reserved.
#
# *******************************************************************************

import itertools

from coppertop import Missing

from bones_data import BType, SV, BSum, BCount, BIndex, BOffset, BNum
from .._at_bones import bones
from .to_for_tests import to


unbound = BType('unbound')
bound = BType('bound')
null = BType('null')
lhs = BType('lhs')
lhsStar = BType('lhsStar')
inout = BType('inout')

matrix = BType('matrix')
vector = BType('vector')
index = BType('index')
num = BType('num')
count = BType('count')
N = BType('N')


@bones(numTypeArgs=1)
def to(t: count, v: int) -> count:
    return BCount(v)


@bones
def _mnew(r:count, c:count) -> matrix[unbound]:
    next(_mnewCount)
    answer = Matrix([None] * c._v)
    for i in range(r._v):
        answer[i] = [None] * r._v
    answer.r = r
    answer.c = c
    return SV(matrix[unbound], answer)


@bones(numTypeArgs=1)
def to(t:matrix[unbound], x:BSum(list, tuple)) -> matrix[unbound]:
    r = len(x) >> to(count)
    c = len(x[0]) >> to(count)
    answer = _mnew(r, c)
    for i in idxRange(r):
        for j in idxRange(c):
            atIJPut(answer, i, j, BNum(x[i-1][j-1]))
    return answer


class Matrix(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.r = 0 >> to(count)
        self.c = 0 >> to(count)
    def __repr__(self):
        rowStrings = []
        for i in range(self.r._v):
            row = []
            for j in range(self.c._v):
                row += [self[j][i]]
            rowStrings += [f'[{",".join([str(e) for e in row])}]']
        return f'[{", ".join(rowStrings)}]'

class Vector(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = 0
    def __repr__(self):
        return f'[{",".join([str(e) for e in self])}]'


# fortran ordered
@bones(unbox=True)
def atIJ(M:matrix[inout]+matrix[unbound], i:index+int, j:index+int) -> num:
    next(_atIJCount)
    return M[j-1][i-1]

@bones(unbox=True)
def atIJPut(M:matrix[inout]+matrix[unbound], i:index+int, j:index+int, x:num) -> matrix[unbound]:
    next(_atIJPutCount)
    M[j-1][i-1] = x
    return M

@bones(unbox=True)
def atI(V:vector[inout]+vector[unbound], i:index+int) -> num:
    next(_atICount)
    return V[i-1]

@bones(unbox=True)
def atIPut(V:vector[inout]+vector[unbound], i:index+int, x:num) -> vector[unbound]:
    next(_atIPutCount)
    V[i-1] = x
    return V


# def atPutAnon(M:matrix[unbound], i:index, j:index, x:num) -> matrix[unbound]:
#     return atPut(M, i, j, x)
#
# def atPutLhs(M:matrix(lhs), i:index, j:index, x:num) -> matrix[lhsStar]:
#     return atPut(M, i, j, x)

@bones
def V(M:matrix[unbound], iV:index+int, i:index+int) -> num:
    return atIJ(M, i, iV)

@bones
def H(M:matrix[unbound], iH:index+int, i:index+int) -> num:
    return atIJ(M, iH, i)


@bones(unbox=True)
def _vnew(n:count) -> vector[unbound]:
    next(_vnewCount)
    answer = Vector([None] * n)
    answer.n = n >> to(count)
    return answer

@bones(unbox=True)
def idxRange(N:count) -> range:
    return range(1, N+1)

@bones(unbox=True)
def idxRange(i1: count, i2: count) -> range:
    return range(i1, i2 + 1)


@bones
def toVector(t:vector, x:BSum(list,tuple)) -> vector[unbound]:
    n = len(x)
    answer = _vnew(n)
    for i in idxRange(n):
        atIPut(answer, i, x[i-1])
    return answer

@bones
def mmul(A:matrix[unbound], B:matrix[unbound]) -> matrix[unbound]:
    assert A.c == B.r
    answer = _mnew(A.r, B.c)
    for iRow in idxRange(A.r):
        for iCol in idxRange(B.c):
            sum = BNum(0.0)
            for i in idxRange(A.c):
                sum += H(A, iRow, i)._v * V(B, iCol, i)._v
            answer = atIJPut(answer, iRow, iCol, sum)
    return answer

@bones
def mmulTrashA(A:matrix[inout], B:matrix, buf:vector[inout]) -> matrix[inout]:
    assert A.c == B.r
    nRows = A.r
    nCols = B.c
    nInner = A.c
    for iRow in idxRange(nRows):
        for iCol in idxRange(nCols):
            sum = 0.0
            for i in idxRange(nInner):
                sum += H(A, iRow, i) * V(B, iCol, i)
            atIPut(buf, iCol, sum)
        for iCol in idxRange(nCols):
            atIJPut(A, iRow, iCol, atI(buf, iCol))
    return A

@bones
def mmulTrashB(A:matrix, B:matrix[inout], buf:vector[inout]) -> matrix[inout]:
    assert A.c == B.r
    nRows = A.r
    nCols = B.c
    nInner = A.c
    for iCol in idxRange(nCols):
        for iRow in idxRange(nRows):
            sum = 0.0
            for i in idxRange(nInner):
                sum += H(A, iRow, i) * V(B, iCol, i)
            atIPut(buf, iRow, sum)
        for iRow in idxRange(nRows):
            atIJPut(B, iRow, iCol, atI(buf, iRow))
    return B

@bones
def mmul_AL_AL__AN(A:matrix[bound], B:matrix[bound]) -> matrix[unbound]:
    return mmul(A, B)

@bones
def mmul_LHS_ANON(A : lhs, B : unbound, S : unbound) -> null:
    pass

@bones
def mmulIP(A : lhs, B : bound, S : unbound) -> null:
    pass

@bones
def mT(A:matrix) -> matrix:
    pass

@bones
def mTDestroy(A:matrix) -> matrix[inout]:
    pass


def testNew():
    A = ((1.0, 2.0), (3.0, 4.0)) >> to(matrix[unbound])
    B = ((5.0, 6.0), (7.0, 8.0)) >> to(matrix[unbound])
    resetCounts()
    C = mmul(A, B)
    print("AB")
    printCounts()

    D = ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)) >> to(matrix[unbound])
    E = ((11.0, 12.0, 13.0), (14.0, 15.0, 16.0), (17.0, 18.0, 19.0)) >> to(matrix[unbound])
    resetCounts()
    print("DE")
    F = mmul(D, E)
    printCounts()

    G = ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)) >> to(matrix[unbound])
    H = ((11.0, 12.0, 13.0), (14.0, 15.0, 16.0), (17.0, 18.0, 19.0)) >> to(matrix[unbound])
    buf = _vnew(G.c)
    resetCounts()
    print("GH - destroy")
    mmulTrashA(G, H, buf)
    printCounts()
    assert F == G

    G = ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)) >> to(matrix[unbound])
    H = ((11.0, 12.0, 13.0), (14.0, 15.0, 16.0), (17.0, 18.0, 19.0)) >> to(matrix[unbound])
    buf = _vnew(G.c)
    resetCounts()
    print("GH - destroy")
    mmulTrashB(G, H, buf)
    printCounts()
    assert F == H

def testSquaring():
    A = ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)) >> to(matrix[unbound])
    resetCounts()
    print("AA")
    X = mmulNew(A, A)
    printCounts()

    buf = _vnew(A.c)
    B = ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)) >> to(matrix[unbound])
    resetCounts()
    print("AA - trash")
    Y = mmulTrashA(B, B, buf)
    printCounts()
    assert X == Y



def test():
    testNew()
    testSquaring()
    print("Pass")




_atICount = itertools.count(start=0)
_atIPutCount = itertools.count(start=0)
_atIJCount = itertools.count(start=0)
_atIJPutCount = itertools.count(start=0)
_mnewCount = itertools.count(start=0)
_vnewCount = itertools.count(start=0)

def resetCounts():
    global _atICount, _atIPutCount, _atIJCount, _atIJPutCount, _mnewCount, _vnewCount
    _atICount = itertools.count(start=0)
    _atIPutCount = itertools.count(start=0)
    _atIJCount = itertools.count(start=0)
    _atIJPutCount = itertools.count(start=0)
    _mnewCount = itertools.count(start=0)
    _vnewCount = itertools.count(start=0)

def printCounts():
    print(f'_atICount: {_atICount}')
    print(f'_atIPutCount: {_atIPutCount}')
    print(f'_atIJCount: {_atIJCount}')
    print(f'_atIJPutCount: {_atIJPutCount}')
    print(f'_mnewCount: {_mnewCount}')
    print(f'_vnewCount: {_vnewCount}')



if __name__ == '__main__':
    test()
