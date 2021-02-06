# *******************************************************************************
#
#    Copyright (c) 2018-2021 David Briant. All rights reserved.
#
# *******************************************************************************

import inspect, types
import contextlib

from coppertop import Missing

from bones_data import BType, SV
from bones_data.predefined import tNullary, tUnary, tBinary, tRmu, tAdverb

class ProgrammerError(Exception):pass


_I_FRAME = 0
_I_FILENAME = 1
_I_FUNCTION = 3

_globalScope = {}



def _typeOfArg(x):
    if isinstance(x, SV):
        return x.s
    else:
        return type(x)




class PolyFn(object):

    def __init__(self, name, numTypeArgs, flavour, fullModuleName):
        self.name = name
        self.numTypeArgs = numTypeArgs
        self.flavour = flavour
        self.fullModuleName = fullModuleName
        self.detailsBySig = {}

    def _doCall(self, args):
        sig = tuple(args[:self.numTypeArgs]+tuple(_typeOfArg(arg) for arg in args[self.numTypeArgs:]))
        details = _selectTarget(sig, self.detailsBySig)
        if details is Missing:
            raise TypeError(f"{self.fullModuleName} - no matches for {repr(sig)}")
        ret, function, unwrap = details
        if unwrap:
            v = function(*tuple(_unwrap(t, arg) for t, arg in zip(sig, args)))
            answer = _wrap(ret, v)
        else:
            answer = function(*args)
        if isinstance(ret, BType):
            if not isinstance(_typeOfArg(answer), BType) or answer.s not in ret:
                raise TypeError(f"Trying to return a {_typeOfArg(answer)} from {self.fullModuleName} which specifies {ret}")
        else:
            if not isinstance(answer, ret):
                raise TypeError(f"Trying to return a {_typeOfArg(answer)} from {self.fullModuleName} which specifies {ret}")
        return answer

    def __call__(self, *args):
        if self.numTypeArgs > 0:
            if len(args) != self.numTypeArgs:
                # type args must specified (currently can't see a reason for allowing them to be partial)
                raise TypeError(f'Must provide {self.numTypeArgs} type args')
            # just the type args are being provided - all flavours
            return _Partial(args, Missing, Missing, self, self.flavour)
        else:
            if len(args) == 0:
                # nullary with no type args
                if self.flavour == tNullary:
                    return self._doCall(args)
                else:
                    raise ProgrammerError("flavour != tNullary yet called with no args")
            elif ... in args:
                # partial
                return _Partial((), args, _iMissings(args), self, self.flavour)
            else:
                # vanilla call
                return self._doCall(args)

    def __rrshift__(self, other):
        # other >> self
        if self.numTypeArgs > 0:
            raise TypeError("Type args have not been specified")
        if self.flavour == tNullary:
            raise TypeError("can't pipe arguments into a nullary fn")
        elif self.flavour == tUnary:
            return self._doCall((other,))
        elif self.flavour == tBinary:
            raise NotImplementedError()
        elif self.flavour == tRmu:
            raise NotImplementedError()
        elif self.flavour == tAdverb:
            raise NotImplementedError()
        else:
            raise ProgrammerError()

    def register(self, sig, ret, function, unwrap):
        if sig in self.detailsBySig:
            raise TypeError("duplicate registration")
        self.detailsBySig[sig] = ret, function, unwrap
        #print(f"{sig}, {tuple(t.id for t in sig)}  ---> {function.__name__}")


def _selectTarget(sig, detailsBySig):
    details = detailsBySig.get(sig, Missing)     # try matching on exact type first
    if details is Missing:                          # find first matching signature - we should check statically that there are no overlapping signatures
        numArgs = len(sig)
        for overload, deets in detailsBySig.items():
            if len(overload) != numArgs: continue
            found = True
            for st, ot in zip(sig, overload):
                if st not in ot:
                    found = False
                    break
            if found:
                details = deets
    return details


class _Partial(object):

    def __init__(self, typeArgs, args, iMissings, polyFn, flavour):
        assert isinstance(typeArgs, tuple)
        assert isinstance(args, tuple) or args is Missing
        self.typeArgs = typeArgs
        self.args = args
        self.iMissings = iMissings
        self.polyFn = polyFn
        self.flavour = flavour

    def __rrshift__(self, arg):
        # other >> self
        if self.flavour == tUnary:
            if self.args is Missing:
                # just the one arg in total
                return self.polyFn._doCall(self.typeArgs+(arg,))
            if len(self.iMissings) == 1:
                iMissing = self.iMissings[0]
                return self.polyFn._doCall(self.typeArgs+self.args[:iMissing]+(arg,)+self.args[iMissing+1:])
            raise TypeError("Must provide all missing args not just pipe one arg in")
        elif self.flavour == tBinary:
            raise NotImplementedError()
        elif self.flavour == tRmu:
            raise NotImplementedError()
        elif self.flavour == tAdverb:
            raise NotImplementedError()
        else:
            raise ProgrammerError()

    def __call__(self, *args):
        if self.args is not Missing:
            # blend args into self.args
            if len(args) != self.iMissings:
                raise TypeError(f"Wrong number of args - {len(args)} provided, {len(self.iMissings)} needed")
            newArgs = list(args)      # make a copy
            for i, arg in zip(self.iMissings, args):
                newArgs[i, arg]
            args = tuple(newArgs)
        if ... in args:
            _Partial(self.typeArgs, args, _iMissings(args), self.polyFn, self.flavour)
        else:
            return self.polyFn._doCall(self.typeArgs+args)

def _iMissings(args):
    iMissings = []
    for i, e in enumerate(args):
        if not isinstance(e, SV) and e == ...:
            iMissings += [i]
    return iMissings



def bones(*args, scope=Missing, name=Missing, sig=Missing, ret=Missing, flavour=tUnary, unwrap=False, numTypeArgs=0):
    # scope - defaults to the getPybonesScope()
    # name - defaults to the python function name
    # sig - tuple of type for each arg
    # if sig is Missing: raise TypeError('sig is Missing')
    # if ret is Missing: raise TypeError('ret is Missing')

    def registerFn(fn):
        if isinstance(fn, type):
            # class
            raise TypeError(f"Can't wrap classes - '{fn.__name__}'")

        # function
        _ret = inspect.signature(fn).return_annotation if ret is Missing else ret
        if _ret is inspect._empty:
            raise TypeError(f"No return type specified for function '{fn.__name__}'")
        argNames = []
        argTypes = []
        for pName, parameter in inspect.signature(fn).parameters.items():
            if parameter.kind == inspect.Parameter.VAR_POSITIONAL:
                raise TypeError('Function must not include *%s' % pName)
            elif parameter.kind == inspect.Parameter.VAR_KEYWORD:
                raise TypeError('Function must not include **%s' % pName)
            else:
                if parameter.default == inspect.Parameter.empty:
                    argNames += [pName]
                    argTypes += [parameter.annotation]
                else:
                    raise TypeError('Function must not include %s=%s' % (pName, parameter.default))
        _sig = (sig,) if isinstance(sig, BType) else sig  # handle the case when there's just the one arg
        _sig = tuple(argTypes) if _sig is Missing else _sig
        # _sig = tuple(bhash(e) for e in _sig)
        for argType, argName in zip(_sig, argNames):
            if argType is inspect._empty:
                raise TypeError(f"No type for '{argName}' for function '{fn.__name__}'")
        doc = fn.__doc__ if hasattr(fn, '__doc__') else ''
        _name = fn.__name__ if name is Missing else name

        # figure if a function of the same name has been imported and copy it's detailsBySig if so
        s = inspect.stack()
        if (s[1].function != '<module>') and (s[1].function != 'bones'):
            raise SyntaxError('@bones is only allowed on module level functions')
        iModule = -1
        for i in range(3):
            if s[i][_I_FUNCTION] == '<module>':
                iModule = i
                break
        if iModule == -1:
            raise SyntaxError('Can\'t find module within 2 levels')
        module = inspect.getmodule(s[iModule][_I_FRAME])
        moduleName = inspect.getmodulename(s[iModule][_I_FILENAME])
        packageName = module.__package__
        myFullModuleName = packageName + "." + moduleName + '.' + _name

        # MUSTDO have global scope and bones scopes - function, parent fns, module, global
        # global is where we store non-application provided constants and functions
        _scope = _globalScope if scope is Missing else scope
        polyFn = _globalScope.get(myFullModuleName, Missing)
        if polyFn is Missing:
            polyFn = _globalScope[myFullModuleName] = PolyFn(_name, numTypeArgs, flavour, myFullModuleName)
        if polyFn.numTypeArgs != numTypeArgs:
            raise TypeError("Similar named functions must have the same number of type args")

        objWithMyName = [o for o in inspect.getmembers(module) if o[0] == _name]
        otherFullModuleName = myFullModuleName
        if objWithMyName and isinstance(objWithMyName[0][1], PolyFn):
            otherFullModuleName = objWithMyName[0][1].fullModuleName
            if myFullModuleName != otherFullModuleName:
                importedPolyFn = objWithMyName[0][1]
                for otherSig, (otherRet, otherFunction, otherUnwrap) in importedPolyFn.detailsBySig.items():
                    polyFn.register(otherSig, otherRet, otherFunction, otherUnwrap)
        polyFn.register(_sig, _ret, fn, unwrap)
        return polyFn

    if len(args) == 1 and isinstance(args[0], (types.FunctionType, types.MethodType, type)):
        # of form @bones so args[0] is the function or class being decorated
        return registerFn(args[0])

    elif len(args) == 1 and isinstance(args[0], str):
        # of form  @bones('<typelang>')
        raise NotImplementedError()

    else:
        # of form as @bones() or @Pipeable(overrideLHS=True) etc
        if len(args): raise TypeError("Only kwargs allowed")
        return registerFn



def _unwrap(t, x):
    # ignore specified type for the moment
    if isinstance(x, SV):
        return x.v
    else:
        return x

def _wrap(t, v):
    # ignore specified type for the moment
    if isinstance(v, SV):
        return v
    else:
        return SV(t, v)

