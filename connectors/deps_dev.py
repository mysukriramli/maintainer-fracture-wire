import logging
import urllib.parse
from typing import Dict
import requests

DEPS_DEV_BASE = "https://api.deps.dev/v3/systems"
_DEPS_CACHE: Dict[str, int] = {}

ECOSYSTEM_MAP = {
    "npm": "npm",
    "pypi": "pypi"
}

def get_dependent_reach(ecosystem: str, package_name: str) -> int:
    system = ECOSYSTEM_MAP.get(ecosystem.lower())
    if not system:
        return 1000

    cache_key = f"{system}:{package_name}"
    if cache_key in _DEPS_CACHE:
        return _DEPS_CACHE[cache_key]

    encoded = urllib.parse.quote(package_name, safe="")
    url = f"{DEPS_DEV_BASE}/{system}/packages/{encoded}"
    headers = {"User-Agent": "Maintainer-Fracture-Wire/1.0"}

    try:
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code == 200:
            data = res.json()
            count = int(data.get("dependentCount", data.get("dependentsCount", 1000)))
            _DEPS_CACHE[cache_key] = count
            return count
    except Exception as e:
        logging.warning(f"deps.dev check failed for {package_name}: {e}")

    _DEPS_CACHE[cache_key] = 1000
    return 1000
