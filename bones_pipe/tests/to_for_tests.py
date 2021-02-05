# *******************************************************************************
#
#    Copyright (c) 2020-2021 David Briant. All rights reserved.
#
# *******************************************************************************

from bones_pipe import bones
from bones_data import tPyStr, SV

@bones(numTypeArgs=1, unwrap=False)
def to(t: tPyStr, v: str) -> tPyStr:
    return SV(tPyStr, v)

