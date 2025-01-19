import argparse
from pydriller import Git
import json

# 修正キーワード
# bug_fix_keywords = ['fix', 'bug', 'resolve', 'patch']

# バグ修正コミットの解析
# for commit in Repository(repo_path).traverse_commits():
#     if any(keyword in commit.msg.lower() for keyword in bug_fix_keywords):
#         print(f"Bug-fix commit found: {commit.hash}")

class BugCommitSearcher():
    def __init__(self, params):
        self.params =  params if isinstance(params, dict) else vars(params)
        self.git = Git(self.params["project_path"])
    
    def search_bug_commit(self):
        with open(self.params["commit_ids_path"], 'r', encoding='utf-8') as f:
            commit_id_list = [commit_id.strip() for commit_id in f.readlines()]

        bug_commit_dict = {}
        for commit_id in commit_id_list:
            commit_obj = self.git.get_commit(commit_id)
            buggy_commits = self.git.get_commits_last_modified_lines(commit_obj)
            for key, values in buggy_commits.items():
                for value in values:
                    if value not in bug_commit_dict.keys():
                        bug_commit_dict[value] = set()
                    bug_commit_dict[value].add(key.replace('\\', '/'))
        
        processed_bug_commit_dict = {key:list(values) for key, values in bug_commit_dict.items()}
        
        with open(self.params["output_path"], 'w', encoding='utf-8') as f:
            json.dump(processed_bug_commit_dict, f, indent=2)
            
    
    

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_path', type=str, default='../../../../sample_data/camel')
    parser.add_argument('--commit_ids_path', type=str, default='../resource/bug_fix_commits.txt')
    parser.add_argument('--output_path', type=str, default='../resource/bug_commits.json')
    return parser
            
if __name__ == '__main__':
    params = read_args().parse_args()
    bla = BugCommitSearcher(params)
    bla.search_bug_commit()
    
