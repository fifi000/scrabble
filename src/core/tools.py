from collections.abc import Callable, Hashable, Iterable, Iterator, Mapping
from typing import TYPE_CHECKING, Any, overload

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison, SupportsRichComparisonT
else:
    from typing import Any as SupportsRichComparison
    from typing import Any as SupportsRichComparisonT


def distinct_by[T, U: Hashable](
    iterable: Iterable[T], *, key: Callable[[T], U]
) -> Iterator[T]:
    seen: set[U] = set()

    for item in iterable:
        if (result := key(item)) not in seen:
            yield item
            seen.add(result)


def split[T](
    iterable: Iterable[T], *, key: Callable[[T], bool]
) -> tuple[list[T], list[T]]:
    group1: list[T] = []
    group2: list[T] = []

    for item in iterable:
        if key(item):
            group1.append(item)
        else:
            group2.append(item)

    return group1, group2


def split_pairs[T, U](iterable: Iterable[tuple[T, U]]) -> tuple[list[T], list[U]]:
    group1: list[T] = []
    group2: list[U] = []

    for a, b in iterable:
        group1.append(a)
        group2.append(b)

    return group1, group2


def find_arg[T](args: Iterable[Any], kwargs: Mapping[str, Any], type_: type[T]) -> T:
    for arg in args:
        if isinstance(arg, type_):
            return arg

    for arg in kwargs.values():
        if isinstance(arg, type_):
            return arg

    raise ValueError(f"No argument of type '{type_.__name__!r}' found in arguments")


def all_same(iterable: Iterable[Any]) -> bool:
    it = iter(iterable)

    try:
        first = next(it)
    except StopIteration:
        return True
    else:
        return all(item == first for item in it)


@overload
def min_max(
    iterable: Iterable[SupportsRichComparisonT], /, *, key: None = None
) -> tuple[SupportsRichComparisonT, SupportsRichComparisonT]: ...


@overload
def min_max[T](
    iterable: Iterable[T], /, *, key: Callable[[T], SupportsRichComparison]
) -> tuple[T, T]: ...


def min_max[T](
    iterable: Iterable[T],
    /,
    *,
    key: Callable[[T], SupportsRichComparison] | None = None,
) -> tuple[T, T]:
    if key is not None:
        return min(iterable, key=key), max(iterable, key=key)
    else:
        # i guess i am correct on this one
        # user should get the type they pass: Iterable[_T] --> (_T, _T)
        # and the overload checks the case without 'key' parameter
        return min(iterable), max(iterable)  # type: ignore[return-value]


@overload
def max_min(
    iterable: Iterable[SupportsRichComparisonT], /, *, key: None = None
) -> tuple[SupportsRichComparisonT, SupportsRichComparisonT]: ...


@overload
def max_min[T](
    iterable: Iterable[T], /, *, key: Callable[[T], SupportsRichComparison]
) -> tuple[T, T]: ...


def max_min[T](
    iterable: Iterable[T],
    /,
    *,
    key: Callable[[T], SupportsRichComparison] | None = None,
) -> tuple[T, T]:
    min_, max_ = min_max(iterable, key=key)  # type: ignore[asignment]
    return max_, min_
