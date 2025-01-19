from abc import ABC, abstractmethod
from typing import List


class ProjectAbstract(ABC):
    @abstractmethod
    def get_issue_id_from_commit_msg(self, output: str = 'commit_with_issue_id.json') -> None:
        """
        Extract issue IDs from commit messages and save the result to a file.

        :param output: The output file where the commit data will be saved in JSON format.
        """
        pass
    
    @abstractmethod
    def extract_issue_id(self, commit_msg: str) -> List[str]:
        """
        Extract issue IDs from a given commit message.

        :param commit_msg: The commit message from which to extract issue IDs.
        :return: A list of issue IDs extracted from the commit message.
        """
        pass
    
    @abstractmethod
    def scraping_from_its(self, issue_ids_file: str = 'commit_with_issue_ids.json', output: str = 'issue_id_with_type.txt') -> None:
        """
        Scrape data from the issue tracking system using issue IDs and save the results.

        :param issue_ids_file: The input file containing the issue IDs to search.
        :param output: The output file where the scraped data will be saved.
        """
        pass
