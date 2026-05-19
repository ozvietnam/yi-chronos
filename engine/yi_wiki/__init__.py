"""YI-Wiki — Master-Apprentice Digital Twin of Thiệu Khang Tiết.

Design source of truth: docs/design/wiki-master-apprentice.md
Schema reference: §5 (Layer 3: PASSAGE + METHOD + CASE STUDY)

Modules:
- models      dataclasses (Author, Passage, Method, CaseStudy, Prediction, ConceptIndex)
- store       SQLite CRUD
- seed_master seed Thiệu Khang Tiết + Tier-1 consultant Lý Chi Tài
"""
from engine.yi_wiki.models import (
    Author,
    Passage,
    Method,
    CaseStudy,
    Prediction,
    ConceptIndex,
)
from engine.yi_wiki.store import WikiStore, get_store

__all__ = [
    "Author",
    "Passage",
    "Method",
    "CaseStudy",
    "Prediction",
    "ConceptIndex",
    "WikiStore",
    "get_store",
]
