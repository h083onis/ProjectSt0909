import re
import tokenize
from io import StringIO


class RemoveComment:
    """コード内のコメントを削除するユーティリティクラス"""
    
    def __init__(self):
        # サポートする言語一覧
        self.supported_languages = {'java', 'c', 'cpp', 'h', 'hpp', 'python'}
    
    def remove_comment(self, code, language):
        """
        指定された言語に基づき、コードからコメントを削除
        Args:
            code (str): コメントを削除する対象のコード
            language (str): コードのプログラミング言語
        Returns:
            str: コメントを削除したコード
        """
        if language not in self.supported_languages:
            raise ValueError(f"Unsupported language: {language}")
        
        if language in {'java', 'c', 'cpp', 'h', 'hpp'}:
            return self._remove_c_like_comment(code)
        elif language == 'python':
            return self._remove_python_comment(code)
    
    def _remove_c_like_comment(self, code):
        """
        C系言語のコードからコメントを削除
        Args:
            code (str): 対象のコード
        Returns:
            str: コメントを削除したコード
        """
        pattern = r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"'
        regex = re.compile(pattern, re.DOTALL | re.MULTILINE)
        
        # コメント部分を削除してクリーンなコードを生成
        def replacer(match):
            group = match.group(0)
            return '' if group.startswith(('/', '/*')) else group
        
        filtered_text = regex.sub(replacer, code)
        return self._remove_empty_lines(filtered_text)
    
    def _remove_python_comment(self, code):
        """
        Pythonコードからコメントを削除
        Args:
            code (str): 対象のコード
        Returns:
            str: コメントを削除したコード
        """
        io_obj = StringIO(code)
        output = []
        prev_toktype = tokenize.INDENT
        last_lineno = -1
        last_col = 0

        for token in tokenize.generate_tokens(io_obj.readline):
            token_type, token_string, (start_line, start_col), (end_line, end_col), _ = token

            if start_line > last_lineno:
                last_col = 0
            if start_col > last_col:
                output.append(" " * (start_col - last_col))
            
            if token_type == tokenize.COMMENT:
                continue
            elif token_type == tokenize.STRING:
                if prev_toktype not in {tokenize.INDENT, tokenize.NEWLINE} and start_col > 0:
                    output.append(token_string)
            else:
                output.append(token_string)
            
            prev_toktype = token_type
            last_col = end_col
            last_lineno = end_line
        
        return self._remove_empty_lines("".join(output))
    
    @staticmethod
    def _remove_empty_lines(code):
        """
        空行を削除
        Args:
            code (str): 対象のコード
        Returns:
            str: 空行を削除したコード
        """
        return "\n".join(line for line in code.splitlines() if line.strip())
