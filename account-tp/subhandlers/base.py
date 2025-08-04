from abc import ABC, abstractmethod
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction

class BaseSubHandler(ABC):
    """Abstract base class for subhandlers in the account transaction processor."""

    def __init__(self, get_address: callable):
        self.get_address = get_address

    @abstractmethod
    def apply(self, transaction, context: Context, payload: dict):
        pass