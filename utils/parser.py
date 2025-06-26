import aiohttp
import yaml
import os
from config import GIT_REPO_URL, ARGO_APPS_FOLDER

def get_repo_info():
    """Convert git@github.com:user/repo.git to (user, repo)"""
    repo_url = GIT_REPO_URL
    if repo_url.startswith("git@github.com:"):
        repo_url = repo_url.replace("git@github.com:", "")
    repo_url = repo_url.replace(".git", "")
    parts = repo_url.split("/")
    return parts[0], parts[1]  # user, repo

async def fetch_github_yaml_files():
    user, repo = get_repo_info()
    branch = "main"
    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{ARGO_APPS_FOLDER}"
    raw_base = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{ARGO_APPS_FOLDER}"

    yamls = []

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to list files in folder: {resp.status}")
            files = await resp.json()

        for f in files:
            if f["name"].endswith((".yaml", ".yml")):
                raw_url = f"{raw_base}/{f['name']}"
                async with session.get(raw_url) as yf:
                    if yf.status != 200:
                        continue
                    content = await yf.text()
                    docs = list(yaml.safe_load_all(content))
                    yamls.extend([doc for doc in docs if doc])
    return yamls

def is_helm_source(source):
    return isinstance(source, dict) and "chart" in source and "repoURL" in source and "targetRevision" in source

def extract_apps(yaml_docs):
    apps = []
    for doc in yaml_docs:
        kind = doc.get("kind")
        metadata = doc.get("metadata", {})
        name = metadata.get("name", "unknown")
        if kind not in ("Application", "ApplicationSet"):
            continue

        if kind == "Application":
            sources = doc.get("spec", {}).get("sources", [])
        else:
            sources = doc.get("spec", {}).get("template", {}).get("spec", {}).get("sources", [])

        for src in sources:
            if is_helm_source(src):
                apps.append({
                    "name": name,
                    "kind": kind,
                    "repoURL": src["repoURL"],
                    "chart": src["chart"],
                    "currentVersion": src["targetRevision"]
                })
    return apps
