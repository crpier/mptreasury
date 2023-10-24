from functools import partial

from result import as_result as as_result_base

from icecream import IceCreamDebugger


def raise_err(exc: OSError):
    return exc


ic = IceCreamDebugger(includeContext=True)
