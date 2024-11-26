import argparse
import subprocess
from java_processor import JavaProcessor
import os
import sys
import time

class ClassRelation():
    def __init__(self, params):
        self.params = vars(params)
        self.get_source_file_command = f"find . -type f -name '*.{self.params['auth_ext']}'"
        if self.params["auth_ext"] == 'java':
            self.processor = JavaProcessor()
        else:
            self.processor = None
            
        self.source_file_paths = self.get_source_file_paths()
        self.fqcn_list = []
        self.class_relations = []  # クラス間の関係を格納するリスト
      
    def get_fqcn_list(self):
        st = time.time()
        for source_file_path in self.source_file_paths:
            with open(source_file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            package_name = self.processor.process(code, "package_declaration")
            if not(package_name):
                continue
            # public_class_name = os.path.splitext(os.path.basename(source_file_path))[0]
            public_class_name = source_file_path.split('.')[0].split('\\')[-1]
            # print(public_class_name)
            # public_class_name = self.processor.process(code, "public_class_declaration", source_file_path.)
            # if public_class_name == None:
            #     continue
            # if len(parent_class_name) > 1:
            #     print(source_file_path)
            self.fqcn_list.append(package_name+'.'+public_class_name)
            # self.fqcn_list.extend(
            #     [f"{package_name}.{class_name}" for class_name in parent_class_names]
            # )
        en = time.time()
        print(f"get_fqcn_list process time:{en-st}")
    
    def make_class_relation_map(self):
        # self.get_fqcn_list()
        # source_file_path = "C:/Users/masak/workspace/sample_data/camel/core/camel-core/src/test/java/org/apache/camel/AutoCloseableTest.java"
        for source_file_path in self.source_file_paths:
            with open(source_file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            # print(source_file_path)
            package_name = self.processor.process(code, "package_declaration")
            public_class_name = source_file_path.split('.')[0].split('\\')[-1]
                # public_class_name = self.processor.process(code, "public_class_declaration")
            
            if not(package_name):
                continue
                # print(class_fqcn_list)
                # if len(class_fqcn_list) > 1:
                #     print(source_file_path)
            # print(package_name, public_class_name)
            type_list = self.processor.process(code, "type_identifier", public_class_name)
            import_list = self.processor.process(code, "import_declaration")
            if type_list:
                for type_name in type_list:
                    referenced_class_fqcn = self.find_fully_qualified_class_name(type_name, import_list) 
                    if referenced_class_fqcn:
                        self.class_relations.append((package_name+'.'+public_class_name, referenced_class_fqcn))
                    # print(self.class_relations)
                
    def find_fully_qualified_class_name(self, type_name, import_list):
        """型名から完全修飾子を検索する"""
        # 1. import宣言から検索
        if import_list:
            for import_item in import_list:
                if import_item.endswith(f".{type_name}"):
                    return import_item
            
            # 2. ワイルドカードインポート（import *）から検索
            for import_item in import_list:
                if import_item.endswith(".*"):
                    potential_fqcn = f"{import_item[:-2]}.{type_name}"
                    if potential_fqcn in self.fqcn_list:
                        return potential_fqcn
        
        # 3. ローカルの完全修飾子リストから検索
        for fqcn in self.fqcn_list:
            if fqcn.endswith(f".{type_name}"):
                return fqcn
        
        return None        
    
    def export_to_dot(self, output_path="class_relations.dot"):
        """クラス間の関係をDot形式でファイルに出力する"""
        with open(output_path, 'w') as f:
            f.write("digraph ClassRelations {\n")
            for (source_class, target_class) in self.class_relations:
                f.write(f'    "{source_class}" -> "{target_class}";\n')
            f.write("}\n")    
    
    def get_source_file_paths(self):
        result = subprocess.run(
            self.get_source_file_command,
            stdout=subprocess.PIPE,
            text=True,
            cwd=self.params["project_path"],
            shell=True
        )
        
        source_file_paths = [
            os.path.abspath(self.params["project_path"]+source_file_path) for source_file_path in result.stdout.splitlines()
        ]
        return source_file_paths


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_path', type=str, default='../../../sample_data/camel')
    parser.add_argument('--auth_ext', type=str, default='java')
    # parser.add_argument('--output_dot', type=str, default='class_relations.dot')
    return parser


if __name__ == '__main__':
    params = read_args().parse_args()
    cr = ClassRelation(params)
    # print(cr.source_file_paths)
    cr.get_fqcn_list()
    cr.make_class_relation_map()
    cr.export_to_dot()
    