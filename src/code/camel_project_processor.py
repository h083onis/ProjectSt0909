import argparse
import re
import json
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from pydriller import Repository
from project_abstract import ProjectAbstract



class CamelProjectProcessor(ProjectAbstract):
    def __init__(self, params):
        self.params =  params if isinstance(params, dict) else vars(params)
    
    def get_issue_id_from_commit_msg(self, output='commit_with_issue_id.json'):
        commit_list = []
        
        for commit in Repository(self.params["project_path"]).traverse_commits():
            issue_ids = self.extract_issue_id(commit.msg)
            if issue_ids:
                commit_list.append({
                    "commit_id": commit.hash,
                    "issue_ids": list(issue_ids)
                })
                    
        with open(output, 'w', encoding='utf-8') as json_file:
            json.dump(commit_list, json_file, indent=2)
        
    def extract_issue_id(self, commit_msg):
        issue_pattern = r"\bCAMEL-\d+\b"
        matches = re.findall(issue_pattern, commit_msg)
        return matches

    def scraping_from_its(self, issue_ids_file='commit_with_issue_id.json', output='issue_id_with_type.txt'):
        driver = webdriver.Chrome()
        
        with open(issue_ids_file, 'r', encoding='utf-8') as f:
            commit_with_issue_id = json.load(f)
            
        issue_id_set = {issue_id for commit in commit_with_issue_id if commit.get("issue_ids") for issue_id in commit["issue_ids"]}
            
        url = "https://issues.apache.org/jira/issues/?jql=project%20%3D%20CAMEL%20AND%20issuetype%20%3D%20Bug"
        search_box_id = 'quickSearchInput'
        issue_type_id = 'type-val'
        
        driver.get(url)
        
        with open(output, 'w', encoding='utf-8') as output_file:
            for issue_id in issue_id_set:
                try:
                    search_box = driver.find_element(By.ID, search_box_id)
                    search_box.clear()
                    search_box.send_keys(issue_id)
                    search_box.send_keys(Keys.RETURN)
                    
                    element = driver.find_element(By.ID, issue_type_id)
                    output_file.write(f"{issue_id}\t{element.text}\n")
                except NoSuchElementException:
                    continue
                finally:
                    sleep(1)  # Avoid overwhelming the server
            
        driver.quit()
        
    def get_bug_fix_commits(self, issue_ids_file='commit_with_issue_id.json', issue_id_with_type_file='issue_id_with_type.txt', output='bug_fix_commits.txt'):
        with open(issue_ids_file, 'r', encoding='utf-8') as f_commit, open(issue_id_with_type_file, 'r', encoding='utf-8') as f_type:
            commit_id_with_issue_id = json.load(f_commit)
            bug_fix_issue_id = {line.strip().split('\t')[0] for line in f_type.readlines() if line.strip().split('\t')[-1] == 'Bug'}
        
        bug_fix_commit = set()
        for item in commit_id_with_issue_id:
            if any(issue_id in bug_fix_issue_id for issue_id in item["issue_ids"]):
                bug_fix_commit.add(item["commit_id"])

        with open(output, 'w', encoding='utf-8') as f:
            for commit_id in bug_fix_commit:
                print(commit_id, file=f) 
        
        
def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_path', type=str, default='../../../../sample_data/camel')
    return parser

if __name__ == '__main__':
    params = read_args().parse_args()
    cpp = CamelProjectProcessor(params)
    cpp.get_bug_fix_commits()