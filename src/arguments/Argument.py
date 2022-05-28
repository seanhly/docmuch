from abc import ABC, abstractmethod
from typing import List


class Argument(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def parse_argument_for_action(
        self,
        arguments: List["Argument"],
        current_index: int,
        action
    ) -> int:
        return current_index + 1