#!/usr/bin/env python3
"""
Base class entity for CraftLore Account TP.
"""

from pydantic import BaseModel, Field, ConfigDict
from ..enums import AuthenticationStatus
from abc import ABC
import cbor2

class BaseClass(BaseModel, ABC):
    """Base class model for CraftLore Account TP."""
    tp_version: str = "1.0"
    model_config = ConfigDict(use_enum_values=True)
    certifications: list = Field(default_factory=list)
    authentication_status: AuthenticationStatus = AuthenticationStatus.PENDING
    created_timestamp: str = Field(default_factory=str)
    is_deleted: bool = False
    history: list = Field(default_factory=list)

    def to_cbor(self) -> bytes: # TODO: Implement in code
        return cbor2.dumps(self.model_dump())
    @classmethod
    def from_cbor(cls, data: bytes) -> "BaseClass":
        return cls.model_validate(cbor2.loads(data))