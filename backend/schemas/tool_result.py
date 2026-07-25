from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class DocumentResult(BaseModel):
    documents: list[dict[str, Any]] = Field(default_factory=list)
    chunks: list[dict[str, Any]] = Field(default_factory=list)
    metadata_summary: dict[str, Any] = Field(default_factory=dict)


class PropertyResult(BaseModel):
    property_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    owner_id: str | None = None
    tax_status: str | None = None
    mutation_status: str | None = None


class AlertResult(BaseModel):
    alerts: list[dict[str, Any]] = Field(default_factory=list)
    severity_summary: dict[str, int] = Field(default_factory=dict)


class HealthResult(BaseModel):
    property_id: str
    health_score: int
    risk_indicators: list[str] = Field(default_factory=list)
    health_factors: dict[str, Any] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)


class OCRResult(BaseModel):
    document_id: str
    extracted_text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class TimelineResult(BaseModel):
    property_id: str
    events: list[dict[str, Any]] = Field(default_factory=list)


class ReportResult(BaseModel):
    property_summary: dict[str, Any] = Field(default_factory=dict)
    evidence_bundle: list[dict[str, Any]] = Field(default_factory=list)
    timeline_summary: list[dict[str, Any]] = Field(default_factory=list)


class LegalResult(BaseModel):
    procedures: list[dict[str, Any]] = Field(default_factory=list)
    rules: list[dict[str, Any]] = Field(default_factory=list)
