from ._cachebox import BaseCacheImpl, FIFOCache
from collections import namedtuple
import inspect
import typing


KT = typing.TypeVar("KT")
VT = typing.TypeVar("VT")
DT = typing.TypeVar("DT")


class Frozen(BaseCacheImpl, typing.Generic[KT, VT]):
    __slots__ = "__cache"

    def __init__(self, cls: BaseCacheImpl[KT, VT]) -> None:
        assert isinstance(cls, BaseCacheImpl)
        assert type(cls) is not Frozen

        self.__cache = cls

    @property
    def cache(self) -> BaseCacheImpl[KT, VT]:
        return self.__cache

    @property
    def maxsize(self) -> int:
        return self.__cache.maxsize

    def __len__(self) -> int:
        return len(self.__cache)

    def __sizeof__(self) -> int:
        return self.__cache.__sizeof__()

    def __bool__(self) -> bool:
        return bool(self.__cache)

    def __contains__(self, key: KT) -> bool:
        return key in self.__cache

    def __setitem__(self, key: KT, value: VT) -> None:
        raise TypeError("This cache is frozen.")

    def __getitem__(self, key: KT) -> VT:
        return self.__cache[key]

    def __delitem__(self, key: KT) -> VT:
        raise TypeError("This cache is frozen.")

    def __str__(self) -> str:
        return f"<Frozen: {self.__cache}>"

    def __iter__(self) -> typing.Iterator[KT]:
        return iter(self.__cache)

    def __richcmp__(self, other: typing.Self, op: int) -> bool:
        return self.__cache.__richcmp__(other, op)

    def capacity(self) -> int:
        return self.__cache.capacity()

    def is_full(self) -> bool:
        return self.__cache.is_full()

    def is_empty(self) -> bool:
        return self.__cache.is_empty()

    def insert(self, key: KT, value: VT, *args, **kwargs) -> typing.Optional[VT]:
        raise TypeError("This cache is frozen.")

    def get(self, key: KT, default: DT = None) -> typing.Union[VT, DT]:
        return self.__cache.get(key, default)

    def pop(self, key: KT, default: DT = None) -> typing.Union[VT, DT]:
        raise TypeError("This cache is frozen.")

    def setdefault(
        self, key: KT, default: typing.Optional[VT] = None, *args, **kwargs
    ) -> typing.Optional[typing.Union[VT, DT]]:
        raise TypeError("This cache is frozen.")

    def popitem(self) -> typing.Tuple[KT, VT]:
        raise TypeError("This cache is frozen.")

    def drain(self, n: int) -> int:
        raise TypeError("This cache is frozen.")

    def clear(self, *, reuse: bool = False) -> None:
        raise TypeError("This cache is frozen.")

    def shrink_to_fit(self) -> None:
        raise TypeError("This cache is frozen.")

    def update(
        self, iterable: typing.Union[typing.Iterable[typing.Tuple[KT, VT]], typing.Dict[KT, VT]]
    ) -> None:
        raise TypeError("This cache is frozen.")

    def keys(self) -> typing.Iterable[KT]:
        return self.__cache.keys()

    def values(self) -> typing.Iterable[VT]:
        return self.__cache.values()

    def items(self) -> typing.Iterable[typing.Tuple[KT, VT]]:
        return self.__cache.items()


def make_key(args: tuple, kwds: dict, fasttype=(int, str)):
    key = args
    if kwds:
        key += (object,)
        for item in kwds.items():
            key += item

    if fasttype and len(key) == 1 and type(key[0]) in fasttype:
        return key[0]

    return key


def make_hash_key(args: tuple, kwds: dict):
    return hash(make_key(args, kwds))


def make_typed_key(args: tuple, kwds: dict):
    key = make_key(args, kwds, fasttype=())

    key += tuple(type(v) for v in args)
    if kwds:
        key += tuple(type(v) for v in kwds.values())

    return key


_CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize", "length", "cachememory"])


class _cached_wrapper(typing.Generic[VT]):
    def __init__(
        self,
        cache: BaseCacheImpl[typing.Any, VT],
        func: typing.Callable[..., VT],
        key_maker: typing.Callable[[tuple, dict], typing.Hashable],
        clear_reuse: bool,
        is_method: bool,
    ) -> None:
        self.cache = cache
        self.func = func
        self._key_maker = (
            (lambda args, kwds: key_maker(args[1:], kwds)) if is_method else (key_maker)
        )
        self.__reuse = clear_reuse
        self._hits = 0
        self._misses = 0

    def cache_info(self) -> _CacheInfo:
        return _CacheInfo(
            self._hits, self._misses, self.cache.maxsize, len(self.cache), self.cache.__sizeof__()
        )

    def cache_clear(self) -> None:
        self.cache.clear(reuse=self.__reuse)
        self._hits = 0
        self._misses = 0

    def __str__(self) -> str:
        return str(self.func)

    def __call__(self, *args, **kwds) -> VT:
        key = self._key_maker(args, kwds)
        try:
            result = self.cache[key]
            self._hits += 1
            return result
        except KeyError:
            self._misses += 1

        result = self.func(*args, **kwds)
        self.cache[key] = result
        return result


class _async_cached_wrapper(_cached_wrapper[VT]):
    async def __call__(self, *args, **kwds) -> VT:
        key = self._key_maker(args, kwds)
        try:
            result = self.cache[key]
            self._hits += 1
            return result
        except KeyError:
            self._misses += 1

        result = await self.func(*args, **kwds)
        self.cache[key] = result
        return result


def cached(
    cache: BaseCacheImpl[typing.Any, VT],
    key_maker: typing.Callable[[tuple, dict], typing.Hashable] = make_key,
    clear_reuse: bool = False,
    **kwargs,
) -> typing.Callable[[typing.Callable[..., VT]], _cached_wrapper[VT]]:
    """
    Memoize your functions (async functions are supported) ...

    By `cache` param, set your cache and cache policy. (If is `None` or `dict`, `FIFOCache` will be used)

    By `key_maker` param, you can set your key maker, see examples below.

    The `clear_reuse` param will be passed to cache's `clear` method.

    Simple Example::

        @cachebox.cached(cachebox.LRUCache(128))
        def sum_as_string(a, b):
            return str(a+b)

        assert sum_as_string(1, 2) == "3"

        assert len(sum_as_string.cache) == 1
        sum_as_string.cache_clear()
        assert len(sum_as_string.cache) == 0

    Key Maker Example::

        def simple_key_maker(args: tuple, kwds: dict):
            return args[0].path

        @cachebox.cached(cachebox.LRUCache(128), key_maker=simple_key_maker)
        def request_handler(request: Request):
            return Response("hello man")

    Typed Example::

        @cachebox.cached(cachebox.LRUCache(128), key_maker=cachebox.make_typed_key)
        def sum_as_string(a, b):
            return str(a+b)
    """
    if isinstance(cache, dict) or cache is None:
        cache = FIFOCache(0)

    if type(cache) is type or not isinstance(cache, BaseCacheImpl):
        raise TypeError("we expected cachebox caches, got %r" % (cache,))

    if "info" in kwargs:
        import warnings

        warnings.warn(
            "'info' parameter is deprecated and no longer available",
            DeprecationWarning,
        )

    def decorator(func: typing.Callable[..., VT]) -> _cached_wrapper[VT]:
        if inspect.iscoroutinefunction(func):
            return _async_cached_wrapper(
                cache,
                func,
                key_maker=key_maker,
                clear_reuse=clear_reuse,
                is_method=kwargs.get("is_method", False),
            )

        return _cached_wrapper(
            cache,
            func,
            key_maker=key_maker,
            clear_reuse=clear_reuse,
            is_method=kwargs.get("is_method", False),
        )

    return decorator


def cachedmethod(
    cache: BaseCacheImpl[typing.Any, VT],
    key_maker: typing.Callable[[tuple, dict], typing.Hashable] = make_key,
    clear_reuse: bool = False,
    **kwargs,
):
    """
    It works like `cached()`, but you can use it for class methods, because it will ignore `self` param.
    """
    kwargs["is_method"] = True
    return cached(cache, key_maker, clear_reuse, **kwargs)


_K = typing.TypeVar("_K")
_V = typing.TypeVar("_V")


def items_in_order(cache: BaseCacheImpl[_K, _V]):
    import warnings

    warnings.warn(
        "'items_in_order' function is deprecated and no longer is available, because all '.items()' methods are ordered now.",
        DeprecationWarning,
    )

    return cache.items()
