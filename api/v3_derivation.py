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


@router.api_route("/api/v3/sandhi", methods=["GET", "POST"])
async def sandhi(request: Request):
    return envelope("sandhi", extra={"query": _payload(request), "note": "Sandhi kernel not mounted"})


@router.api_route("/api/v3/morphology/verb/conjugate", methods=["GET", "POST"])
async def verb_conjugate(request: Request):
    return envelope("verb_conjugate", extra={"query": _payload(request), "note": "Verb kernel not mounted"})


@router.api_route("/api/v3/morphology/noun/inflect", methods=["GET", "POST"])
async def noun_inflect(request: Request):
    return envelope("noun_inflect", extra={"query": _payload(request), "note": "Noun kernel not mounted"})


@router.api_route("/api/v3/prakriya", methods=["GET", "POST"])
async def prakriya(request: Request):
    return envelope("prakriya", extra={"query": _payload(request), "note": "Prakriya kernel not mounted"})


@router.api_route("/api/v3/chandas", methods=["GET", "POST"])
async def chandas(request: Request):
    return envelope("chandas", extra={"query": _payload(request), "note": "Chandas kernel not mounted"})
