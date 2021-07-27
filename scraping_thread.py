import math
import threading
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from driver_setting import set_driver
from log_setting import write_log
from write_csv import write_csv

THREAD_COUNT = 5
SEARCH_QUERY_URL = "https://tenshoku.mynavi.jp/list/{query_word}"
PAGE_QUERY_URL = "https://tenshoku.mynavi.jp/list/{query_word}/" + "pg{page_counter}"


class mainavi_scraping:
    def __init__(self, search_words, query_word) -> None:
        self.data_counter = 0
        self.page_count = 0
        self.search_words = search_words
        self.query_word = query_word
        self.df = pd.DataFrame()
        self.lock = threading.RLock()

    def fetch_page_count(self):
        query_url = SEARCH_QUERY_URL.format(query_word=self.query_word)
        driver = set_driver(True)
        driver.get(query_url)
        data_count = int(
            driver.find_element_by_xpath(
                "/html/body/div[1]/div[3]/div[2]/div/p[2]/em"
            ).text
        )
        self.page_count = math.ceil(data_count / 50)
        driver.quit()

    def loop_scraping(self):
        with ThreadPoolExecutor() as executor:
            for page_counter in range(1, self.page_count + 1):
                executor.submit(self.scrape, page_counter=page_counter)
        self.df.sort_index()

    def scrape(self, page_counter):
        with self.lock:
            query_url = PAGE_QUERY_URL.format(
                query_word=self.query_word, page_counter=page_counter
            )
            driver = set_driver(True)
            driver.get(query_url)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            corps_list = driver.find_elements_by_class_name("cassetteRecruit__content")
            for corp in corps_list:
                self.data_counter += 1
                try:
                    self.df = self.df.append(
                        pd.DataFrame(
                            {
                                "会社名": self.fetch_corp_name(corp, "div > section > h3"),
                                "勤務地": self.find_table_target_word(corp, "勤務地"),
                                "給与": self.find_table_target_word(corp, "給与"),
                            },
                            index=[self.data_counter],
                        )
                    )
                    write_log(f"{self.data_counter}件目完了")
                except Exception:
                    pass
                    write_log(f"{self.data_counter}件目失敗")
            driver.quit()

    def fetch_corp_name(self, driver, css_selector):
        try:
            return driver.find_element_by_css_selector(css_selector).text
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
        table_headers = driver.find_elements_by_class_name("tableCondition__head")
        table_bodies = driver.find_elements_by_class_name("tableCondition__body")
        for table_header, table_body in zip(table_headers, table_bodies):
            if table_header.text == target:
                return table_body.text


def main():

    # 検索ワード入力
    search_word = input("検索ワード>>")

    # クエリパラメータの形に整形
    search_words = search_word.split()
    query_words = []
    for word in search_words:
        query_words.append("kw" + word)
    query_word = "_".join(query_words)
    write_log(f"検索ワード：{search_words}")

    # URLクエリパラメータで接続
    my_scraping = mainavi_scraping(search_words, query_word)
    my_scraping.fetch_page_count()
    my_scraping.loop_scraping()
    my_scraping.write_csv()
    print(len(my_scraping.df))
    print(my_scraping.data_counter)


if __name__ == "__main__":
    main()
