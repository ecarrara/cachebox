"""
cachebox core ( written in Rust )
"""

import typing

__version__: str
__author__: str

version_info: typing.Tuple[int, int, int, bool]
""" (major, minor, patch, is_beta) """

KT = typing.TypeVar("KT")
VT = typing.TypeVar("VT")
DT = typing.TypeVar("DT")

class BaseCacheImpl(typing.Generic[KT, VT]):
    """
    This is the base class of all cache classes such as Cache, FIFOCache, ...

    Do not try to call its constructor, this is only for type-hint.
    """

    def __init__(
        self,
        maxsize: int,
        iterable: typing.Union[typing.Iterable[typing.Tuple[KT, VT]], typing.Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ) -> None: ...
    @staticmethod
    def __class_getitem__(*args) -> None: ...
    @property
    def maxsize(self) -> int: ...
    def __len__(self) -> int: ...
    def __sizeof__(self) -> int: ...
    def __bool__(self) -> bool: ...
    def __contains__(self, key: KT) -> bool: ...
    def __setitem__(self, key: KT, value: VT) -> None: ...
    def __getitem__(self, key: KT) -> VT: ...
    def __delitem__(self, key: KT) -> VT: ...
    def __str__(self) -> str: ...
    def __iter__(self) -> typing.Iterator[KT]: ...
    def __richcmp__(self, other: typing.Self, op: int) -> bool: ...
    def __getstate__(self) -> object: ...
    def __getnewargs(self) -> tuple: ...
    def __setstate__(self, state: object) -> None: ...
    def capacity(self) -> int: ...
    def is_full(self) -> bool: ...
    def is_empty(self) -> bool: ...
    def insert(self, key: KT, value: VT) -> typing.Optional[VT]: ...
    def get(self, key: KT, default: DT = None) -> typing.Union[VT, DT]: ...
    def pop(self, key: KT, default: DT = None) -> typing.Union[VT, DT]: ...
    def setdefault(self, key: KT, default: typing.Optional[VT] = None) -> typing.Optional[VT]: ...
    def popitem(self) -> typing.Tuple[KT, VT]: ...
    def drain(self, n: int) -> int: ...
    def clear(self, *, reuse: bool = False) -> None: ...
    def shrink_to_fit(self) -> None: ...
    def update(
        self, iterable: typing.Union[typing.Iterable[KT, VT], typing.Dict[KT, VT]]
    ) -> None: ...
    def keys(self) -> typing.Iterable[KT]: ...
    def values(self) -> typing.Iterable[VT]: ...
    def items(self) -> typing.Iterable[typing.Tuple[KT, VT]]: ...

class Cache(BaseCacheImpl[KT, VT]):
    """
    A simple cache that has no algorithm; this is only a hashmap.

    `Cache` vs `dict`:
    - it is thread-safe and unordered, while `dict` isn't thread-safe and ordered (Python 3.6+).
    - it uses very lower memory than `dict`.
    - it supports useful and new methods for managing memory, while `dict` does not.
    - it does not support `popitem`, while `dict` does.
    - You can limit the size of `Cache`, but you cannot for `dict`.
    """

    def __new__(
        cls,
        maxsize: int,
        iterable: typing.Union[typing.Iterable[typing.Tuple[KT, VT]], typing.Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ):
        """
        A simple cache that has no algorithm; this is only a hashmap.

        By `maxsize` param, you can specify the limit size of the cache ( zero means infinity ); this is unchangable.

        By `iterable` param, you can create cache from a dict or an iterable.

        If `capacity` param is given, cache attempts to allocate a new hash table with at
        least enough capacity for inserting the given number of elements without reallocating.
        """
        ...

    def __setitem__(self, key: KT, value: VT) -> None:
        """
        Set self[key] to value.

        Note: raises `OverflowError` if the cache reached the maxsize limit,
        because this class does not have any algorithm.
        """
        ...

    def __getitem__(self, key: KT) -> VT:
        """
        Returns self[key].

        Note: raises `KeyError` if key not found.
        """
        ...

    def __delitem__(self, key: KT) -> VT:
        """
        Deletes self[key].

        Note: raises `KeyError` if key not found.
        """
        ...

    def capacity(self) -> int:
        """
        Returns the number of elements the map can hold without reallocating.
        """
        ...

    def is_full(self) -> bool:
        """
        Equivalent directly to `len(self) == self.maxsize`
        """
        ...

    def is_empty(self) -> bool:
        """
        Equivalent directly to `len(self) == 0`
        """
        ...

    def insert(self, key: KT, value: VT) -> typing.Optional[VT]:
        """
        Equals to `self[key] = value`, but returns a value:

        - If the cache did not have this key present, None is returned.
        - If the cache did have this key present, the value is updated,
          and the old value is returned. The key is not updated, though;

        Note: raises `OverflowError` if the cache reached the maxsize limit,
        because this class does not have any algorithm.
        """
        ...

    def get(self, key: KT, default: DT = None) -> typing.Union[VT, DT]:
        """
        Equals to `self[key]`, but returns `default` if the cache don't have this key present.
        """
        ...

    def pop(self, key: KT, default: DT = None) -> typing.Union[VT, DT]:
        """
        Removes specified key and return the corresponding value.

        If the key is not found, returns the `default`.
        """
        ...

    def setdefault(self, key: KT, default: typing.Optional[VT] = None) -> typing.Optional[VT]:
        """
        Inserts key with a value of default if key is not in the cache.

        Return the value for key if key is in the cache, else default.
        """
        ...

    def popitem(self) -> typing.NoReturn: ...  # not implemented for this class
    def drain(self, n: int) -> typing.NoReturn: ...  # not implemented for this class
    def clear(self, *, reuse: bool = False) -> None:
        """
        Removes all items from cache.

        If reuse is True, will not free the memory for reusing in the future.
        """
        ...

    def shrink_to_fit(self) -> None:
        """
        Shrinks the cache to fit len(self) elements.
        """
        ...

    def update(self, iterable: typing.Iterable[KT] | typing.Dict[KT, VT]) -> None:
        """
        Updates the cache with elements from a dictionary or an iterable object of key/value pairs.

        Note: raises `OverflowError` if the cache reached the maxsize limit.
        """
        ...

    def keys(self) -> typing.Iterable[KT]:
        """
        Returns an iterable object of the cache's keys.

        Notes:
        - You should not make any changes in cache while using this iterable object.
        - Keys are not ordered.
        """
        ...

    def values(self) -> typing.Iterable[VT]:
        """
        Returns an iterable object of the cache's values.

        Notes:
        - You should not make any changes in cache while using this iterable object.
        - Values are not ordered.
        """
        ...

    def items(self) -> typing.Iterable[typing.Tuple[KT, VT]]:
        """
        Returns an iterable object of the cache's items (key-value pairs).

        Notes:
        - You should not make any changes in cache while using this iterable object.
        - Items are not ordered.
        """
        ...

class FIFOCache(BaseCacheImpl[KT, VT]):
    """
    FIFO Cache implementation - First-In First-Out Policy (thread-safe).

    In simple terms, the FIFO cache will remove the element that has been in the cache the longest
    """
    def __new__(
        cls,
        maxsize: int,
        iterable: typing.Union[typing.Iterable[typing.Tuple[KT, VT]], typing.Dict[KT, VT]] = ...,
        *,
        capacity: int = ...,
    ):
        """
        FIFO Cache implementation - First-In First-Out Policy (thread-safe).

        By `maxsize` param, you can specify the limit size of the cache ( zero means infinity ); this is unchangable.

        By `iterable` param, you can create cache from a dict or an iterable.

        If `capacity` param is given, cache attempts to allocate a new hash table with at
        least enough capacity for inserting the given number of elements without reallocating.
        """
        ...

    def __setitem__(self, key: KT, value: VT) -> None:
        """
        Set self[key] to value.
        """
        ...

    def __getitem__(self, key: KT) -> VT:
        """
        Returns self[key].

        Note: raises `KeyError` if key not found.
        """
        ...

    def __delitem__(self, key: KT) -> VT:
        """
        Deletes self[key].

        Note: raises `KeyError` if key not found.
        """
        ...

    def capacity(self) -> int:
        """
        Returns the number of elements the map can hold without reallocating.
        """
        ...

    def is_full(self) -> bool:
        """
        Equivalent directly to `len(self) == self.maxsize`
        """
        ...

    def is_empty(self) -> bool:
        """
        Equivalent directly to `len(self) == 0`
        """
        ...

    def insert(self, key: KT, value: VT) -> typing.Optional[VT]:
        """
        Equals to `self[key] = value`, but returns a value:

        - If the cache did not have this key present, None is returned.
        - If the cache did have this key present, the value is updated,
          and the old value is returned. The key is not updated, though;
        """
        ...

    def get(self, key: KT, default: DT = None) -> typing.Union[VT, DT]:
        """
        Equals to `self[key]`, but returns `default` if the cache don't have this key present.
        """
        ...

    def pop(self, key: KT, default: DT = None) -> typing.Union[VT, DT]:
        """
        Removes specified key and return the corresponding value.

        If the key is not found, returns the `default`.
        """
        ...

    def setdefault(self, key: KT, default: typing.Optional[VT] = None) -> typing.Optional[VT]:
        """
        Inserts key with a value of default if key is not in the cache.

        Return the value for key if key is in the cache, else default.
        """
        ...

    def popitem(self) -> typing.Tuple[KT, VT]:
        """
        Removes the element that has been in the cache the longest
        """
        ...

    def drain(self, n: int) -> int:
        """
        Does the `popitem()` `n` times and returns count of removed items.
        """
        ...

    def clear(self, *, reuse: bool = False) -> None:
        """
        Removes all items from cache.

        If reuse is True, will not free the memory for reusing in the future.
        """
        ...

    def update(self, iterable: typing.Iterable[KT] | typing.Dict[KT, VT]) -> None:
        """
        Updates the cache with elements from a dictionary or an iterable object of key/value pairs.
        """
        ...

    def first(self, n: int = 0) -> typing.Optional[KT]:
        """
        Returns the first key in cache; this is the one which will be removed by `popitem()`.
        """
        ...

    def last(self) -> typing.Optional[KT]:
        """
        Returns the last key in cache.
        """
        ...

class RRCache(BaseCacheImpl[KT, VT]):
    pass
