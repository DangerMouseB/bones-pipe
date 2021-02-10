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


inout = BType('inout')

matrix = BType('matrix')
vector = BType('vector')
index = BType('index')
num = BType('num')
count = BType('count')


@bones(numTypeArgs=1)
def to(t: count, v: int) -> count:
    return BCount(v)

@bones(numTypeArgs=1, unbox=True)
def to(t: matrix[inout], v: matrix) -> matrix[inout]:
    return v

@bones(numTypeArgs=1, unbox=True)
def to(t: vector[inout], v: vector) -> vector[inout]:
    return v

@bones(numTypeArgs=1)
def to(t:matrix, x:BSum(list, tuple)) -> matrix:
    r = len(x) >> to(count)
    c = len(x[0]) >> to(count)
    answer = new(matrix)(r, c)
    for i in idxRange(r):
        for j in idxRange(c):
            atIJPut(answer, i, j, BNum(x[i-1][j-1]))
    return answer

@bones(numTypeArgs=1)
def to(t:vector, x:BSum(list,tuple)) -> vector:
    n = len(x)
    answer = new(vector)(n)
    for i in idxRange(n):
        atIPut(answer, i, BNum(x[i-1]))
    return answer

@bones(numTypeArgs=1, unbox=True)
def new(t: vector, n:count) -> vector:
    next(_vnewCount)
    answer = Vector([None] * n)
    answer.n = n >> to(count)
    return answer

@bones(numTypeArgs=1)
def new(t:matrix, r:count, c:count) -> matrix:
    next(_mnewCount)
    answer = Matrix([None] * c._v)
    for i in range(r._v):
        answer[i] = [None] * r._v
    answer.r = r
    answer.c = c
    return SV(matrix, answer)

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
            rowStrings += [f'[{",".join([repr(e) for e in row])}]']
        return f'[{", ".join(rowStrings)}]'

class Vector(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = 0
    def __repr__(self):
        return f'[{",".join([repr(e) for e in self])}]'


# fortran ordered
@bones
def atIJ(M:matrix[inout]+matrix, i:index+int, j:index+int) -> num:
    next(_atIJCount)
    return M._v[j-1][i-1] >> to(num)

@bones(unbox=True)
def atIJPut(M:matrix[inout]+matrix, i:index+int, j:index+int, x:num) -> matrix:
    next(_atIJPutCount)
    M[j-1][i-1] = x
    return M

@bones
def atI(V:vector[inout]+vector, i:index+int) -> num:
    next(_atICount)
    return V._v[i-1] >> to(num)

@bones(unbox=True)
def atIPut(V:vector[inout]+vector, i:index+int, x:num) -> vector:
    next(_atIPutCount)
    V[i-1] = x
    return V

@bones
def V(M:matrix+matrix[inout], iV:index+int, i:index+int) -> num:
    return atIJ(M, i, iV)

@bones
def H(M:matrix+matrix[inout], iH:index+int, i:index+int) -> num:
    return atIJ(M, iH, i)

@bones(unbox=True)
def idxRange(n:count) -> range:
    return range(1, n+1)

@bones(unbox=True)
def idxRange(i1: count, i2: count) -> range:
    return range(i1, i2 + 1)

@bones
def mmul(A:matrix, B:matrix) -> matrix:
    # matrix multiplication
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
def mmul(A:matrix[inout], B:matrix, buf:vector[inout]) -> matrix[inout]:
    # matrix multiplication using a buffer so matrix A can be overwritten
    assert A.c == B.r
    nRows = A.r
    nCols = B.c
    nInner = A.c
    for iRow in idxRange(nRows):
        for iCol in idxRange(nCols):
            sum = BNum(0.0)
            for i in idxRange(nInner):
                sum += H(A, iRow, i) * V(B, iCol, i)
            atIPut(buf, iCol, sum)
        for iCol in idxRange(nCols):
            atIJPut(A, iRow, iCol, atI(buf, iCol))
    return A

@bones
def mmul(A:matrix, B:matrix[inout], buf:vector[inout]) -> matrix[inout]:
    # matrix multiplication using a buffer so matrix B can be overwritten
    assert A.c == B.r
    nRows = A.r
    nCols = B.c
    nInner = A.c
    for iCol in idxRange(nCols):
        for iRow in idxRange(nRows):
            sum = BNum(0.0)
            for i in idxRange(nInner):
                sum += H(A, iRow, i) * V(B, iCol, i)
            atIPut(buf, iRow, sum)
        for iRow in idxRange(nRows):
            atIJPut(B, iRow, iCol, atI(buf, iRow))
    return B

@bones
def T(A:matrix) -> matrix:
    # matrix transpose - answers a new matrix
    pass

@bones
def T(A:matrix[inout]) -> matrix[inout]:
    # matrix transpose - inplace
    pass


buf = new(vector)(64 >> to(count)) >> to(vector[inout])   # 64 bytes - 2 cache lines, 8 floats, enough for our example

def testNew():
    A = ((1.0, 2.0), (3.0, 4.0)) >> to(matrix)
    B = ((5.0, 6.0), (7.0, 8.0)) >> to(matrix)
    resetCounts()
    C = mmul(A, B)
    print("A.B")
    printCounts()

    D = ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)) >> to(matrix)
    E = ((11.0, 12.0, 13.0), (14.0, 15.0, 16.0), (17.0, 18.0, 19.0)) >> to(matrix)
    resetCounts()
    print("D.E")
    F = mmul(D, E)
    printCounts()

    G = ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)) >> to(matrix) >> to(matrix[inout])
    H = ((11.0, 12.0, 13.0), (14.0, 15.0, 16.0), (17.0, 18.0, 19.0)) >> to(matrix)

    resetCounts()
    print("G.H - overwrite G")
    mmul(G, H, buf)
    printCounts()
    assert F._v == G._v

    G = ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)) >> to(matrix)
    H = ((11.0, 12.0, 13.0), (14.0, 15.0, 16.0), (17.0, 18.0, 19.0)) >> to(matrix) >> to(matrix[inout])
    resetCounts()
    print("G.H - overwrite H")
    mmul(G, H, buf)
    printCounts()
    assert F._v == H._v


def testSquaring():
    A = ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)) >> to(matrix)
    resetCounts()
    print("A.A")
    X = mmul(A, A)
    printCounts()

    B = ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)) >> to(matrix)
    resetCounts()
    print("A.A - overwrite A (just needs to use more buffer space)")
    Y = mmul(B >> to(matrix[inout]), B, buf)
    printCounts()
    assert X._v == Y._v



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
