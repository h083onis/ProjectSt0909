from enum import Enum

class State(Enum):
    NORMAL = 1
    DOUBLE = 2
    SINGLE = 3

def replace_double_quote(text):
    result = []
    state = State.NORMAL
    escape = False  # エスケープ状態を追跡
    
    for ch in text:
        if state == State.DOUBLE:
            if not escape and ch == '"':  # ダブルクォート終了
                state = State.NORMAL
            result.append(ch)
            escape = (ch == '\\')  # バックスラッシュでエスケープを切り替え
            continue

        if state == State.SINGLE:
            if not escape and ch == "'":  # シングルクォート終了
                state = State.NORMAL
                result.append('"')  # ダブルクォートに置換
                continue
            if ch == '"':  # シングルクォート内のダブルクォートをエスケープ
                result.append("\\")
            result.append(ch)
            escape = (ch == '\\')
            continue

        if ch == '"':  # ダブルクォート開始
            state = State.DOUBLE
        elif ch == "'":  # シングルクォート開始
            state = State.SINGLE
            ch = '"'  # ダブルクォートに置換
        result.append(ch)
        escape = (ch == '\\')
    
    return ''.join(result)

        
if __name__ == '__main__':
    text = """{'commit_id': 'c7b040de15003f63fa1b32ab7ccb283032ac1890', 'timestamp': 1572593668, 'commit_author': "Timo 'Timii' Paananen", 'changed_files': [{'source_path': 'components/camel-cxf/src/test/java/org/apache/camel/component/cxf/CxfComponentEnableMtomTest.java', 'fqcn': 'org.apache.camel.component.cxf.CxfComponentEnableMtomTest', 'test_file': []}]}"""
    # text = """{'commit_id': '872ff668e32620d4026e17835a1cc4a931a316a9', 'timestamp': 1574495531, 'commit_author': 'Claus ""Ibsen', 'changed_files': [{'source_path': 'components/camel-hdfs/src/test/java/org/apache/camel/component/hdfs/HdfsConsumerTest.java', 'fqcn': 'org.apache.camel.component.hdfs.HdfsConsumerTest', 'test_file': []}]}"""
    replaced_text = replace_double_quote(text)
    import json
    print(replaced_text)
    print(json.loads(replaced_text))