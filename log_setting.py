from datetime import datetime
from pathlib import Path

LOG_FILE_PATH = "./log/log_{datetime}.log"
log_file_path = LOG_FILE_PATH.format(
    datetime=datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
)

# logフォルダがない場合は作成
dir = Path("./log")
dir.mkdir(parents=True, exist_ok=True)


def write_log(log_txt):
    now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    log_str = f"[log: {now}]{log_txt}"
    with open(log_file_path, "a") as f:
        f.write(log_str + "\n")
