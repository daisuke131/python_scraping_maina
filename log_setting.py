import logging
import logging.handlers
from datetime import datetime
from pathlib import Path


def log_setting():
    dir = Path("./log")
    dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    log = logging.getLogger(__name__)
    # ログ出力レベルの設定
    log.setLevel(logging.INFO)

    # ローテーティングファイルハンドラを作成
    rh = logging.handlers.RotatingFileHandler(f"./log/{now}.log", encoding="utf-8-sig")

    # ロガーに追加
    log.addHandler(rh)
    return log
