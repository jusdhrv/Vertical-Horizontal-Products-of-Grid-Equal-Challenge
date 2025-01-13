import os

def clear_logs():
    logs_path = "Data/logs.txt"
    if os.path.exists(logs_path):
        with open(logs_path, "w") as file:
            file.truncate(0)
        print(f"Cleared contents of {logs_path}")
    else:
        print(f"{logs_path} does not exist")

def delete_memo_data():
    memo_data_path = "Data/memo_data.pkl"
    if os.path.exists(memo_data_path):
        os.remove(memo_data_path)
        print(f"Deleted {memo_data_path}")
    else:
        print(f"{memo_data_path} does not exist")

if __name__ == "__main__":
    clear_logs()
    delete_memo_data()