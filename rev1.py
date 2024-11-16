from typing import Callable, Concatenate, Protocol, runtime_checkable

def fmap_arrow[**P, F1, F2](g: Callable[[F1], F2], f: Callable[P, F1]) -> Callable[P, F2]:
    def inner(*args: P.args, **kwargs: P.kwargs) -> F2:
        return g(f(*args, **kwargs))
    return inner

def one_step[F,S,**R,Res](
    f: Callable[Concatenate[F,S,R], Res]
) -> Callable[[F],Callable[Concatenate[S,R], Res]]:
    def outer(first: F) -> Callable[Concatenate[S, R], Res]:
        def inner(second: S, /, *args: R.args, **kwargs: R.kwargs) -> Res:
            return f(first, second, *args, **kwargs)
        return inner
    return outer

@runtime_checkable
class Pipelike[O, I](Protocol):
    def __and__[NEW_I](self, _: Callable[[NEW_I], I], /) -> "Pipelike[O, NEW_I]": ...
    def __or__(self, _: I, /) -> O: ...
    def __call__(self, _: I, /) -> O: ...

class Pipe:
    def __and__[O, I](self, f: Callable[[I], O]) -> Pipelike[O, I]:
        def outer[O1, I1](f1: Callable[[I1], O1]) -> Pipelike[O1, I1]:
            class _Pipe:
                function: Callable[[I1], O1]
                def __init__(self, function: Callable[[I1], O1]):
                    self.function = function
                def __and__[NEW_I1](self, f2: Callable[[NEW_I1], I1]) -> Pipelike[O1, NEW_I1]:
                    def inner_compose[C, B, A](left: Callable[[B], C], right: Callable[[A], B]) -> Callable[[A], C]:
                        def inner(x: A) -> C:
                            return left(right(x))
                        return inner
                    return Pipe() & inner_compose(self.function, f2)
                def __or__(self, x: I1) -> O1:
                    return self.function(x)
                def __call__(self, x: I1) -> O1:
                    return self.function(x)

            return Pipe(f1)

        return outer(f)
