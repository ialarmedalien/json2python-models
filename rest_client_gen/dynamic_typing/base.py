from typing import Any, Union, Iterable, List


class BaseType:
    def __iter__(self) -> Iterable['MetaData']:
        raise NotImplementedError()

    def replace(self, t: Union['MetaData', List['MetaData']], **kwargs) -> 'BaseType':
        """
        Replace nested type in-place

        :param t: Meta type
        :param kwargs: Other args
        :return:
        """
        raise NotImplementedError()

    def to_static_type(self) -> type:
        raise NotImplementedError()


class UnknownType(BaseType):
    __slots__ = []

    def __str__(self):
        return "Unknown"

    def __iter__(self) -> Iterable['MetaData']:
        return ()

    def replace(self, t: 'MetaData', **kwargs) -> 'UnknownType':
        return self

    def to_static_type(self):
        return Any


Unknown = UnknownType()
NoneType = type(None)
MetaData = Union[type, dict, BaseType]


class SingleType(BaseType):
    __slots__ = ["type"]

    def __init__(self, t: MetaData):
        self.type = t

    def __str__(self):
        return f"{self.__class__.__name__}[{self.type}]"

    def __repr__(self):
        return f"<{self.__class__.__name__} [{self.type}]>"

    def __iter__(self) -> Iterable['MetaData']:
        yield self.type

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.type == other.type

    def replace(self, t: 'MetaData', **kwargs) -> 'SingleType':
        self.type = t
        return self


class ComplexType(BaseType):
    __slots__ = ["types"]

    def __init__(self, *types: MetaData):
        self.types = list(types)

    def __str__(self):
        items = ', '.join(map(str, self.types))
        return f"{self.__class__.__name__}[{items}]"

    def __repr__(self):
        items = ', '.join(map(str, self.types))
        return f"<{self.__class__.__name__} [{items}]>"

    def __iter__(self) -> Iterable['MetaData']:
        yield from self.types

    def _sort_key(self, item):
        if isinstance(item, dict):
            return f"Dict#{sorted(item.keys())}"
        else:
            return str(item)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and all(t1 == t2 for t1, t2 in zip(
            sorted(self.types, key=self._sort_key), sorted(other.types, key=self._sort_key)
        ))

    def __len__(self):
        return len(self.types)

    def replace(self, t: Union['MetaData', List['MetaData']], index=None, **kwargs) -> 'ComplexType':
        if index is None and isinstance(t, list):
            self.types = t
        elif index is not None and not isinstance(t, list):
            self.types[index] = t
        else:
            raise ValueError(f"Unsupported arguments: t={t} index={index} kwargs={kwargs}")
        return self
