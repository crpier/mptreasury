from inspect import _ParameterKind, signature
from typing import Awaitable, Callable, Hashable, ParamSpec, TypeVar


class MissingDependencyError(Exception):
    ...


class IncorrectInjectableSignatureError(Exception):
    ...


class DoubleInjectionError(Exception):
    ...


_INJECTS: dict[Hashable, object] = {}


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
                elif sig.annotation in _INJECTS:
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
                if kwargs.get(name) is not None:
                    pass
                elif sig.annotation in _INJECTS:
                    kwargs.update({name: _INJECTS[sig.annotation]})
                else:
                    msg = (
                        "Missing dependency for "
                        f"{name}: {sig.annotation} in {func}"
                    )
                    raise MissingDependencyError(msg)
        return func(*args, **kwargs)

    return inner


def add_injectable(annotation: Hashable, injectable: object) -> None:
    if annotation in _INJECTS:
        msg = f"Injectable {annotation} already added"
        raise DoubleInjectionError(msg)
    _INJECTS[annotation] = injectable
