"""
gemini_llm.py - the "G" (Generation) part of RAG, using the FREE Google Gemini API.

Works locally and on Streamlit Community Cloud. Uses only the `requests` library.

The API key is NEVER written in code. Provide it as:
  * Streamlit Cloud:  App -> Settings -> Secrets ->  GEMINI_API_KEY = "your-key"
  * Local PC:         $env:GEMINI_API_KEY="your-key"   (or .streamlit/secrets.toml)
Get a free key at https://aistudio.google.com/apikey
"""

from __future__ import annotations

import json
import os
from typing import Iterator

import requests

DEFAULT_MODEL = "gemini-3.5-flash-lite"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


class GeminiError(Exception):
    """Beginner-friendly error message."""


def _key(api_key: str | None = None) -> str:
    return (api_key if api_key is not None else os.getenv("GEMINI_API_KEY", "")).strip()


def has_key(api_key: str | None = None) -> bool:
    k = _key(api_key)
    return bool(k) and not k.startswith("PASTE")


def list_models(api_key: str | None = None, timeout: int = 10) -> list[str]:
    """Every model name this key can send text to (used by the sidebar model picker)."""
    api_key = _key(api_key)
    if not has_key(api_key):
        return []
    try:
        r = requests.get(f"{BASE_URL}/models?pageSize=200", headers={"x-goog-api-key": api_key}, timeout=timeout)
        if not r.ok:
            return []
        data = r.json()
    except (requests.exceptions.RequestException, ValueError):
        return []
    names = []
    for m in data.get("models", []):
        if "generateContent" in m.get("supportedGenerationMethods", []):
            names.append(str(m.get("name", "")).replace("models/", "", 1))
    return [n for n in names if n]


def get_status(model: str | None = None, api_key: str | None = None) -> dict:
    model = (model or os.getenv("GEMINI_MODEL") or GEMINI_MODEL).strip()
    api_key = _key(api_key)
    if not has_key(api_key):
        return {"running": False, "model_ready": False, "model": model, "detail": "No GEMINI_API_KEY set"}
    try:
        r = requests.get(f"{BASE_URL}/models/{model}", headers={"x-goog-api-key": api_key}, timeout=8)
    except requests.exceptions.RequestException:
        return {"running": False, "model_ready": False, "model": model, "detail": "Cannot reach Google"}
    if r.status_code in (401, 403):
        return {"running": True, "model_ready": False, "model": model, "detail": "API key rejected"}
    if r.status_code == 400:
        return {"running": True, "model_ready": False, "model": model, "detail": "Invalid API key or model request"}
    if r.status_code == 404:
        return {"running": True, "model_ready": False, "model": model, "detail": "Model not found"}
    if r.status_code == 429:
        return {
            "running": True,
            "model_ready": False,
            "model": model,
            "detail": "Free quota used up for this model - pick another model",
        }
    if r.status_code == 503:
        return {"running": True, "model_ready": False, "model": model, "detail": "Model is busy right now - try again or pick another model"}
    return {"running": True, "model_ready": r.ok, "model": model, "detail": "" if r.ok else f"HTTP {r.status_code}"}


def stream_answer(
    prompt: str,
    system: str,
    history: list[dict] | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> Iterator[str]:
    model = (model or os.getenv("GEMINI_MODEL") or GEMINI_MODEL).strip()
    api_key = _key(api_key)
    if not has_key(api_key):
        raise GeminiError("GEMINI_API_KEY is not set. Add it in Streamlit Secrets (see README).")

    contents = []
    for m in (history or [])[-4:]:
        contents.append({"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]})
    contents.append({"role": "user", "parts": [{"text": prompt}]})

    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 800},
    }
    url = f"{BASE_URL}/models/{model}:streamGenerateContent?alt=sse"
    try:
        with requests.post(url, json=payload, headers={"x-goog-api-key": api_key}, stream=True, timeout=(5, 60)) as resp:
            if resp.status_code in (400, 401, 403):
                raise GeminiError("Gemini rejected the API key. Check GEMINI_API_KEY in your secrets.")
            if resp.status_code == 429:
                if "per day" in resp.text.lower():
                    raise GeminiError(
                        f"The free daily limit for '{model}' is used up (free tier allows only ~20 questions "
                        "per model per day). Each model has its own quota, so pick another model in the sidebar."
                    )
                raise GeminiError("Free Gemini limit reached for now. Wait a minute and try again.")
            if resp.status_code == 404:
                raise GeminiError(
                    f"Gemini model '{model}' is not available to this key. Pick another model in the sidebar."
                )
            if resp.status_code == 503:
                raise GeminiError(f"Gemini model '{model}' is busy right now. Pick another model in the sidebar or retry.")
            resp.raise_for_status()
            for raw in resp.iter_lines():
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8", errors="ignore")
                if not raw or not raw.startswith("data:"):
                    continue
                data = json.loads(raw[5:].strip())
                for cand in data.get("candidates", []):
                    for part in cand.get("content", {}).get("parts", []):
                        if part.get("text"):
                            yield part["text"]
    except requests.exceptions.Timeout:
        raise GeminiError("Gemini took too long to respond. Please try again.")
    except requests.exceptions.RequestException as exc:
        raise GeminiError(f"Could not reach Gemini: {exc}")
