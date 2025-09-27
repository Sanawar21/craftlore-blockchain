#!/usr/bin/env python3
"""Packaging is created when a batch of products has been completed (by work order or directly).
To get the products ready for shipment, they are packaged into a packaging asset. This may include products from other batches"""



from pydantic import Field
from typing import Optional, Dict, Any

from . import BaseAsset
from models.enums import AssetType

# --- Certification ---
class Certification(BaseAsset):
    """Generic certificate schema that can represent GI and other certificates."""
    asset_type: AssetType = Field(default=AssetType.CERTIFICATION)
    title: str = Field(..., description="Title or type of certificate (e.g., GI Certificate, ISO 9001)")
    issue_timestamp: str = Field(..., description="Date when the certificate was issued")
    expiry_timestamp: Optional[str] = Field(None, description="Optional expiry/validity date")
    issuer: str = Field(..., description="Public key of the issuing authority")
    holder: str = Field(..., description="Public key or uid of the entity or person to whom the certificate is issued")
    description: Optional[str] = Field(None, description="Summary or details of the certificate")
    
    # For domain-specific fields like GI, academic, ISO, etc.
    fields: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible key-value fields for specialized certificate details"
    )
    
    @property
    def forbidden_fields(self) :
        """Fields that should not be set during creation."""
        return super().forbidden_fields
    
    @property
    def editable_fields(self) -> set:
        """Fields that can be edited after creation."""
        return super().editable_fields