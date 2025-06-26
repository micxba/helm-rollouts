import aiohttp
import yaml

async def fetch_all_chart_versions(repo_url, chart):
    try:
        if repo_url.startswith("oci://"):
            return {"error": "OCI not supported yet"}

        index_url = repo_url.rstrip("/") + "/index.yaml"
        async with aiohttp.ClientSession() as session:
            async with session.get(index_url) as resp:
                if resp.status != 200:
                    raise Exception(f"HTTP {resp.status}")
                index_data = await resp.text()
                parsed = yaml.safe_load(index_data)
                entries = parsed.get("entries", {})
                versions = entries.get(chart)
                if not versions:
                    raise Exception("Chart not found")
                return [v["version"] for v in versions]
    except Exception as e:
        return {"error": str(e)}

