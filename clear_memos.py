import os


def delete_memo_data():
    memo_data_path = "Data/memo_data.pkl"
    if os.path.exists(memo_data_path):
        os.remove(memo_data_path)
        print(f"Deleted {memo_data_path}")
    else:
        print(f"No memos to delete")


if __name__ == "__main__":
    delete_memo_data()
