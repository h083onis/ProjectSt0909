import re
from io import StringIO
import tokenize

class RemoveComment():
    def __init__(self):
        pass
    
    def remove_comment(self, code, language):
        if language in ['java', 'c', 'cpp', 'h', 'hpp']:
            return self.remove_relative_c_comment(code)
        elif language == 'python':
            return self.remove_python_comment(code)
        else:
            return ValueError(f"Unsupported language: {language}")
        
    def remove_relative_c_comment(self, code):
        # 正規表現を使用してコメントを削除
        pattern = r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"'
        regex = re.compile(pattern, re.DOTALL | re.MULTILINE)
        
        # コメントを空文字に置き換える
        filtered_text = regex.sub(lambda x: '' if x.group(0).startswith(('/', '/*')) else x.group(0), code)
    
        return '\n'.join(line for line in filtered_text.splitlines() if line.strip())
    
    def remove_python_comment(self, code):
        io_obj = StringIO(code)
        out = ""
        prev_toktype = tokenize.INDENT
        last_lineno = -1
        last_col = 0
        for token in tokenize.generate_tokens(io_obj.readline):
            token_type, token_string, (start_line, start_col), (end_line, end_col), _ = token
            
            #インデントなどの位置調整
            #１つ前のトークンと比較して行が変わっているか
            if start_line > last_lineno:
                last_col = 0
            #１つ前のトークンとの位置の差を空白で埋める
            if start_col > last_col:
                out += (" " * (start_col - last_col))
                
            # Remove comments:
            if token_type == tokenize.COMMENT:
                pass
            # This series of conditionals removes docstrings:
            elif token_type == tokenize.STRING:
                if prev_toktype != tokenize.INDENT and prev_toktype != tokenize.NEWLINE and start_col > 0:
                    out += token_string
            else:
                out += token_string
            prev_toktype = token_type
            last_col = end_col
            last_lineno = end_line
                    
        return '\n'.join(line for line in out.split('\n') if line.strip() != '')
        