import os

# Remote Git configuration
GIT_REPO_URL = os.getenv("git_repo_url", "git@github.com:micxba/gitops.git")
GIT_BRANCH = os.getenv("git_branch", "main")

# Personal access token for private repositories (GitHub or GitLab)
GIT_TOKEN = os.getenv("git_token")

# Folder within the repo to scan for Argo Application YAMLs
ARGO_APPS_FOLDER = os.getenv("argo_apps_folder", "apps")

# YAML field lookups (used in Application and ApplicationSet parsing)
APP_HELM_REPO_PATH = os.getenv("app_helm_repo_path", "spec.sources[*].repoURL")
APP_HELM_TARGET_REVISION = os.getenv("app_helm_targetrevision", "spec.sources[*].targetRevision")
APP_HELM_CHART = os.getenv("app_helm_chart", "spec.sources[*].chart")

APPSET_HELM_REPO_PATH = os.getenv("appset_helm_repo_path", "spec.template.spec.sources[*].repoURL")
APPSET_HELM_TARGET_REVISION = os.getenv("appset_helm_targetrevision", "spec.template.spec.sources[*].targetRevision")
APPSET_HELM_CHART = os.getenv("appset_helm_chart", "spec.template.spec.sources[*].chart")
