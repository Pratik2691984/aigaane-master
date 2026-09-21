"""Read-only derivation mocks. Never write disk. Kernels not mounted."""
from fastapi import APIRouter, Request

router = APIRouter()

FLAGS = {
    "status": "mock_fallback",
    "canonicalWrite": False,
    "promotionAllowed": False,
    "importAllowed": False,
    "previewOnly": True,
    "readOnly": True,
    "httpHint": 501,
}


def envelope(engine, record=None, extra=None):
    body = dict(FLAGS)
    body["engine"] = engine
    body["kernelMounted"] = False
    body["record"] = record
    if extra:
        body.update(extra)
    return body


def _payload(request: Request):
    q = dict(request.query_params)
    return q