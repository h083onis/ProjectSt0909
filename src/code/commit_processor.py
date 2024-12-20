import argparse
import json
import os
import subprocess
import time
import traceback
import sys

import pandas as pd
from git import Repo
from gitdb.exc import BadName

from class_relation import ClassRelation
from graph_search import GraphSearch
from remove_comment import RemoveComment
from utils import Logging


class CommitProcessor():
    def __init__(self, params):
        self.params =  params if isinstance(params, dict) else vars(params)
        self.project_repo = Repo(params.project_path)
        df = pd.read_csv(params.label_csv_path)
        self.commit_ids = df['commit_hash']
        self.auth_ext = params.auth_ext
        
        self.before_txt = 'before.txt'
        self.after_txt = 'after.txt'
  
        self.empty_commmit_id = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'
        self.diff_command = ("diff -B -w --old-line-format=<\t%dn\n --new-line-format=>\t%dn\n --unchanged-line-format= "+self.before_txt+" "+self.after_txt).split(' ')
        self.cr = ClassRelation(self.params)
        self.rc = RemoveComment()
        self.gs = GraphSearch()
        self.logger = Logging()
        
    def excute(self, output_path=None):
        if not(output_path):
            output_path = self.params["project_path"].split('/')[-1]+'.txt'

        with open(output_path, "w") as f:
            for i, commit_id in enumerate(self.commit_ids):
                print(str(i+1)+' / '+str(self.commit_ids.shape[0]))
                print(commit_id)
                st = time.time()
                try:
                    self.project_repo.git.checkout(commit_id)
                    try:
                        commit = self.project_repo.commit(commit_id+'~1')
                    except (IndentationError, BadName):
                        commit = self.project_repo.commit(self.empty_commmit_id)
                    diff = commit.diff(commit_id)
                    
                    changed_files = self.process_commit(diff, commit_id)
                    if len(changed_files) == 0:
                        continue
                    
                    json_data = {}
                    class_relations = self.cr.make_class_relation_map()
                    
                    self.gs.read_dict(class_relations)
                    changed_files_with_test_files = []
                    for ch_file in changed_files:
                        chd_file_with_test_file = {}
                        abs_file_path = os.path.abspath(self.params["project_path"]+'/'+ch_file)
                        if abs_file_path not in self.cr.path_to_fqcn_dict.keys():
                            continue
                        fqcn = self.cr.path_to_fqcn_dict[abs_file_path]
                        test_files = self.gs.find_files_with_keyword(fqcn)
                        chd_file_with_test_file["source_path"] = ch_file
                        chd_file_with_test_file["fqcn"] = fqcn
                        for test in test_files:
                            relative_path = os.path.relpath(
                                self.cr.fqcn_to_path_dict[test["fqcn"]], start=self.params["project_path"]
                            )
                            test["test_path"] = relative_path.replace('\\', '/') 
                        chd_file_with_test_file["test_file"] = test_files
                        changed_files_with_test_files.append(chd_file_with_test_file)
                        
                    json_data["commit_id"] = commit_id
                    json_data["timestamp"] = commit.committed_date
                    json_data["commit_author"] = commit.author.name
                    json_data["changed_files"] = changed_files_with_test_files
                    print(str(json_data), file=f)
                except Exception as e:
                    print(e)
                    error_message = traceback.format_exc()
                    print(error_message)
                    self.logger.log_debug_info(commit_id, e, error_message)
                finally:
                    en = time.time()
                    self.logger.log_commit_time(commit_id, en-st)  
            
    def process_commit(self, diff, commit_id):
        #変更されたファイルを抽出する
        changed_files = []
        for item in diff:
            ch_type = item.change_type
            if not(item.b_path.endswith('.'+self.auth_ext)) or ch_type == 'D':
                continue
            # elif ch_type in {'M', 'R'}:
            #     self.out_file_content(commit_id, item.a_path, file_type=self.before_txt)
            #     self.out_file_content(commit_id, item.b_path, file_type=self.after_txt)
            # elif ch_type in {'A', 'C'}:
            #     with open(self.before_txt,'w', encoding='utf-8') as f:
            #         f.truncate(0)
            #     self.out_file_content(commit_id, item.b_path, file_type=self.after_txt)
            # else:
            #     continue
            
            # ch_line_num = self.get_ch_line_num()
            # if not(ch_line_num):
            #     continue
            changed_files.append(item.b_path)
            
        return changed_files
    
    def out_file_content(self, commit_id, file_path, file_type):
        output = self.project_repo.git.show(commit_id+("~1:" if file_type == self.before_txt else ':')+file_path)
        output = self.rc.remove_comment(output, file_path.split('.')[-1])
        with open(file_type, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(output.replace('\r\n', '\n'))
            
    def get_ch_line_num(self):
        result = subprocess.run(self.diff_command, stdout=subprocess.PIPE, text=True)
        if result.stdout == '':
            return None
        ch_line_num_list=[[],[]] #index 0 number of before  index 1 number of after
        [ch_line_num_list[0].append(tmp.split('\t')[1]) if tmp[0] == '<' \
            else ch_line_num_list[1].append(tmp.split('\t')[1]) \
                for tmp in result.stdout.split('\n')[:-1]]
        return ch_line_num_list

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_path', type=str, default='../../../../sample_data/camel')
    parser.add_argument('--auth_ext', type=str, default='java')
    parser.add_argument('--label_csv_path', type=str, default='../../../../sample_data/label_dataset/data/camel.csv')
    return parser

if __name__ == "__main__":
    params = read_args().parse_args()
    cp = CommitProcessor(params)
    cp.excute()