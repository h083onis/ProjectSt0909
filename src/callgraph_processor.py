
from git import Repo
from gitdb.exc import BadName
import pandas as pd
import subprocess
from src2.java_processor import JavaProcessor


class CallgraphProcessor():
    def __init__(self, params):
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
        self.get_test_file_command = "find -type f -name '*Test*.java'".split(' ')
        self.java_command = "java -jar ?.jar".split(' ')
        
        self.java_parser = JavaProcessor()

        
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
        
        
    def process_commit(self, diff, commit_id):
        for item in diff:
            ch_type = item.change_type
            if not(self.is_auth_ext(ch_type)) or ch_type == 'D':
                continue
            self.out_file_content(commit_id, item.a_path, file_type=self.before_txt, process_type='no_comment')
            self.out_file_content(commit_id, item.b_path, file_type=self.after_txt, process_type='no_comment')
            
            ch_line_num = self.get_ch_line_num()
            if ch_line_num == None:
                continue
            
            # 変更前後で影響を受けたメソッドを抽出
            before_method_dict = self.java_parser.get_method_dict(self.before_txt)
            after_method_dict = self.java_parser.get_method_dict(self.after_txt)
            before_ch_class_method_set = self.get_ch_method_list(before_method_dict, ch_line_num[0])
            after_ch_class_method_set = self.get_ch_method_list(after_method_dict, ch_line_num[1])
            ch_class_method_name_set = before_ch_class_method_set | after_ch_class_method_set
            
            # 影響を受けたメソッドのうち変更後にのみ残っているメソッドを抽出
            after_exist_ch_class_method_list = []
            for ch_class_method_name in ch_class_method_name_set:
                if ch_class_method_name not in after_method_dict:
                    continue
                if ch_class_method_name in after_method_dict.keys() and ch_class_method_name in before_method_dict.keys() \
                    and after_method_dict[ch_class_method_name]['content'] == before_method_dict[ch_class_method_name]['content']:
                    continue
                after_exist_ch_class_method_list.append(ch_class_method_name)
            
            #コメント・空白類ありで影響を受けた変更後のメソッドの位置情報を抽出
            self.out_file_content(commit_id, item.b_path, file_type=self.after_txt, process_type='with_comment')
            after_method_dict_with_comment_dict = self.java_parser.get_method_dict(self.after_txt)
            ch_class_method_name_set_with_comment_list = [{class_method:after_method_dict_with_comment_dict[class_method]['position']} for class_method in after_exist_ch_class_method_list]
        
        
        #コールグラフ作成
        self.make_callgraph(commit_id, after_method_dict_with_comment_dict['package_name'], ch_class_method_name_set_with_comment_list)
        
            
    def out_file_content(self, commit_id, file_path, file_type, process_type):
        output = self.project_repo.git.show(commit_id+("~1:" if file_type == self.before_txt else ':')+file_path)
        if process_type == 'no_comment':
            output = self.java_parser.remove_comment(output)
        with open(type+'.txt', 'w', encoding='utf-8', errors='ignore') as f:
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
    
    def get_ch_method_list(self, method_dict, ch_line_num):
        ch_method_name_set = ()
        extracted_list = []
        for ch_line_num in ch_line_num:
            for i, (key, value) in enumerate(method_dict.items()):
                for i in extracted_list:
                    continue
                if int(value['position'][0][0])+1 <= int(ch_line_num) \
                    and int(value['position'][1][0]) >= int(ch_line_num):
                    ch_method_name_set.add(key)
                    extracted_list.append(i)
                    break
        return ch_method_name_set
    
    def get_test_file_path(self):
        result = subprocess.run(self.get_test_file_command, stdout=subprocess.PIPE, text=True)
        assert result != '', 'error: does not find test files'
        
        with open(self.test_txt, 'w', encoding='utf-8') as f:
            f.write(result.replace('\r\n', '\n'))
        
    def make_callgraph(self, commit_id, package_name, method_list):
        input_command = self.java_command + [commit_id, self.params.project_path, package_name]
        # package classname [行位置、行位置] classname [行位置、行位置]
        result = subprocess.run(self.java_command, stdout=subprocess.PIPE, text=True)
        assert result != '', "error: no result when making a callgraph"
        