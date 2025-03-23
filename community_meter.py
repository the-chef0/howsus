from datetime import datetime, timedelta
from repo_handler import RepoHandler

class CommunityMeter:

    def __init__(self, handler: RepoHandler, timeframe: int = 30):
        self._handler = handler
        cutoff_date = datetime.now() - timedelta(days=timeframe)
        self._formatted_date = cutoff_date.strftime('%Y-%m-%d')

    def get_merged_pr_count(self) -> int:
        merged_pr_query = f'is:pr merged:>={self._formatted_date}'
        merged_pr_result = self._handler.get_issue_query_result(merged_pr_query)
        return merged_pr_result.totalCount

    def get_closed_issue_count(self) -> int:
        closed_issue_query = f'is:issue closed:>={self._formatted_date}'
        closed_issue_result = self._handler.get_issue_query_result(closed_issue_query)
        return closed_issue_result.totalCount
