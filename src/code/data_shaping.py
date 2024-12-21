import pandas as pd
import json
import argparse
import time

class DataShaping():
    def __init__(self, params):
        self.params =  params if isinstance(params, dict) else vars(params)
        label_df = pd.read_csv(self.params["label_csv_path"])
        self.commit_label_dict = label_df.set_index('commit_hash')['contains_bug'].to_dict()
    
    def excute(self):
        st = time.time()
        commit_ids = []
        changed_src_files = []
        test_file_hierarchy_depth = []
        is_test_file_changed_with_code = []
        is_bug_commit = []
        
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
                
                num_added_record = self.analyze_commit(
                    data,
                    changed_src_files,
                    test_file_hierarchy_depth,
                    is_test_file_changed_with_code,
                )
                if num_added_record > 0:
                    commit_ids.extend([data["commit_id"]] * num_added_record)
                    is_bug_commit.extend([self.commit_label_dict[data['commit_id']]] * num_added_record)
        
        # データフレームに変換
        shaped_df = pd.DataFrame(
            data={
                "commit_id": commit_ids,
                "changed_src_files": changed_src_files,
                "test_file_hierarchy_depth": test_file_hierarchy_depth,
                "is_test_file_changed_with_code": is_test_file_changed_with_code,
                "is_bug_commit": is_bug_commit
            }
        )

        # 出力ファイルに保存
        shaped_df.to_csv(self.params["output_csv_path"], index=False)
        en = time.time()
        print(f"processed in {str(en-st):.4f} seconds.")
        
    def analyze_commit(
        self,
        data,
        changed_src_files,
        test_file_hierarchy_depth,
        is_test_file_changed_with_code,
    ):
        num_added_record = 0
        changed_files_dict = {ch_file["source_path"]:ch_file["test_file"] for ch_file in data["changed_files"]}
        for src_path, test_file in changed_files_dict.items():
            #テストコードは製品コードではないため除外
            if "Test" in src_path:
                continue
            
            #変更されたファイル
            changed_src_files.append(src_path)
            
            #テストファイルの深さ, テストファイルが一緒に変更されているか
            depth_min = float('inf')
            is_test_file_changed = float('inf')

            # 空のリストはFalse判定
            if test_file:
                for test in test_file:
                    depth_min = min(depth_min, test["depth"])
                    if test["test_path"] in changed_files_dict.keys():
                        is_test_file_changed = min(is_test_file_changed, test["depth"])
            
            depth_min = depth_min if depth_min != float('inf') else None
            is_test_file_changed = is_test_file_changed if is_test_file_changed != float('inf') else None
                
            test_file_hierarchy_depth.append(depth_min)
            is_test_file_changed_with_code.append(is_test_file_changed)
            
            # 追加レコード数
            num_added_record += 1
            
        return num_added_record
        
def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, default='../resource/camel3.txt')
    parser.add_argument('--output_csv_path', type=str, default='shaped_data.csv')
    parser.add_argument('--label_csv_path', type=str, default='../../../../sample_data/label_dataset/data/camel.csv')
    return parser
        
if __name__ == '__main__':
    params = read_args().parse_args()
    ds = DataShaping(params)
    ds.excute()