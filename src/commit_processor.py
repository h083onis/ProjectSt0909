import pandas as pd
from git import Repo
from gitdb.exc import BadName
from class_relation import ClassRelation

class CommitProcessor():
    def __init__(self, params):
        if params != dict:
            self.params = vars(params)
        else:
            self.params = params
        self.project_repo = Repo(params.project_path)
        df = pd.read_csv(params.label_csv_path)
        self.commit_ids = df['comit_id']
        self.auth_ext = params.auth_ext
        
        self.before_txt = 'before.txt'
        self.after_txt = 'after.txt'
        self.test_txt = 'test.txt'
        self.empty_commmit_id = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'
        self.diff_command = "diff -B -w --old-line-format=<\t%dn\n --new-line-format=>\t%dn\n --unchanged-line-format= "+self.before.txt+" "+self.after_txt.split(' ')
        self.cr = ClassRelation()
        self.
        
    def excute(self):
        for commit_id in self.commit_ids:
            self.project_repo.git.checkout(commit_id)
            
            try:
                commit = self.project_repo.commit(commit_id+'~1')
            except (IndentationError, BadName):
                commit = self.project_repo.commit(self.empty_commmit_id)
            diff = commit.diff(commit_id)
            
            if self.process_commit(diff, commit_id):
                continue
            self.get_test_file_path()
            
    def is_auth_ext(self, file_path):
        return any(file_path.endswith('.'+auth) for auth in self.auth_ext)
    
    def out_file_content(self, commit_id, file_path, file_type):
        output = self.project_repo.git.show(commit_id+("~1:" if file_type == self.before_txt else ':')+file_path)
        output = self.java_parser.remove_comment(output)
        with open(type+'.txt', 'w', encoding='utf-8', errors='ignore') as f:
            f.write(output.replace('\r\n', '\n'))
             