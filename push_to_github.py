"""
Helper script to push the repository to GitHub using Dulwich.
Usage:
    python push_to_github.py <GITHUB_TOKEN>
or:
    python push_to_github.py
(it will securely prompt for the token)
"""

import sys
import getpass
from dulwich import porcelain

REPO_URL = "https://github.com/reddyhemanthkumar112-a11y/project1.git"

def main():
    token = None
    if len(sys.argv) > 1:
        token = sys.argv[1].strip()
    else:
        print("GitHub requires authentication to push.")
        print("Generate a Personal Access Token (classic or fine-grained) at:")
        print("https://github.com/settings/tokens (with 'repo' scope)")
        print()
        token = getpass.getpass("Enter your GitHub Personal Access Token: ").strip()

    if not token:
        print("Error: No token provided.")
        sys.exit(1)

    # Format authenticated URL
    # https://<token>@github.com/reddyhemanthkumar112-a11y/project1.git
    auth_url = f"https://{token}@github.com/reddyhemanthkumar112-a11y/project1.git"

    print("Opening repository...")
    repo = porcelain.open_repo(".")

    print(f"Pushing 'main' branch to {REPO_URL}...")
    try:
        porcelain.push(repo, auth_url.encode("utf-8"), b"refs/heads/main:refs/heads/main")
        print("=" * 60)
        print("SUCCESS! All files pushed to GitHub repository:")
        print(REPO_URL)
        print("=" * 60)
    except Exception as e:
        print(f"Push failed: {e}")
        print()
        print("Tip: Ensure your GitHub Personal Access Token has 'repo' write permissions.")
        sys.exit(1)

if __name__ == "__main__":
    main()
