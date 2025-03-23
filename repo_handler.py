from github import Github

import subprocess

class RepoHandler:

    def __init__(self, access_token: str, repo_owner: str, repo_name: str, working_dir: str = "./temp"):
        self._github = Github(access_token)
        self._repo_owner = repo_owner
        self._repo_name = repo_name
        self._working_dir = working_dir
        self._repo = self._github.get_repo(f"{repo_owner}/{repo_name}")

    def get_repo_clone_url(self) -> str:
        return self._repo.ssh_url

    def get_issue_query_result(self, issue_query: str) -> str:
        query_on_repo = f"repo:{self._repo_owner}/{self._repo_name} {issue_query}"
        return self._github.search_issues(query=query_on_repo)

    def clone_repo(self):
        repo_url = self._repo.ssh_url
        
        subprocess.run(
            ["git", "clone", repo_url, f"{self._working_dir}/{self._repo_name}"],
            check=True
        )
        print(f"Repository cloned to {self._working_dir}")

    def get_working_dir(self) -> str:
        return self._working_dir

    def get_repo_name(self) -> str:
        return self._repo_name