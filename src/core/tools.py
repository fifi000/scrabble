from collections.abc import Callable, Hashable, Iterable
from typing import TypeVar


T = TypeVar('T')
U = TypeVar('U', bound='Hashable')


def distinct_by(iterable: Iterable[T], *, key: Callable[[T], U]) -> Iterable[T]:
    seen: set[U] = set()

    for item in iterable:
        if (result := key(item)) not in seen:
            yield item
            seen.add(result)


def split(
    iterable: Iterable[T], *, key: Callable[[T], bool]
) -> tuple[Iterable[T], Iterable[T]]:
    """
    Splits an iterable into two groups based on a predicate function.
    Args:
        iterable (Iterable[T]): The input iterable to be split.
        key (Callable[[T], bool]): A predicate function that determines the grouping.
            Items for which the predicate returns True are placed in the first group,
            and the rest in the second group.
    Returns:
        tuple[Iterable[T], Iterable[T]]: A tuple containing two lists:
            - The first list contains items for which the predicate returned True.
            - The second list contains the remaining items.
    Example:
        >>> split([1, 2, 3, 4], key=lambda x: x % 2 == 0)
        ([2, 4], [1, 3])
    """
    group1: list[T] = []
    group2: list[T] = []

    for item in iterable:
        if key(item):
            group1.append(item)
        else:
            group2.append(item)

    return group1, group2
