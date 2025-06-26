import os
import subprocess

def ensure_git_repo(folder, repo_url):
    if not os.path.isdir(folder):
        print(f"Cloning repo {repo_url} into {folder}")
        subprocess.run(["git", "clone", repo_url, folder], check=True)
    else:
        print(f"Pulling latest changes in {folder}")
        subprocess.run(["git", "-C", folder, "pull"], check=True)