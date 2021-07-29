import math
from concurrent.futures.thread import ThreadPoolExecutor

import pandas as pd
import requests
from bs4 import BeautifulSoup

from log_setting import write_log
from write_csv import write_csv

THREAD_COUNT = 2  # スレッド数Noneで自動
SEARCH_QUERY_URL = "https://tenshoku.mynavi.jp/list/{query_word}"
PAGE_QUERY_URL = "https://tenshoku.mynavi.jp/list/{query_word}/" + "pg{page_counter}"


class mainavi_scraping:
    def __init__(self, search_word: str) -> None:
        self.search_words: list = search_word.split()
        self.query_word: str
        self.page_count: int = 0
        self.df = pd.DataFrame()
        self.fetch_query_word()

    def fetch_query_word(self):
        query_words = []
        for word in self.search_words:
            query_words.append("kw" + word)
        self.query_word = "_".join(query_words)

    def fetch_page_count(self):
        query_url = SEARCH_QUERY_URL.format(query_word=self.query_word)
        resp = requests.get(query_url, timeout=(3.0, 7.5))
        soup = BeautifulSoup(resp.text, "html.parser")
        data_count = int(
            soup.select_one(
                "body > div.wrapper > div:nth-child(5) > "
                + "div.result > div > p.result__num > em"
            ).text
        )
        self.page_count = math.ceil(data_count / 50)

    def scrape(self, page_counter):
        query_url = PAGE_QUERY_URL.format(
            query_word=self.query_word, page_counter=page_counter
        )
        resp = requests.get(query_url, timeout=(3.0, 7.5))
        soup = BeautifulSoup(resp.text, "html.parser")
        corps_list = soup.select(".cassetteRecruit__content")

        data_counter = 0
        for corp in corps_list:
            data_counter += 1
            self.df = self.df.append(
                {
                    "page": str(page_counter),
                    "index": str(data_counter),
                    "会社名": self.fetch_corp_name(corp, "div > section > h3"),
                    "勤務地": self.find_table_target_word(corp, "勤務地"),
                    "給与": self.find_table_target_word(corp, "給与"),
                },
                ignore_index=True,
            )

    def fetch_corp_name(self, driver, css_selector):
        try:
            return driver.select_one(css_selector).text
        except Exception:
            pass

    def write_csv(self):
        # CSVに書き込み
        if len(self.df) > 0:
            write_csv("_".join(self.search_words), self.df)
            write_log(f"{len(self.df)}件出力しました。")
        else:
            write_log(f"{len(self.df)}件です。")

    # テーブルからヘッダーで指定した内容を取得
    def find_table_target_word(self, driver, target):
        table_headers = driver.select(".tableCondition__head")
        table_bodies = driver.select(".tableCondition__body")
        for table_header, table_body in zip(table_headers, table_bodies):
            if table_header.text == target:
                return table_body.text


def main():

    # 検索ワード入力
    search_word = input("検索ワード>>")

    # URLクエリパラメータで接続
    my_scraping = mainavi_scraping(search_word)
    my_scraping.fetch_page_count()
    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        for page_counter in range(1, my_scraping.page_count + 1):
            executor.submit(my_scraping.scrape, page_counter)
    my_scraping.df.sort_values(["page", "index"])
    my_scraping.write_csv()
    print(len(my_scraping.df))


if __name__ == "__main__":
    main()
