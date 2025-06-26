import aiohttp
import yaml
import os
import base64
from config import GIT_REPO_URL, ARGO_APPS_FOLDER, GIT_BRANCH, GIT_TOKEN

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
    api_url = (
        f"https://api.github.com/repos/{user}/{repo}/contents/"
        f"{ARGO_APPS_FOLDER}?ref={GIT_BRANCH}"
    )

    headers = {"Accept": "application/vnd.github.v3+json"}
    if GIT_TOKEN:
        headers["Authorization"] = f"Bearer {GIT_TOKEN}"

    yamls = []

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(api_url) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to list files in folder: {resp.status}")
            files = await resp.json()

        for f in files:
            if f["name"].endswith((".yaml", ".yml")):
                file_url = f["url"]
                async with session.get(file_url) as yf:
                    if yf.status != 200:
                        continue
                    file_data = await yf.json()
                    content = file_data.get("content", "")
                    if file_data.get("encoding") == "base64":
                        content = base64.b64decode(content).decode()
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
