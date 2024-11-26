from tree_sitter import Language, Parser
import tree_sitter_java as tsjava
import os
import sys
import re


class JavaProcessor():
    def __init__(self):
        self.CODE = 1
        self.C_COMMENT = 2
        self.CPP_COMMENT = 3
        self.STRING_SINGLE_LITERAL = 4
        self.STRING_DUBLE_LITERAL = 5
        
        self.parser = Parser(Language(tsjava.language()))

    # def get_class_names(self, node, class_names, parent_class=None): # Depth-First Search「深さ優先探索」
    #     # print(node.type+' '+node.text.decode("utf8", errors='ignore'))
    #     if node.type == 'interface_declaration':
    #         return
    #     if node.type == 'class_declaration':
    #         # print(node.type+' '+node.text.decode("utf8", errors='ignore'))
    #         for child in node.children:
    #             if child.type == 'identifier':
    #                 # print(child.type+' '+child.text.decode("utf8", errors='ignore'))
    #                 current_class_name = child.text.decode("utf8", errors='ignore')
    #                 class_names.append(current_class_name)
    #         return
    #         # if current_class_name:
    #         #     full_class_name = f"{parent_class}.{current_class_name}" if parent_class else current_class_name
    #         #     class_names.append(full_class_name)
    #         #     parent_class = full_class_name  # 現在のクラスを親クラスとして扱う

    #     [self.get_class_names(child, class_names, parent_class) for child in node.children]
    
    # def get_public_class_name(self, node, target_name):
    #     if node.type == 'interface_declaration' or node.type == 'class_declaration' or node.type == 'abstract_class_declaration':
    #         # public 修飾子を確認
    #         is_public = any(child.type == 'modifier' and child.text.decode("utf8", errors='ignore') == 'public' for child in node.children)
    #         if not is_public:
    #             return
            
    #         # クラス名を取得
    #         for child in node.children:
    #             if child.type == 'identifier':
    #                 current_class_name = child.text.decode("utf8", errors='ignore')
    #                 # ファイル名と一致するクラス名のみを追加
    #                 if current_class_name == target_name:
    #                     return current_class_name
    #         return

    #     for child in node.children:
    #         public_class_name = self.get_public_class_name(child, target_name)
    #         if public_class_name:
    #             return public_class_name
    #     return None
    
    def get_package_name(self, node):
        if node.type == 'package_declaration':
            for child in node.children:
                if child.type == 'scoped_identifier':
                    return child.text.decode("utf8", errors='ignore')

        for child in node.children:
            package_name = self.get_package_name(child)
            if package_name:
                return package_name
        return None
    
    def get_type_identifier_in_class(self, target_class, node, type_set):
        if node.type in ['interface_declaration', 'class_declaration', 'abstract_class_declaration']:
            for child in node.children:
                if not child.type == 'modifiers' and child.text.decode("utf8", errors='ignore') == 'public':
                    return
                if child.type == 'identifier':
                    class_name = child.text.decode("utf8", errors='ignore')
                    if target_class == class_name:
                        self._collect_type_identifiers(node, type_set)
            return
                
        [self.get_type_identifier_in_class(target_class, child, type_set) for child in node.children]
    
    def _collect_type_identifiers(self, node, type_set, parent_class=None):
        if node.type == 'scoped_type_identifier':
            identifiers = [child.text.decode("utf8", errors='ignore') for child in node.children if child.type == 'type_identifier']
            if len(identifiers) > 1:
                parent_class = identifiers[0]  # 最初の識別子が親クラス名
                inner_class = identifiers[1]  # 2番目が内部クラス名
                # type_list.append(f"{parent_class}.{inner_class}")
                type_set.add(parent_class)
            return
        
        if node.type == 'type_identifier':
            parent_class = node.text.decode("utf-8", errors='ignore')
            type_set.add(parent_class)
            return

        [self._collect_type_identifiers(child, type_set, parent_class=None) for child in node.children]
        
    def get_import_declaration(self, node, import_list):
        if node.type == 'import_declaration':
            for child in node.children:
                if child.type == 'scoped_identifier':
                    import_list.append(child.text.decode("utf-8", errors='ignore'))
                    return
                
        [self.get_import_declaration(child, import_list) for child in node.children]
        
    def process(self, code, process_type=None, target_class=None):
        code = bytes(code, "utf8", errors='ignore')
        tree = self.parser.parse(code)
        # if process_type == "public_class_declaration":
        #     return self.get_public_class_name(tree.root_node, target_class)
        if process_type == "package_declaration":
            return self.get_package_name(tree.root_node)
        if process_type == "type_identifier":
            type_set = set()
            self.get_type_identifier_in_class(target_class, tree.root_node, type_set)
            if len(type_set) == 0:
                return None
            return list(type_set)
        elif process_type == "import_declaration":
            import_list = []
            self.get_import_declaration(tree.root_node, import_list)
            if len(import_list) == 0:
                return None
            return import_list
        else:
            return None
    
    def remove_comment(self, text):
        # 正規表現を使用してコメントを削除
        pattern = r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"'
        regex = re.compile(pattern, re.DOTALL | re.MULTILINE)
        # コメントを空文字に置き換える
        filtered_text = regex.sub(lambda x: '' if x.group(0).startswith(('/', '/*')) else x.group(0), text)
        # 空行の削除
        line_list = [line for line in filtered_text.split('\n') if line.strip() != '']
        return '\n'.join(line_list)
        
    # def remove_comment(self, text):
    #     result = []
    #     prev = ''
    #     state = self.CODE
    #     escape_cnt = 0

    #     for ch in text:
    #         # Skip to the end of C-style comment
    #         if state == self.C_COMMENT:
    #             if escape_cnt % 2 == 0 and prev == '*' and ch == '/':
    #                 state = self.CODE
    #                 escape_cnt = 0
    #                 prev = ''
    #                 continue
    #             if ch == '\\':
    #                 escape_cnt += 1
    #             else:
    #                 escape_cnt = 0
    #             if ch == '\n':
    #                 prev = ''
    #             else:
    #                 prev = ch
    #             continue

    #         # Skip to the end of the line (C++ style comment)
    #         if state == self.CPP_COMMENT:
    #             if ch == '\n':  # End comment
    #                 state = self.CODE
    #                 result.append('\n')
    #                 prev = ''
    #             continue

    #         # Skip to the end of the string literal
    #         if state == self.STRING_DUBLE_LITERAL:
    #             if escape_cnt % 2 == 0 and ch == '"':
    #                 state = self.CODE
    #                 escape_cnt = 0
    #             if ch == '\\':
    #                 escape_cnt += 1
    #             else:
    #                 escape_cnt = 0
    #             # print(prev)
    #             result.append(prev)
    #             prev = ch
    #             continue
            
    #          # Skip to the end of the string literal
    #         if state == self.STRING_SINGLE_LITERAL:
    #             if escape_cnt % 2 == 0 and ch == '\'':
    #                 state = self.CODE
    #                 escape_cnt = 0
    #             if ch == '\\':
    #                 escape_cnt += 1
    #             else:
    #                 escape_cnt = 0
    #             result.append(prev)
    #             prev = ch
    #             continue
            
    #         if ch == '\\':
    #             escape_cnt += 1
    #         else:
    #             escape_cnt = 0
    #         # Starts C-style comment?
    #         if escape_cnt % 2 == 0 and prev == '/' and ch == '*':
    #             state = self.C_COMMENT
    #             prev = ''
    #             escape_cnt = 0
    #             continue

    #         # Starts C++ style comment?
    #         if escape_cnt % 2 == 0 and prev == '/' and ch == '/':
    #             state = self.CPP_COMMENT
    #             prev = ''
    #             escape_cnt = 0
    #             continue

    #         # Comment has not started yet
    #         if prev: result.append(prev)

    #         # Starts string literal?
    #         if escape_cnt % 2 == 0 and ch == '\'':
    #             state = self.STRING_SINGLE_LITERAL
    #             escape_cnt = 0
            
    #         # Starts string literal?
    #         if escape_cnt % 2 == 0 and ch == '"':
    #             state = self.STRING_DUBLE_LITERAL
    #             escape_cnt = 0
    #         prev = ch

    #     # Returns filtered text
    #     if prev: result.append(prev)
    #     line_list = [line for line in ''.join(result).split('\n') if line.strip() != '']
    #     result = '\n'.join(line_list)
    #     return result
    
