"""Single seam for Kubernetes cluster access.

All ConfigMap/Secret I/O and client construction live here so the
incluster→kubeconfig fallback and ConfigMap-``data`` parsing exist in exactly
one place. Callers cross one interface; tests mount fakes by patching ``core`` /
``batch`` (or the read/patch helpers).

Non-deterministic (imports ``kubernetes``): never import this from a Temporal
workflow module — only from activity code.
"""

from __future__ import annotations

import base64
import os

NAMESPACE = os.getenv("AGENTS_NAMESPACE", "agents")


# --------------------------------------------------------------------------- #
# Client accessors (the patchable seam for tests)
# --------------------------------------------------------------------------- #
def _load_config() -> None:
    from kubernetes import config

    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()


def core():
    from kubernetes import client

    _load_config()
    return client.CoreV1Api()


def batch():
    from kubernetes import client

    _load_config()
    return client.BatchV1Api()


# --------------------------------------------------------------------------- #
# ConfigMap / Secret helpers (hide data parsing + 404 + base64)
# --------------------------------------------------------------------------- #
def _data(obj) -> dict:
    """Pull the ``data`` mapping off a ConfigMap/Secret, tolerating both the
    kubernetes client object (``obj.data``) and a plain dict (as fakes pass)."""
    if isinstance(obj, dict):
        return obj.get("data") or {}
    return obj.data or {}


def read_configmap_data(name: str, namespace: str = NAMESPACE) -> dict | None:
    """Return a ConfigMap's ``data`` mapping, or ``None`` if it doesn't exist."""
    from kubernetes.client.exceptions import ApiException

    try:
        cm = core().read_namespaced_config_map(name, namespace)
    except ApiException as exc:  # 404 = the ConfigMap hasn't been written yet
        if getattr(exc, "status", None) == 404:
            return None
        raise
    return _data(cm)


def patch_configmap_data(name: str, data: dict, namespace: str = NAMESPACE) -> None:
    """Patch ``data`` keys onto an existing ConfigMap."""
    core().patch_namespaced_config_map(name, namespace, {"data": data})


def read_secret_value(name: str, key: str, namespace: str = NAMESPACE) -> str:
    """Read and base64-decode a single key from a Secret; ``""`` if absent."""
    sec = core().read_namespaced_secret(name, namespace)
    raw = _data(sec).get(key, "")
    return base64.b64decode(raw).decode() if raw else ""
