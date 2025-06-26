from flask import Flask, render_template, jsonify, request
from utils.parser import fetch_github_yaml_files, extract_apps
from utils.helm import fetch_all_chart_versions
from config import GIT_BRANCHES
import asyncio

app = Flask(__name__)

@app.route('/')
def index():
    # Initial data without remote helm version checks
    default_branch = GIT_BRANCHES[0]
    docs = asyncio.run(fetch_github_yaml_files(default_branch))
    apps = extract_apps(docs)
    for app in apps:
        app['latestVersion'] = "loading..."
    return render_template(
        "index.html",
        apps=apps,
        branches=GIT_BRANCHES,
        selected_branch=default_branch,
    )

@app.route('/data')
def data():
    branch = request.args.get('branch', GIT_BRANCHES[0])
    docs = asyncio.run(fetch_github_yaml_files(branch))
    apps = extract_apps(docs)
    for app_data in apps:
        app_data['latestVersion'] = "loading..."
    return jsonify(apps)

@app.route('/latest')
def latest():
    async def load_latest():
        branch = request.args.get('branch', GIT_BRANCHES[0])
        docs = await fetch_github_yaml_files(branch)
        apps = extract_apps(docs)
        tasks = [fetch_all_chart_versions(app['repoURL'], app['chart']) for app in apps]
        all_versions_list = await asyncio.gather(*tasks)

        enriched = []
        for app, versions in zip(apps, all_versions_list):
            if isinstance(versions, dict) and "error" in versions:
                enriched.append({
                    "name": app["name"],
                    "chart": app["chart"],
                    "currentVersion": app["currentVersion"],
                    "latestVersion": "error",
                    "allVersions": []
                })
            else:
                enriched.append({
                    "name": app["name"],
                    "chart": app["chart"],
                    "currentVersion": app["currentVersion"],
                    "latestVersion": versions[0],
                    "allVersions": versions
                })
        return enriched

    results = asyncio.run(load_latest())
    return jsonify(results)




if __name__ == "__main__":
    app.run(debug=True)
