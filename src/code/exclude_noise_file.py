import argparse
import json
import traceback
import sys

import hashlib

import pandas as pd
from git import Repo
from gitdb.exc import BadName

from remove_comment import RemoveComment

class ExcludeNoiseFile():
    def __init__(self, params):
        self.params =  params if isinstance(params, dict) else vars(params)
        self.project_repo = Repo(params.project_path)
        df = pd.read_csv(params.label_csv_path)
        self.commit_ids = df['commit_hash']
        self.auth_ext = params.auth_ext
        
        self.before_txt = 'before.txt'
        self.after_txt = 'after.txt'
  
        self.empty_commit_id = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'
        self.rc = RemoveComment()
        
    def excute(self, output_path=None):
        commit_list = []
        for i, commit_id in enumerate(self.commit_ids):
            print(str(i+1)+' / '+str(len(self.commit_ids)))
            print(commit_id)
            try:
                commit = self.get_commit(commit_id)
                if commit:
                    changed_files = self.process_commit(commit, commit_id)
                    if changed_files:
                        commit_list.append({
                            "commit_id": commit_id,
                            "changed_files": changed_files
                        })
            except Exception as e:
                print(f"Error processing commit {commit_id}: {e}")
                print(traceback.format_exc())
                    
        self.save_results(commit_list, output_path)

    def get_commit(self, commit_id):
        try:
            commit = self.project_repo.commit(commit_id)
            if not commit.parents:
                print(f"Commit {commit_id} has no parent; treating as initial commit.")
                parent_commit = self.project_repo.tree(self.empty_commit_id)
            else:
                parent_commit = commit.parents[0]
            return parent_commit.diff(commit_id)
        except (IndentationError, BadName, ValueError) as e:
            print(f"Error accessing parent commit for {commit_id}: {e}")
            return None
                            
    def process_commit(self, diff, commit_id):
        #変更されたファイルを抽出する
        changed_files = []
        for item in diff:
            ch_type = item.change_type
            file_path = item.b_path
            if not item.b_path.endswith(f'.{self.auth_ext}') or ch_type == 'D':
                continue
            
            before_content, after_content = self.get_file_contents(ch_type, commit_id, item)
            if self.is_file_modified(before_content, after_content):
                changed_files.append(file_path)

        return changed_files

    def get_file_contents(self, ch_type, commit_id, item):
        if ch_type in {'M', 'R'}:
            before_content = self.out_file_content(commit_id, item.a_path, file_type=self.before_txt)
            after_content = self.out_file_content(commit_id, item.b_path, file_type=self.after_txt)
        elif ch_type in {'A', 'C'}:
            before_content = ''
            after_content = self.out_file_content(commit_id, item.b_path, file_type=self.after_txt)
        else:
            before_content = after_content = ''
        return before_content, after_content
    
    def is_file_modified(self, before_content, after_content):
        before_content = ''.join(before_content.split())
        after_content = ''.join(after_content.split())
        return hashlib.sha256(before_content.encode('utf-8', errors='ignore')).hexdigest() != hashlib.sha256(after_content.encode('utf-8', errors='ignore')).hexdigest()
    
    def out_file_content(self, commit_id, file_path, file_type):
        output = self.project_repo.git.show(f'{commit_id}{"~1:" if file_type == self.before_txt else ":"}{file_path}')
        output = self.rc.remove_comment(output, file_path.split('.')[-1])
        return output
    
    def save_results(self, commit_list, output_path):
        if not output_path:
            output_path = "changed_files.json"
        with open(output_path, "w") as f:
            json.dump(commit_list, f, indent=2)
            
def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_path', type=str, default='../../../../sample_data/camel')
    parser.add_argument('--auth_ext', type=str, default='java')
    parser.add_argument('--label_csv_path', type=str, default='../../../../sample_data/label_dataset/data/camel.csv')
    return parser

if __name__ == "__main__":
    params = read_args().parse_args()
    enf = ExcludeNoiseFile(params)
    enf.excute()
    sys.exit(0)