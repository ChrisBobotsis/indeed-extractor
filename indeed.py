from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup
from bs4.element import Comment

from datetime import datetime

import argparse
import pandas as pd
import numpy as np
import os

import logging

from typing import List
from tqdm import tqdm

from constants import INDEED_BASE_URL

logger = logging.getLogger()

logging.basicConfig(
    level=logging.INFO,
)

fh = logging.FileHandler('indeed.log')

logger.addHandler(fh)

JOB_TITLE = "job_title"

COMPANY = "company"

SALARY_AND_TYPE = "salary_and_job_type"

LOCATION = "location"

DESCRIPTION = "description"

URL = "url"

ID = "id"


class selenium_element(object):

    JOB_LIST = 0


class indeed_extractor(object):

    def __init__(self):

        self.path = os.getcwd()
        self.save_path = os.path.join(
            self.path,
            "data",
        )

        path = os.path.join(
            self.path,
            "data",
            "csv",
        )

        if os.path.exists(path) is False:

            os.makedirs(path)

        path = os.path.join(
            self.path,
            "data",
            "job_ids",
        )

        if os.path.exists(path) is False:

            os.makedirs(path)

    JOB_ITEM = {
        "class": "cardOutline"
    }

    JOB_TITLE = {
        "class": "jobTitle",
    }

    COMPANY = {
        "element": "span",
        "class": "companyName",
    }

    LOCATION = {
        "element": "div",
        "class": "companyLocation",
    }

    JOB_PANE = {
        "element": "div",
        "class": "jobsearch-Rightpane",
    }

    POSTING_URL = {
        "class": "jobTitle"
    }

    def soup_item2text(
        self,
        soup,
        element,
        kwargs,
    ):

        text = soup.find(
            element,
            kwargs,
        ).text.strip()

        return text

    def soup2text(
        self,
        soup,
    ):

        if soup:

            texts = soup.findAll(string=True)
            visible_texts = filter(
                self.tag_visible,
                texts,
            )

            return u" ".join(t.strip() for t in visible_texts)

        return None

    def tag_visible(
        self,
        element,
    ):
        if element.parent.name in [
            'style',
            'script',
            'head',
            'title',
            'meta',
            '[document]',
        ]:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def page_not_found(
        self,
        soup,
    ):

        x = soup.find(PAGE_NOT_FOUND["element"])

        if x is None:

            return False

        for xi in x:

            if (xi.string == PAGE_NOT_FOUND["text"]):

                return True

        return False

    def get_search_url(
        self,
        keywords: List[str],
        location: str,
        radius=None,
        start=None,
    ):

        q = '+'.join(keywords.split())

        url = f"{INDEED_BASE_URL}/jobs?q={q}&l={location}"

        if radius:

            url += f"&radius={radius}"

        if start:

            url += f"&start={start}"

        return url

    def get_job_url(
        self,
        id,
    ):

        return f"{INDEED_BASE_URL}/viewjob?jk={id}"

    def page_soup2job_ids(
        self,
        soup,
    ):

        job_items = soup.findAll(class_="cardOutline")

        ids = [x.find(class_="jobTitle").a["data-jk"] for x in job_items]

        return ids

    def url2soup(
        self,
        url: str,
    ):

        driver = self.get_webdriver(True)

        driver.get(url)

        html = driver.page_source

        driver.close()

        return BeautifulSoup(html, "html.parser")

    def isNext(
        self,
        soup,
    ):

        x = soup.find(
            "a",
            {"aria-label": "Next Page"},
        )

        if x:

            return True

        return False

    def extract_job_data(
        self,
        id_: str,
    ):

        url = self.get_job_url(id_)

        driver = self.get_webdriver(True)

        data = {
            JOB_TITLE: None,
            COMPANY: None,
            SALARY_AND_TYPE: None,
            LOCATION: None,
            DESCRIPTION: None,
            URL: url,
            ID: id_,
        }

        try:

            driver.get(url)

        except TimeoutException as e:

            return data

        soup = BeautifulSoup(
            driver.page_source,
            "html.parser",
        )

        driver.close()

        if self.page_not_found(soup):

            return data

        data[JOB_TITLE] = self.soup2text(
            soup.find(
                JobPosting.JOB_TITLE["element"],
                JobPosting.JOB_TITLE["kwargs"],
            )
        )

        data[COMPANY] = self.soup2text(
            soup.find(
                JobPosting.COMPANY["element"],
                JobPosting.COMPANY["kwargs"],
            )
        )

        data[SALARY_AND_TYPE] = self.soup2text(
            soup.find(
                JobPosting.SALARY_AND_TYPE["element"],
                JobPosting.SALARY_AND_TYPE["kwargs"],
            )
        )

        data[LOCATION] = self.soup2text(
            soup.find(
                JobPosting.LOCATION["element"],
                JobPosting.LOCATION["kwargs"],
            )
        )

        data[DESCRIPTION] = self.soup2text(
            soup.find(
                JobPosting.DESCRIPTION["element"],
                JobPosting.DESCRIPTION["kwargs"],
            )
        )

        data[URL] = url

        data[ID] = id_

        return data

    def download_job_ids(
        self,
        keywords: List[str],
        location,
        radius,
        start,
        file_name,
        max_results,
    ):

        logger.info("Starting job id extraction")

        job_ids = []

        continueSearch = True

        count = 0

        while continueSearch is True:

            # Get url for search
            url = self.get_search_url(
                keywords,
                location,
                radius,
                start,
            )

            # Get Soup
            soup = self.url2soup(url)

            # Extract Each Job ID
            new_ids = self.page_soup2job_ids(soup)

            count += len(new_ids)

            logger.info(f"Extracted {count} ids")

            job_ids.extend(new_ids)

            # Increment start
            start += 10

            if count >= max_results:

                continueSearch = False

            else:

                # Check if there is a next button
                continueSearch = self.isNext(soup)

        logger.info("Writing extracted ids to txt file")

        file_name = os.path.join(
            self.save_path,
            "job_ids",
            f"{file_name}.txt",
        )

        with open(file_name, "w") as f:

            f.write(
                "\n".join(job_ids)
            )

        return

    def download_job_data(
        self,
        file_name: str,
    ):

        logger.info("Starting job description extraction")

        with open(
            os.path.join(
                "data",
                "job_ids",
                file_name,
            ),
            "r"
        ) as f:

            ids = f.read().split("\n")

        data = []

        for id_ in tqdm(ids):

            data.append(
                self.extract_job_data(id_)
            )

        logger.info("Writing job description data to csv")

        df = pd.DataFrame.from_dict(data)

        csv_file = os.path.join(
            self.save_path,
            "csv",
            f"{file_name}.csv",
        )

        df.to_csv(
            csv_file,
            index=False,
        )

    def get_webdriver(
        self,
        headless: bool = True,
    ):

        options = Options()

        if headless is True:

            options.add_argument("-headless")

        driver = webdriver.Firefox(
            options=options,
        )

        return driver

    def download_wrapper(
        self,
        query: str,
        location: str,
        radius: int = 25,
        start: int = 0,
        max_results: float = np.inf,
    ):

        try:

            self.download(
                query,
                location,
                radius,
                start,
                max_results,
            )

        except Exception as e:

            logger.critical(e, exc_info=True)

    def download(
        self,
        query: str,
        location: str,
        radius: int,
        start: int,
        max_results: int,
    ):

        now = str(datetime.now())

        file_name = f"{query}_{location}_{radius}_{start}_{max_results}_{now}"

        logger.info("Downloading Job Ids")

        self.download_job_ids(
            query,
            location,
            radius,
            start,
            file_name,
            max_results,
        )

        logger.info("Downloading Job Data")

        self.download_job_data(
            f"{file_name}.txt",
        )

        logger.info("Cleaning Up")

        self.cleanup(file_name)

        return

    def cleanup(
        self,
        file_name,
    ):

        os.remove(
            os.path.join(
                self.save_path,
                "job_ids",
                f"{file_name}.txt"
            )
        )

        return


class JobPosting(object):

    SALARY_AND_TYPE = {
        "element": "div",
        "kwargs": {
            "id": "salaryInfoAndJobType",
        }
    }

    JOB_TITLE = {
        "element": "h1",
        "kwargs": {
            "class": "jobsearch-JobInfoHeader-title",
        }
    }

    COMPANY = {
        "element": "div",
        "kwargs": {
            "data-testid": "inlineHeader-companyName",
        }
    }

    LOCATION = {
        "element": "div",
        "kwargs": {
            "data-testid": "inlineHeader-companyLocation",
        }
    }

    DESCRIPTION = {
        "element": "div",
        "kwargs": {
            "id": "jobDescriptionText",
        }
    }


class JobPane(object):

    DESCRIPTION = {
        "element": "div",
        "id": "jobDescriptionText",

    }

    BENEFITS = {
        "element": "div",
        "id": "benefits",
    }

    DETAILS = {
        "element": "div",
        "id": "jobDetailsSection",
    }


NEXT_BTN = {
    "element": "a",
    "aria-label": "Next Page",
}

PAGE_NOT_FOUND = {
    "element": "p",
    "text": "The page you requested could not be found.",
}


if __name__ == "__main__":

    indeed_extractor = indeed_extractor()

    parser = argparse.ArgumentParser(
        description="Just an example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    radii = [0, 5, 10, 15, 25, 35, 50, 100]

    parser.add_argument(
        "-q", "--query",
        type=str,
        required=True,
        action="store",
        help="The search query you would like to search indeed for.",
    )

    parser.add_argument(
        "-r", "--radius",
        choices=radii,
        type=int,
        default=25,
        action="store",
        help="The 'within distance' parameter for you search.",
    )

    parser.add_argument(
        "-l", "--location",
        type=str,
        default='',
        action="store",
        help="The location for the search query.",
    )

    parser.add_argument(
        "-m", "--max-results",
        type=int,
        default=np.inf,
        action="store",
        help="The max number of results you would like to be extracted.",
    )

    parser.add_argument(
        "-s", "--start",
        type=int,
        default=0,
        action="store",
        help="The start value for your query.",
    )

    args = parser.parse_args()
    config = vars(args)

    indeed_extractor.download_wrapper(
        config["query"],
        config["location"],
        config["radius"],
        config["start"],
        config["max_results"]
    )

    """download_job_data(
        "software engineer_Canada_50_670_2023-08-14 16:02:32.741044"
    )"""

    """download_job_ids(
        "software engineer",
        "Canada",
    )"""
