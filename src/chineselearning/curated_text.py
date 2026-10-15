"""Validate curated texts independently of HSK extraction and preserve supplied IDs."""

import json
from pathlib import Path

FORMAT = "chineselearning-curated-texts"
VERSION = 2
OPTIONAL_FIELDS = ("author", "period", "notes")


def validate_fields(record, required, optional, context):
    if (not isinstance(record, dict) or not set(required) <= record.keys()
            or record.keys() - set(required) - set(optional)):
        raise ValueError(f"Invalid {context} fields")


def validate_id(value, context):
    if type(value) is not int or not 1 <= value <= 2**63 - 1:
        raise ValueError(f"{context} must be a positive 64-bit integer")


def validate_required_text(value, context):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context} must be nonblank text")


def validate_document(spec):
    validate_fields(spec, ("format", "version", "categories", "texts"), (), "document")
    if (spec["format"] != FORMAT or type(spec["version"]) is not int
            or spec["version"] != VERSION):
        raise ValueError("Unsupported curated-text format/version")
    if not isinstance(spec["categories"], list) or not isinstance(spec["texts"], list):
        raise ValueError("Categories and texts must be lists")
    category_ids = set()
    for category in spec["categories"]:
        validate_fields(category, ("id", "label"), (), "category")
        validate_id(category["id"], "Category ID")
        if category["id"] in category_ids:
            raise ValueError(f"Duplicate category ID: {category['id']}")
        category_ids.add(category["id"])
        validate_required_text(category["label"], "Category label")
    text_ids = set()
    for text in spec["texts"]:
        validate_fields(text, ("id", "category_ids", "title", "body"), OPTIONAL_FIELDS, "text")
        validate_id(text["id"], "Text ID")
        if text["id"] in text_ids:
            raise ValueError(f"Duplicate text ID: {text['id']}")
        text_ids.add(text["id"])
        assignments = text["category_ids"]
        if not isinstance(assignments, list) or not assignments:
            raise ValueError("category_ids must be a nonempty list")
        assigned_ids = set()
        for category_id in assignments:
            validate_id(category_id, "Category reference")
            if category_id in assigned_ids:
                raise ValueError(f"Duplicate category assignment: {category_id}")
            if category_id not in category_ids:
                raise ValueError(f"Missing category reference: {category_id}")
            assigned_ids.add(category_id)
        for field in ("title", "body"):
            validate_required_text(text[field], field)
        for field in OPTIONAL_FIELDS:
            if text.get(field) is not None and not isinstance(text[field], str):
                raise ValueError(f"{field} must be text or null")
    return spec


def read_rows(path):
    """Copy validated values without trimming, renumbering, or inventing metadata."""
    spec = validate_document(json.loads(Path(path).read_text(encoding="utf-8")))
    return {
        "text_category": sorted(spec["categories"], key=lambda record: record["id"]),
        "library_text": sorted(
            [dict({key: value for key, value in text.items() if key != "category_ids"},
                  **{field: text.get(field) for field in OPTIONAL_FIELDS})
             for text in spec["texts"]],
            key=lambda record: record["id"],
        ),
        "text_category_assignment": [
            dict(text_id=text["id"], category_id=category_id)
            for text in sorted(spec["texts"], key=lambda record: record["id"])
            for category_id in sorted(text["category_ids"])
        ],
    }
