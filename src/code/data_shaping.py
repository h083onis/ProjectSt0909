import pandas as pd
import json
import argparse
import time

class DataShaping():
    def __init__(self, params):
        self.params =  params if isinstance(params, dict) else vars(params)
    
    def excute(self):
        st = time.time()
        commit_ids = []
        src_paths = []
        categories = []
        
        with open(self.params["changed_src_paths"], 'r', encoding='utf-8') as f:
            changed_src_paths = {data["commit_id"]:data["changed_files"] for data in json.load(f)}
                    
        with open(self.params["data_path"]) as f:
            while True:
                tmp = f.readline().strip()
                if tmp == '':
                    break
                try:
                    data = json.loads(tmp)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
                    continue
                
                if data["commit_id"] not in changed_src_paths.keys():
                    continue
                
                num_added_record = self.analyze_commit(
                    data,
                    src_paths,
                    categories,
                    set(changed_src_paths[data["commit_id"]])
                )
                if num_added_record > 0:
                    commit_ids.extend([data["commit_id"]] * num_added_record)
        
        # データフレームに変換
        shaped_df = pd.DataFrame(
            data={
                "commit_id": commit_ids,
                "changed_src_files": src_paths,
                "categories": categories,
            }
        )

        # 出力ファイルに保存
        shaped_df.to_csv(self.params["output_csv_path"], index=False)
        en = time.time()
        print(f"processed in {str(en-st):.4f} seconds.")
        
    def analyze_commit(
        self,
        data,
        src_paths,
        categories,
        changed_src_paths
    ):
        num_added_record = 0
        changed_files_dict = {ch_file["source_path"]:ch_file["test_file"] for ch_file in data["changed_files"]}
        for src_path, test_file in changed_files_dict.items():
            #テストコードは製品コードではないため除外
            if "Test" in src_path or \
                "/test/" in src_path or \
                src_path not in changed_src_paths:
                continue
            
            #変更されたファイル
            src_paths.append(src_path)

            # 空のリストはFalse判定
            if test_file:
                num_direct_test_file = 0
                num_changed_test_files = 0
                
                for test in test_file:
                    if test["depth"] > 1:
                        continue
                    if test["test_path"] in changed_files_dict.keys():
                        num_changed_test_files += 1
                    num_direct_test_file += 1
                if num_direct_test_file == num_changed_test_files:
                    categories.append(4)
                elif num_changed_test_files > 0:
                    categories.append(3)
                elif num_direct_test_file > 0:
                    categories.append(2)
                else:
                    categories.append(1)
            else:
                categories.append(1)
            
            # 追加レコード数
            num_added_record += 1
            
        return num_added_record
        
def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, default='../resource/camel3.txt')
    parser.add_argument('--output_csv_path', type=str, default='shaped_data.csv')
    parser.add_argument('--changed_src_paths', type=str, default='../resource/changed_src_paths.json')
    return parser
        
if __name__ == '__main__':
    params = read_args().parse_args()
    ds = DataShaping(params)
    ds.excute()