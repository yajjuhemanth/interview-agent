"""Minimal smoke tests to validate key API routes.

Covers:
- POST /generate (dev stub)
- POST /save
- GET  /get
- POST /agent (201 with AI configured, else 503)
"""

import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE = os.environ.get("BASE_URL", "http://localhost:5000")

def post(path: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = Request(f"{BASE}{path}", data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req) as resp:
            return resp.getcode(), json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if hasattr(e, 'read') else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {"raw": body}
        return e.code, payload

def get(path: str):
    req = Request(f"{BASE}{path}")
    with urlopen(req) as resp:
        return resp.getcode(), json.loads(resp.read().decode("utf-8"))


def main() -> int:
    print("1) /generate ...", end=" ")
    code, gen = post("/generate", {
        "job_title": "Backend Engineer",
        "job_description": "APIs, Python, Flask, MySQL"
    })
    print(code)
    assert code == 200 and isinstance(gen.get("questions"), list)

    print("2) /save ...", end=" ")
    code, saved = post("/save", {
        "job_title": gen["job_title"],
        "job_description": gen["job_description"],
        "questions": gen["questions"][:3] or ["Q1", "Q2", "Q3"],
    })
    print(code)
    assert code == 201 and "id" in saved

    print("3) /get ...", end=" ")
    code, rows = get("/get")
    print(code)
    assert code == 200 and isinstance(rows, list) and any(r.get("id") == saved["id"] for r in rows)

    print("4) /agent ...", end=" ")
    code, agent_resp = post("/agent", {
        "job_title": "Frontend Developer",
        "job_description": "ReactJS, JS, testing"
    })
    print(code)
    # Accept 201 (AI configured) or 503 (AI unavailable but handled)
    assert code in (201, 503)
    if code == 201:
        assert isinstance(agent_resp, dict) and "id" in agent_resp and isinstance(agent_resp.get("questions"), list)

    print("SMOKE TEST PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
