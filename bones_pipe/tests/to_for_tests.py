# *******************************************************************************
#
#    Copyright (c) 2020-2021 David Briant. All rights reserved.
#
# *******************************************************************************

from .._at_bones import bones
from bones_data import SV
from bones_data.predefined import tPyStr

@bones(numTypeArgs=1, unwrap=False)
def to(t: tPyStr, v: str) -> tPyStr:
    return SV(tPyStr, v)

