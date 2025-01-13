import os


def clear_logs():
    existing_logs = [f for f in os.listdir("Data") if f.endswith("-logs.txt")]
    if existing_logs:
        for log_file in existing_logs:
            log_file_path = f"Data/{log_file}"
            os.remove(log_file_path)
            print(f"Deleted {log_file_path}")
        print(f"Cleared contents of logs")
    else:
        print(f"No logs to delete")


if __name__ == "__main__":
    clear_logs()
