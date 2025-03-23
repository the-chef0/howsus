from code_meter import CodeMeter
from community_meter import CommunityMeter
from repo_handler import RepoHandler

handler = RepoHandler(
    access_token="",
    repo_owner="apache",
    repo_name="arrow"
)

handler.clone_repo()
code_meter = CodeMeter(handler=handler, py_file_dir="python/pyarrow")
community_meter = CommunityMeter(handler=handler)
print(f"Abstractness: {code_meter.get_abstractness()}")
print(f"Instability: {code_meter.get_instability()}")
print(f"Merged PRs: {community_meter.get_merged_pr_count()}")
print(f"Closed issues: {community_meter.get_closed_issue_count()}")