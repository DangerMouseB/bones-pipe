# *******************************************************************************
#
#    Copyright (c) 2020-2021 David Briant. All rights reserved.
#
# *******************************************************************************

from coppertop.testing import AssertEqual

from bones import pybones, setPybonesScope
from bones.names import getFnDetailsForSig, getBindingsForNameAndVerbType, newGlobalContext, newModuleContext
from bones_data.types import tNum, fBinary


def test_wrapper():
    globalCtx = newGlobalContext()
    moduleCtx = newModuleContext(globalCtx, moduleName='test')

    with setPybonesScope(moduleCtx.localScope):
        @pybones(sig=(tNum, tNum), ret=tNum)
        def add(x, y):
            '''adds two tPyInts'''
            return x + y

    bindings = getBindingsForNameAndVerbType(moduleCtx, 'add', fBinary)
    ret, sig, fn, requiresCtx, unbox = getFnDetailsForSig(bindings, (tNum, tNum))
    fn(1, 1) >> AssertEqual >> 2



def main():
    test_wrapper()
    print("pass")


if __name__ == '__main__':
    main()
