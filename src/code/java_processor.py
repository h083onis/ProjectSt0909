import tree_sitter_java as tsjava
from tree_sitter import Language, Parser


class JavaProcessor():
    def __init__(self):
        self.CODE = 1
        self.C_COMMENT = 2
        self.CPP_COMMENT = 3
        self.STRING_SINGLE_LITERAL = 4
        self.STRING_DUBLE_LITERAL = 5
        self.parser = Parser(Language(tsjava.language()))
    
    def get_package_name(self, node):
        for child in node.children:
            if child.type == 'package_declaration':
                code = child.text.decode("utf8", errors='ignore')
                return (code.split(' ')[1])[:-1]
        return None
    
    def get_type_identifier_in_class(self, target_class, node, idf_set):
        if node.type in {'interface_declaration', 'class_declaration', 'enum_declaration'}:
            for child in node.children:
                if child.type == 'identifier':
                    class_name = child.text.decode("utf8", errors='ignore')
                    if target_class != class_name:
                        return
                if child.type in {"superclass", "super_interfaces", "extends_interfaces"}:
                    self.collect_identifiers(child, idf_set)
                if child.type in {'class_body', 'interface_body', 'enum_body'}:
                    for child2 in child.children:
                        self.collect_identifiers(child2, idf_set)
            return
        
        for child in node.children:
            self.get_type_identifier_in_class(target_class, child, idf_set)
    
    def collect_identifiers(self, node, idf_set):
        if node.type == 'scoped_type_identifier':
            for child in node.children:
                if child.type == 'type_identifier':
                    parent_class = child.text.decode("utf-8", errors='ignore')
                    idf_set.add(parent_class)
                    return
            return
        
        if node.type in {'type_identifier', 'identifier'}:
            parent_class = node.text.decode("utf-8", errors='ignore')
            idf_set.add(parent_class)
            return
        
        for child in node.children:
            self.collect_identifiers(child, idf_set)
        
    def get_import_declaration(self, node):
        import_list = []
        for child in node.children:
            if child.type == 'import_declaration':
                code = child.text.decode("utf8", errors='ignore')
                import_list.append((code.split(' ')[1])[:-1])
        return import_list
        
    def process(self, code, process_type=None, target_class=None):
        code = bytes(code, "utf8", errors='ignore')
        tree = self.parser.parse(code)
        if process_type == "package_declaration":
            return self.get_package_name(tree.root_node)
        if process_type == "identifier":
            idf_set = set()
            self.get_type_identifier_in_class(target_class, tree.root_node, idf_set)
            return list(idf_set)
        elif process_type == "import_declaration":
            return self.get_import_declaration(tree.root_node)
        else:
            return None
    