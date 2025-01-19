from radon.complexity import cc_visit
from radon.metrics import analyze
from radon.metrics import mi_visit
import argparse
from git import Repo
import pandas as pd
import lizard

class MetricsCalculater():
    def __init__(self, params):
        self.params =  params if isinstance(params, dict) else vars(params)
        self.df = pd.read_csv(self.params["data_path"]) 
        self.project_repo = Repo(self.params["project_path"])
        
    def excute(self):
        complexities = []
        llocs = []

        for idx, row in self.df.iterrows():
            try:
                # Gitリポジトリからコードを取得
                code = self.project_repo.git.show(f"{row['commit_id']}:{row['changed_src_files']}")
                
                # Lizardでコードを解析
                analysis_result = lizard.analyze_file.analyze_source_code(row["changed_src_files"], code)
                
                # サイクロマティック複雑度とNLOCを集計
                total_complexity = sum(func.cyclomatic_complexity for func in analysis_result.function_list)
                total_lloc = sum(func.nloc for func in analysis_result.function_list)

                complexities.append(total_complexity)
                llocs.append(total_lloc)
            except Exception as e:
                print(f"Error analyzing file {row['changed_src_files']}: {e}")
                complexities.append(None)
                llocs.append(None)

        # DataFrameに結果を追加
        self.df["complexity"] = complexities
        self.df["lloc"] = llocs
        self.df.to_csv(self.params["out_path"], index=False)

        
def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, default='../resource/result2/shaped_data.csv')
    parser.add_argument('--project_path', type=str, default='../../../../sample_data/camel')
    parser.add_argument('--out_path', type=str, default='data_with_metrics.csv')
    return parser

if __name__ == '__main__':
    params = read_args().parse_args()
    mc = MetricsCalculater(params)
    mc.excute()