# *******************************************************************************
#
#    Copyright (c) 2020-2021 David Briant. All rights reserved.
#
# *******************************************************************************

import itertools

from coppertop import Missing


_tSeed = itertools.count(start=0)
_tNameSeed = itertools.count(start=1)


class T(object):
    def __init__(self, name=Missing):
        self.id = next(_tSeed)
        self.name = name if name is not Missing else f't{next(_tNameSeed)}'
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return self.name
    def __pow__(self, power, modulo=None):
        return self
    def __getitem__(self, item):
        if len(namedAttributes) == 0:
            if len(attributes) == 0:
                raise TypeError("Need attributes and/or namedAttributes")
            if len(attributes) == 1:
                return STT(self, attributes[0])
            return ATT(self, *attributes)
        else:
            raise NotImplementedError()


class STT(T):
    def __init__(self, parent, tag, name=Missing):
        super().__init__(name)
        self.parent = parent
        self.tag = tag
    def __str__(self):
        return f'{self.parent}({self.tag})'



anon = T('anon')
aliased = T('aliased')
lhs = T('lhs')
lhsStar = T('lhsStar')
matrix = T('matrix')
vector = T('vector')
index = T('index')
num = T('num')
count = T('count')
N = T('N')
inout = T('inout')


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
def atIJ(M:matrix, i:index, j:index) -> num:
    next(_atIJCount)
    return M[j-1][i-1]

def atIJPut(M:matrix[inout], i:index, j:index, x:num) -> matrix:
    next(_atIJPutCount)
    M[j-1][i-1] = x
    return M

def atI(V:vector, i:index) -> num:
    next(_atICount)
    return V[i-1]

def atIPut(V:vector[inout], i:index, x:num) -> vector:
    next(_atIPutCount)
    V[i-1] = x
    return V


# def atPutAnon(M:matrix[anon], i:index, j:index, x:num) -> matrix[anon]:
#     return atPut(M, i, j, x)
#
# def atPutLhs(M:matrix(lhs), i:index, j:index, x:num) -> matrix[lhsStar]:
#     return atPut(M, i, j, x)

def V(M:matrix, iV:index, i:index) -> num:
    return atIJ(M, i, iV)

def H(M:matrix, iH:index, i:index) -> num:
    return atIJ(M, iH, i)

def mnew(r:count, c:count) -> matrix[anon]:
    next(_mnewCount)
    answer = Matrix([None] * c)
    for i in range(r):
        answer[i] = [None] * r
    answer.r = r
    answer.c = c
    return answer

def vnew(n:count) -> vector[anon]:
    next(_vnewCount)
    answer = Vector([None] * n)
    answer.n = n
    return answer

def indexes(i1orN:count, i2:count=Missing) -> N**index:
    if i2 is Missing:
        return range(1, i1orN+1)
    else:
        return range(i1orN, i2+1)

def toMatrix(t:matrix, x:list) -> matrix[anon]:
    r = len(x)
    c = len(x[0])
    answer = mnew(r, c)
    for i in indexes(r):
        for j in indexes(c):
            atIJPut(answer, i, j, x[i-1][j-1])
    answer.r = r
    answer.c = c
    return answer

def toVector(t:vector, x:list) -> vector[anon]:
    n = len(x)
    answer = vnew(n)
    for i in indexes(n):
        atIPut(answer, i, x[i-1])
    return answer

def mmulNew(A:matrix, B:matrix) -> matrix:
    assert A.c == B.r
    answer = mnew(A.r, B.c)
    for iRow in indexes(A.r):
        for iCol in indexes(B.c):
            sum = 0.0
            for i in indexes(A.c):
                sum += H(A, iRow, i) * V(B, iCol, i)
            answer = atIJPut(answer, iRow, iCol, sum)
    return answer

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

def mmul_AL_AL__AN(A:matrix(aliased), B:matrix(aliased)) -> matrix[anon]:
    return mmulNew(A, B)

def mmul_LHS_ANON(A : lhs, B : anon, S : anon):
    pass

def mmulIP(A : lhs, B : aliased, S : anon):
    pass

def mT(A:matrix) -> matrix:
    pass

def mTDestroy(A:matrix) -> matrix[inout]:
    pass


def testNew():
    A = toMatrix(matrix, ((1.0, 2.0), (3.0, 4.0)) )
    B = toMatrix(matrix, ((5.0, 6.0), (7.0, 8.0)) )
    resetCounts()
    C = mmulNew(A, B)
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
    buf = vnew(G.c)
    resetCounts()
    print("GH - destroy")
    mmulTrashA(G, H, buf)
    printCounts()
    assert F == G

    G = toMatrix(matrix, ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)) )
    H = toMatrix(matrix, ((11.0, 12.0, 13.0), (14.0, 15.0, 16.0), (17.0, 18.0, 19.0)) )
    buf = vnew(G.c)
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

    buf = vnew(A.c)
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

if __name__ == '__main__':
    test()
