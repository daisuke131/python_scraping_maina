from pathlib import Path
from time import sleep

import pandas as pd

from driver_setting import set_driver
from log_setting import write_log


def main():

    # 検索ワード入力
    search_word = input("検索ワード>>")

    # kw~~~_kw~~~に整形
    search_words = search_word.split()
    query_words = []
    for word in search_words:
        query_words.append("kw" + word)
    query_word = "_".join(query_words)
    write_log(f"検索ワード：{search_words}\n")

    # URLクエリパラメータで接続
    query_url = "https://tenshoku.mynavi.jp/list/" + query_word
    driver = set_driver(True)
    driver.get(query_url)
    sleep(3)

    try:
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
        sleep(5)
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
    except Exception:
        pass

    df = pd.DataFrame()

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        corps_list = driver.find_elements_by_class_name("cassetteRecruit__content")
        for corp in corps_list:
            df = df.append(
                {
                    "会社名": fetch_corp_data(corp, "会社名", "div > section > h3"),
                    "勤務地": fetch_corp_data(
                        corp, "勤務地", "table > tbody > tr:nth-child(3) > td"
                    ),
                    "給与": fetch_corp_data(
                        corp, "給与", "table > tbody > tr:nth-child(4) > td"
                    ),
                },
                ignore_index=True,
            )
            write_log(f"{len(df)}件読み込み完了\n")

        # 次のページへ
        try:
            driver.find_element_by_class_name("iconFont--arrowLeft").click()
            sleep(1)
        except Exception:
            break

    # CSVに書き込み
    if len(df) > 0:
        write_csv("_".join(search_words), df)
        write_log(f"{len(df)}件出力しました。\n")
    else:
        write_log(f"{len(df)}件です。\n")

    # ブラウザ閉じる
    driver.quit()


# CSV書き込み
def write_csv(search_word, df):
    # ディレクトリがないとエラーになるため作成
    dir = Path("./csv")
    dir.mkdir(parents=True, exist_ok=True)

    # csvファイル名に検索ワードを加える。
    csv_path = f"./csv/{search_word}_data.csv"
    # 行番号なしで出力
    df.to_csv(csv_path, index=False, encoding="CP932")


# データ取得できない場合はスルー
def fetch_corp_data(driver, data_name, css_selector):
    try:
        return driver.find_element_by_css_selector(css_selector).text
    except Exception:
        write_log(f"{data_name}が取得できませんでした。")
        pass


if __name__ == "__main__":
    main()
