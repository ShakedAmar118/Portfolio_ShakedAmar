from typing import Any


class TreeNode:
    def __init__(self, data: Any, left: Any = None, right: Any = None) -> None:
        self.__data: Any = data
        self.__left: Any = left
        self.__right: Any = right

    @property
    def left(self) -> Any:
        return self.__left

    @left.setter
    def left(self, new_left: Any) -> None:
        self.__left = new_left

    @property
    def right(self) -> Any:
        return self.__right

    @right.setter
    def right(self, new_right: Any) -> None:
        self.__right = new_right

    @property
    def data(self) -> Any:
        return self.__data

    @data.setter
    def data(self, new_data: Any) -> None:
        self.__data = new_data

    def tree_str(self, tree: bytes = b'') -> bytes:
        if self.left is None and self.right is None:
            if isinstance(self.data, tuple):
                tree += self.data[0] + b'l,'
            else:
                tree += self.data + b'l,'
            return tree
        tree += (str(self.data) + ',').encode()
        tree = self.__left.tree_str(tree)
        tree = self.__right.tree_str(tree)
        return tree
