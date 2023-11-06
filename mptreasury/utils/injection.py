from collections.abc import Callable
from inspect import _ParameterKind, signature
from typing import Any, Awaitable, ParamSpec, TypeVar


class MissingDependencyError(Exception):
    ...


class IncorrectInjectableSignatureError(Exception):
    ...


class DoubleInjectionError(Exception):
    ...


_INJECTS: dict[str, object] = {}
_LAZY_INJECTS: dict[str, Callable[[], Any]] = {}


class Injected:
    ...


_P = ParamSpec("_P")
_T = TypeVar("_T")


def injectable(func: Callable[_P, Awaitable[_T]]) -> Callable[_P, Awaitable[_T]]:
    async def inner(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        for name, sig in signature(func).parameters.items():
            if sig.default is Injected:
                if sig.kind is not _ParameterKind.KEYWORD_ONLY:
                    msg = (
                        f"Injected parameter {name} in "
                        f"{func.__name__} must be keyword-only"
                    )
                    raise IncorrectInjectableSignatureError(msg)
                if kwargs.get(name) is not None:
                    pass
                elif sig.name in _LAZY_INJECTS:
                    _INJECTS[sig.name] = _LAZY_INJECTS[sig.name]()
                    del _LAZY_INJECTS[sig.name]
                    kwargs.update({name: _INJECTS[sig.annotation]})
                elif sig.name in _INJECTS:
                    kwargs.update({name: _INJECTS[sig.annotation]})
                else:
                    msg = (
                        "Missing dependency for "
                        f"{name}: {sig.annotation} in {func.__name__}"
                    )
                    raise MissingDependencyError(msg)
        return await func(*args, **kwargs)

    return inner


def injectable_sync(func: Callable[_P, _T]) -> Callable[_P, _T]:
    def inner(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        for name, sig in signature(func).parameters.items():
            if sig.default is Injected:
                if sig.kind is not _ParameterKind.KEYWORD_ONLY:
                    msg = (
                        f"Injected parameter {name} in "
                        f"{func.__name__} must be keyword-only"
                    )
                    raise IncorrectInjectableSignatureError(msg)
                # Don't inject the arg if it was provided to the function
                if kwargs.get(name) is not None:
                    pass
                elif name in _LAZY_INJECTS:
                    _INJECTS[name] = _LAZY_INJECTS[name]()
                    del _LAZY_INJECTS[name]
                    kwargs.update({name: _INJECTS[name]})
                elif sig.name in _INJECTS:
                    kwargs.update({name: _INJECTS[name]})
                else:
                    msg = (
                        f"Function {func.__name__} did not find {name} injected"
                    )
                    raise MissingDependencyError(msg)
        return func(*args, **kwargs)

    return inner


def add_injectable(name: str, injectable: Callable[[], Any]) -> None:
    if name in _INJECTS or name in _LAZY_INJECTS:
        msg = f"Injectable {name} already added"
        raise DoubleInjectionError(msg)
    _INJECTS[name] = injectable


def add_lazy_injectable(name: str, injectable: Callable[[], Any]) -> None:
    if name in _INJECTS or name in _LAZY_INJECTS:
        msg = f"Injectable {name} already added"
        raise DoubleInjectionError(msg)
    _LAZY_INJECTS[name] = injectable
