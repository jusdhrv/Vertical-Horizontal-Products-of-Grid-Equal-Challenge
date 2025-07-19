import os


def clear_workers():
    existing_workers = [f for f in os.listdir("Data/Workers") if f.startswith("worker_")]
    if existing_workers:
        for worker_file in existing_workers:
            worker_file_path = f"Data/Workers/{worker_file}"
            os.remove(worker_file_path)
            print(f"Deleted {worker_file_path}")
        print(f"Cleared contents of workers")
    else:
        print(f"No workers to delete")


if __name__ == "__main__":
    clear_workers()
