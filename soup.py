import math
from concurrent.futures.thread import ThreadPoolExecutor

import pandas as pd
import requests
from bs4 import BeautifulSoup

from log_setting import log_setting
from write_csv import write_csv

THREAD_COUNT = None  # スレッド数Noneで自動
SEARCH_QUERY_URL = "https://tenshoku.mynavi.jp/list/{query_word}"
PAGE_QUERY_URL = "https://tenshoku.mynavi.jp/list/{query_word}/" + "pg{page_counter}"
log = log_setting()


class mainavi_scraping:
    def __init__(self, search_word: str) -> None:
        self.search_words: str
        self.query_word: str
        self.df = pd.DataFrame()
        self.df_list = []
        self.search_word_formating(search_word)

    def search_word_formating(self, search_word):
        # クエリパラメータの形に整形
        self.search_words = search_word.split()
        query_words = []
        for word in self.search_words:
            query_words.append("kw" + word)
        self.query_word = "_".join(query_words)
        log.info(f"検索ワード：{self.search_words}")

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

    def scraping(self):
        with ThreadPoolExecutor() as executor:
            for page_counter in range(self.page_count):
                executor.submit(self.fetch_scraping_data, page_counter + 1)
        for df_data in self.df_list:
            self.df = self.df.append(df_data, ignore_index=True)
        self.df = self.df.sort_values(["page", "index"])

    def fetch_scraping_data(self, page_counter):
        query_url = PAGE_QUERY_URL.format(
            query_word=self.query_word, page_counter=page_counter
        )
        resp = requests.get(query_url, timeout=(3.0, 7.5))
        soup = BeautifulSoup(resp.text, "html.parser")
        corps_list = soup.select(".cassetteRecruit__content")
        data_counter = 0
        for corp in corps_list:
            data_counter += 1
            self.df_list.append(
                {
                    "page": page_counter,
                    "index": data_counter,
                    "会社名": self.fetch_corp_name(corp, "div > section > h3"),
                    "勤務地": self.find_table_target_word(corp, "勤務地"),
                    "給与": self.find_table_target_word(corp, "給与"),
                }
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
            log.info(f"{len(self.df)}件出力しました。")
        else:
            log.info(f"{len(self.df)}件です。")

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
    my_scraping = mainavi_scraping(search_word)
    my_scraping.fetch_page_count()
    my_scraping.scraping()
    my_scraping.write_csv()


if __name__ == "__main__":
    main()
