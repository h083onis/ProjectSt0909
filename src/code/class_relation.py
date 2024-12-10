import argparse
import glob
import os
import time

from java_processor import JavaProcessor


class ClassRelation():
    def __init__(self, params):
        self.params =  params if isinstance(params, dict) else vars(params)
        if self.params["auth_ext"] == 'java':
            self.processor = JavaProcessor()
        else:
            raise ValueError("Unsupported programming language. Please set 'auth_ext' to 'java'.")
        self.source_file_paths = []
        self.path_to_fqcn_dict = {}
        self.fqcn_to_path_dict = {}
      
    def make_class_relation_map(self, to_dot=False, output_path="class_relations.dot"):
        """クラス間の関連を構築し、DOT形式で出力する"""
        self.get_source_file_paths()
        self.get_fqcn_dict()
        
        class_relations = []
        for src_path, fqcn_name in self.path_to_fqcn_dict.items():
            with open(src_path, 'r', encoding='utf-8') as f:
                code = f.read()
       
            public_class_name = src_path.split('\\')[-1].split('.')[0]
       
            idf_list = self.processor.process(code, "identifier", public_class_name)
            import_list = self.processor.process(code, "import_declaration")

            accessible_classes = self.resolve_accessible_classes(
                fqcn_name.rsplit('.', maxsplit=1)[0], import_list, self.path_to_fqcn_dict.values()
            )
            
            for idf_name in idf_list:
                if idf_name in accessible_classes.keys():
                    class_relations.append((fqcn_name, accessible_classes[idf_name]))
        
        if to_dot: self.export_to_dot(class_relations, output_path)
        
        return class_relations
    
            
    def get_fqcn_dict(self):
        """各ソースファイルのFQCNを取得"""
        for src_path in self.source_file_paths:
            try:
                with open(src_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                package_name = self.processor.process(code, "package_declaration")
                if package_name:
                    public_class_name = os.path.splitext(os.path.basename(src_path))[0]
                    self.path_to_fqcn_dict[src_path] = f"{package_name}.{public_class_name}"
                    self.fqcn_to_path_dict[f"{package_name}.{public_class_name}"] = src_path
            except Exception as e:
                print(f"Error reading file {src_path}: {e}")    
          
    def resolve_accessible_classes(self, package_name, import_list, fqcn_list):
        """利用可能なクラスを解決"""
        accessible_classes = {}
        
        # パッケージインポートとクラスインポートを分離
        package_imports = {imp[:-2] for imp in import_list if imp.endswith(".*")}
        class_imports = {imp for imp in import_list if not imp.endswith(".*")}
        
        for fqcn in fqcn_list:
            class_package, class_name = fqcn.rsplit('.', maxsplit=1)
            
            # クラスインポートを判定
            if fqcn in class_imports:
                accessible_classes[class_name] = fqcn
            # パッケージインポートを判定
            elif class_package in package_imports:
                accessible_classes[class_name] = fqcn
            # 同一パッケージ内のクラス判定
            elif class_package == package_name:
                accessible_classes[class_name] = fqcn
       
        return accessible_classes
    
    def export_to_dot(self, class_relations, output_path="class_relations.dot"):
        """DOT形式のファイルにエクスポート"""
        try:
            with open(output_path, 'w') as f:
                f.write("digraph ClassRelations {\n")
                for (source_class, target_class) in class_relations:
                    f.write(f'    "{source_class}" -> "{target_class}";\n')
                f.write("}\n")    
        except Exception as e:
            print(f"Error writing to {output_path}: {e}")
    
    def get_source_file_paths(self):
        relative_source_file_paths = glob.glob(self.params["project_path"]+"/**/*."+self.params['auth_ext'], recursive=True)
        
        self.source_file_paths = [
            os.path.abspath(source_file_path) for source_file_path in relative_source_file_paths
        ]


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_path', type=str, default='../../../../sample_data/camel')
    parser.add_argument('--auth_ext', type=str, default='java')
    # parser.add_argument('--output_dot', type=str, default='class_relations.dot')
    return parser


if __name__ == '__main__':
    params = read_args().parse_args()
    cr = ClassRelation(params)
    st = time.time()
    cr.make_class_relation_map(to_dot=True)
    en = time.time()
    print(en-st)
    