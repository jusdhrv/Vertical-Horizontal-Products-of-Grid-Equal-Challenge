import os
from os import listdir, path, remove


def clear_logs():
    existing_logs = [f for f in listdir("Data") if f.endswith("-logs.txt")]
    if existing_logs:
        for log_file in existing_logs:
            log_file_path = f"Data/{log_file}"
            remove(log_file_path)
            print(f"Deleted {log_file_path}")
        print(f"Cleared contents of logs")
    else:
        print(f"No logs to delete")

def clear_outputs():
    """Delete all session output files in the Data/ folder."""
    output_dir = "Data"
    if not path.exists(output_dir):
        print("| Data directory does not exist.")
        return
    deleted = 0
    for f in listdir(output_dir):
        if f.startswith("session_") and f.endswith("-output.json"):
            remove(path.join(output_dir, f))
            deleted += 1
    print(f"| Deleted {deleted} session output files.")


if __name__ == "__main__":
    clear_logs()
    clear_outputs()
