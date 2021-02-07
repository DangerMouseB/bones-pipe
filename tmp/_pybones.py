# *******************************************************************************
#
#    Copyright (c) 2019-2020 David Briant. All rights reserved.
#
# *******************************************************************************


import inspect, types
import contextlib

from coppertop import Missing

from bones_data.types import fUnary, BType
print('#fred')

_scopes = []

@contextlib.contextmanager
def setPybonesScope(scope):
    global _scopes
    _scopes.append(scope)
    try:
        yield scope
    finally:
        if not _scopes:
            raise RuntimeError("somehow there isn't a scope to pop off the stack")
        _scopes = _scopes[0:-1]


def getPybonesScope():
    if not _scopes:
        raise RuntimeError("there is no scope set")
    return _scopes[-1]


def pybones(*args, scope=Missing, name=Missing, sig=Missing, ret=Missing, flavour=fUnary, unbox=True):
    # scope - defaults to the getPybonesScope()
    # name - defaults to the python function name
    # sig - tuple of type for each arg
    if sig is Missing: raise TypeError('sig is Missing')
    if ret is Missing: raise TypeError('ret is Missing')


    def _process(fnOrClass):
        argNames = []
        if isinstance(fnOrClass, type):
            parameters = dict(inspect.signature(fnOrClass.__init__).parameters)
            selfName = list(parameters.keys())[0]
            del parameters[selfName]
        else:
            parameters = inspect.signature(fnOrClass).parameters
        for pName, parameter in parameters.items():
            if parameter.kind == inspect.Parameter.VAR_POSITIONAL:
                raise TypeError('Function must not include *%s' % pName)
            elif parameter.kind == inspect.Parameter.VAR_KEYWORD:
                raise TypeError('Function must not include **%s' % pName)
            else:
                if parameter.default == inspect.Parameter.empty:
                    argNames.append(pName)
                else:
                    raise TypeError('Function must not include %s=%s' % (pName, parameter.default))

        doc = fnOrClass.__doc__ if hasattr(fnOrClass, '__doc__') else ''
        _name = fnOrClass.__name__ if name is Missing else name
        _scope = getPybonesScope() if scope is Missing else scope
        requiresCtx = '_ctx' in argNames
        if requiresCtx:
            argNames = [n for n in argNames if n != '_ctx']
        _sig = (sig,) if isinstance(sig, BType) else sig    # handle the case when there's just the one arg
        _scope.names.registerPythonFunction(_name, _sig, ret, fnOrClass, requiresCtx, unbox, flavour)
        return fnOrClass

    if len(args) == 1 and isinstance(args[0], (types.FunctionType, types.MethodType, type)):
        # of form @pybones so args[0] is the function or class being decorated
        return _process(args[0])
    else:
        # of form as @pybones() or @Pipeable(overrideLHS=True) etc
        if len(args): raise TypeError("Only kwargs allowed")
        return _process