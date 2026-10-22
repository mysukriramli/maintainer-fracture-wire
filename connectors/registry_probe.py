import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import requests

logging.basicConfig(level=logging.INFO)

TARGET_PACKAGES = [
    # Widely adopted Python packages
    {"ecosystem": "pypi", "name": "requests", "alternatives": ["httpx", "aiohttp"]},
    {"ecosystem": "pypi", "name": "urllib3", "alternatives": ["httpx"]},
    {"ecosystem": "pypi", "name": "pyyaml", "alternatives": ["ruamel.yaml"]},
    {"ecosystem": "pypi", "name": "six", "alternatives": ["builtins"]},
    {"ecosystem": "pypi", "name": "peewee", "alternatives": ["sqlalchemy", "tortoise-orm"]},
    {"ecosystem": "pypi", "name": "tornado", "alternatives": ["fastapi", "asyncio"]},
    # Widely adopted npm packages
    {"ecosystem": "npm", "name": "express", "alternatives": ["fastify", "koa"]},
    {"ecosystem": "npm", "name": "lodash", "alternatives": ["radash", "remeda"]},
    {"ecosystem": "npm", "name": "moment", "alternatives": ["date-fns", "dayjs", "luxon"]},
    {"ecosystem": "npm", "name": "axios", "alternatives": ["ky", "fetch", "got"]},
    {"ecosystem": "npm", "name": "chalk", "alternatives": ["kleur", "picocolors"]},
    {"ecosystem": "npm", "name": "commander", "alternatives": ["yargs", "cac"]}
]

def probe_package(ecosystem: str, name: str) -> Optional[Dict[str, Any]]:
    headers = {"User-Agent": "Maintainer-Fracture-Wire/1.0"}
    now = datetime.now(timezone.utc)

    if ecosystem == "pypi":
        url = f"https://pypi.org/pypi/{name}/json"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                info = data.get("info", {})
                latest_ver = info.get("version", "0.0.0")
                releases = data.get("releases", {}).get(latest_ver, [])
                
                days_elapsed = 30.0
                if releases:
                    upload_time = releases[0].get("upload_time_iso_8601")
                    if upload_time:
                        dt = datetime.fromisoformat(upload_time.replace("Z", "+00:00"))
                        days_elapsed = max(0.0, (now - dt).total_seconds() / 86400.0)

                # Heuristic maintainer estimation from PyPI author strings
                author = info.get("author") or ""
                maintainer = info.get("maintainer") or ""
                m_count = 2 if (author and maintainer and author != maintainer) else 1

                return {
                    "package_name": name,
                    "ecosystem": "pypi",
                    "latest_version": latest_ver,
                    "days_since_last_release": round(days_elapsed, 1),
                    "maintainer_count": m_count,
                    "is_deprecated": False
                }
        except Exception as e:
            logging.warning(f"PyPI probe failed for {name}: {e}")

    elif ecosystem == "npm":
        url = f"https://registry.npmjs.org/{name}"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                latest_ver = data.get("dist-tags", {}).get("latest", "0.0.0")
                time_entry = data.get("time", {}).get(latest_ver)
                
                days_elapsed = 30.0
                if time_entry:
                    dt = datetime.fromisoformat(time_entry.replace("Z", "+00:00"))
                    days_elapsed = max(0.0, (now - dt).total_seconds() / 86400.0)

                maintainers = data.get("maintainers", [])
                m_count = len(maintainers) if isinstance(maintainers, list) else 1

                # Detect npm deprecation notice
                is_deprecated = "deprecated" in data.get("versions", {}).get(latest_ver, {})

                return {
                    "package_name": name,
                    "ecosystem": "npm",
                    "latest_version": latest_ver,
                    "days_since_last_release": round(days_elapsed, 1),
                    "maintainer_count": max(1, m_count),
                    "is_deprecated": is_deprecated
                }
        except Exception as e:
            logging.warning(f"npm probe failed for {name}: {e}")

    return None
