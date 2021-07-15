import os
import random

from dotenv import load_dotenv
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.utils import ChromeType


def set_driver(headless_flg):
    # 使用ブラウザの管理は.envで行う
    load_dotenv()
    # firefox or chromium指定以外はchromeで起動
    browser_name = os.getenv("BROWSER")
    if "firefox" in browser_name:
        options = webdriver.FirefoxOptions()
    else:
        options = webdriver.ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg is True:
        options.add_argument("--headless")
    # UA情報ランダム
    user_agent = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) "
        + "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) "
        + "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15",
    ]
    user_agent_random = user_agent[random.randrange(0, len(user_agent), 1)]
    options.add_argument("--user-agent=" + user_agent_random)
    # その他、起動オプションの設定
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--incognito")

    if "firefox" in browser_name:
        return webdriver.Firefox(
            executable_path=GeckoDriverManager().install(), options=options
        )
    elif "chromium" in browser_name:
        return webdriver.Chrome(
            ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(),
            options=options,
        )
    else:
        return webdriver.Chrome(ChromeDriverManager().install(), options=options)
