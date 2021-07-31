from time import sleep

import pandas as pd

from common.driver import set_driver
from log_setting import write_log
from write_csv import write_csv


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
    query_url = "https://tenshoku.mynavi.jp/list/" + query_word
    driver = set_driver(True)
    driver.get(query_url)
    sleep(3)

    df = pd.DataFrame()

    while True:
        corps_list = driver.find_elements_by_class_name("cassetteRecruit__content")
        for corp in corps_list:
            try:
                df = df.append(
                    {
                        "会社名": fetch_corp_name(corp, "div > section > h3"),
                        "勤務地": find_table_target_word(corp, "勤務地"),
                        "給与": find_table_target_word(corp, "給与"),
                    },
                    ignore_index=True,
                )
                write_log(f"{len(df)}件目完了")
            except Exception:
                write_log(f"{len(df)}件目失敗")

        # 次のページへ
        next_page_links = driver.find_elements_by_class_name("iconFont--arrowLeft")
        if len(next_page_links) > 0:
            next_page_link = next_page_links[0].get_attribute("href")
            driver.get(next_page_link)
        else:
            break

    # CSVに書き込み
    if len(df) > 0:
        write_csv("_".join(search_words), df)
        sleep(5)
        write_log(f"{len(df)}件出力しました。")
    else:
        write_log(f"{len(df)}件です。")

    # ブラウザ閉じる
    driver.quit()


# データ取得できない場合はスルー
def fetch_corp_name(driver, css_selector):
    try:
        return driver.find_element_by_css_selector(css_selector).text
    except Exception:
        pass


# テーブルからヘッダーで指定した内容を取得
def find_table_target_word(driver, target):
    table_headers = driver.find_elements_by_class_name("tableCondition__head")
    table_bodies = driver.find_elements_by_class_name("tableCondition__body")
    for table_header, table_body in zip(table_headers, table_bodies):
        if table_header.text == target:
            return table_body.text


if __name__ == "__main__":
    main()
