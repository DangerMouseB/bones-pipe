# *******************************************************************************
#
#    Copyright (c) 2020-2021 David Briant. All rights reserved.
#
# *******************************************************************************

import itertools

from coppertop import Missing

from bones_data import BType, SV
from .._at_bones import bones
from .to_for_tests import to


unbound = BType('unbound')
bound = BType('bound')

lhs = BType('lhs')
lhsStar = BType('lhsStar')
matrix = BType('matrix')
vector = BType('vector')
index = BType('index')
num = BType('num')
count = BType('count')
N = BType('N')
inout = BType('inout')


@bones(numTypeArgs=1)
def to(t: matrix, v: str) -> matrix:
    return SV(t, v)




def _mnew(r:count, c:count) -> matrix[unbound]:
    next(_mnewCount)
    answer = Matrix([None] * c)
    for i in range(r):
        answer[i] = [None] * r
    answer.r = r
    answer.c = c
    return answer


@bones(numTypeArgs=1)
def to(t:matrix[unbound], x:list) -> matrix[unbound]:
    r = len(x) >> to(count)
    c = len(x[0]) >> to(count)
    answer = _mnew(r, c)
    for i in indexes(r):
        for j in indexes(c):
            atIJPut(answer, i, j, x[i-1][j-1])
    answer.r = r
    answer.c = c
    return SV(t, answer)


class Matrix(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.r = 0
        self.c = 0
    def __repr__(self):
        rowStrings = []
        for i in indexes(self.r):
            row = []
            for j in indexes(self.c):
                row += [atIJ(self, i, j)]
            rowStrings += [f'[{",".join([str(e) for e in row])}]']
        return f'[{", ".join(rowStrings)}]'

class Vector(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = 0
    def __repr__(self):
        return f'[{",".join([str(e) for e in self])}]'


# fortran ordered
@bones
def atIJ(M:matrix, i:index, j:index) -> num:
    next(_atIJCount)
    return M[j-1][i-1]

@bones
def atIJPut(M:matrix[inout], i:index, j:index, x:num) -> matrix:
    next(_atIJPutCount)
    M[j-1][i-1] = x
    return M

@bones
def atI(V:vector, i:index) -> num:
    next(_atICount)
    return V[i-1]

@bones
def atIPut(V:vector[inout], i:index, x:num) -> vector:
    next(_atIPutCount)
    V[i-1] = x
    return V


# def atPutAnon(M:matrix[unbound], i:index, j:index, x:num) -> matrix[unbound]:
#     return atPut(M, i, j, x)
#
# def atPutLhs(M:matrix(lhs), i:index, j:index, x:num) -> matrix[lhsStar]:
#     return atPut(M, i, j, x)

@bones
def V(M:matrix, iV:index, i:index) -> num:
    return atIJ(M, i, iV)

@bones
def H(M:matrix, iH:index, i:index) -> num:
    return atIJ(M, iH, i)


@bones
def _vnew(n:count) -> vector[unbound]:
    next(_vnewCount)
    answer = Vector([None] * n)
    answer.n = n
    return answer

@bones
def indexes(i1orN:count, i2:count=Missing) -> N**index:
    if i2 is Missing:
        return range(1, i1orN+1)
    else:
        return range(i1orN, i2+1)


@bones
def toVector(t:vector, x:list) -> vector[unbound]:
    n = len(x)
    answer = _vnew(n)
    for i in indexes(n):
        atIPut(answer, i, x[i-1])
    return answer

@bones
def mmul(A:matrix[unbound], B:matrix[unbound]) -> matrix[unbound]:
    assert A.c == B.r
    answer = _mnew(A.r, B.c)
    for iRow in indexes(A.r):
        for iCol in indexes(B.c):
            sum = 0.0
            for i in indexes(A.c):
                sum += H(A, iRow, i) * V(B, iCol, i)
            answer = atIJPut(answer, iRow, iCol, sum)
    return answer

@bones
def mmulTrashA(A:matrix[inout], B:matrix, buf:vector[inout]) -> matrix[inout]:
    assert A.c == B.r
    nRows = A.r
    nCols = B.c
    nInner = A.c
    for iRow in indexes(nRows):
        for iCol in indexes(nCols):
            sum = 0.0
            for i in indexes(nInner):
                sum += H(A, iRow, i) * V(B, iCol, i)
            atIPut(buf, iCol, sum)
        for iCol in indexes(nCols):
            atIJPut(A, iRow, iCol, atI(buf, iCol))
    return A

@bones
def mmulTrashB(A:matrix, B:matrix[inout], buf:vector[inout]) -> matrix[inout]:
    assert A.c == B.r
    nRows = A.r
    nCols = B.c
    nInner = A.c
    for iCol in indexes(nCols):
        for iRow in indexes(nRows):
            sum = 0.0
            for i in indexes(nInner):
                sum += H(A, iRow, i) * V(B, iCol, i)
            atIPut(buf, iRow, sum)
        for iRow in indexes(nRows):
            atIJPut(B, iRow, iCol, atI(buf, iRow))
    return B

@bones
def mmul_AL_AL__AN(A:matrix(bound), B:matrix(bound)) -> matrix[unbound]:
    return mmulNew(A, B)

@bones
def mmul_LHS_ANON(A : lhs, B : unbound, S : unbound):
    pass

@bones
def mmulIP(A : lhs, B : bound, S : unbound):
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

    D = toMatrix(matrix, ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)) )
    E = toMatrix(matrix, ((11.0, 12.0, 13.0), (14.0, 15.0, 16.0), (17.0, 18.0, 19.0)) )
    resetCounts()
    print("DE")
    F = mmulNew(D, E)
    printCounts()

    G = toMatrix(matrix, ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)) )
    H = toMatrix(matrix, ((11.0, 12.0, 13.0), (14.0, 15.0, 16.0), (17.0, 18.0, 19.0)) )
    buf = _vnew(G.c)
    resetCounts()
    print("GH - destroy")
    mmulTrashA(G, H, buf)
    printCounts()
    assert F == G

    G = toMatrix(matrix, ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)) )
    H = toMatrix(matrix, ((11.0, 12.0, 13.0), (14.0, 15.0, 16.0), (17.0, 18.0, 19.0)) )
    buf = _vnew(G.c)
    resetCounts()
    print("GH - destroy")
    mmulTrashB(G, H, buf)
    printCounts()
    assert F == H

def testSquaring():
    A = toMatrix(matrix, ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)) )
    resetCounts()
    print("AA")
    X = mmulNew(A, A)
    printCounts()

    buf = _vnew(A.c)
    B = toMatrix(matrix, ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)) )
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
