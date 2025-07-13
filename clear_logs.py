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

def clear_outputs():
    existing_outputs = [f for f in os.listdir("Data") if f.endswith("-output.json")]
    if existing_outputs:
        for output_file in existing_outputs:
            output_file_path = f"Data/{output_file}"
            os.remove(output_file_path)
            print(f"Deleted {output_file_path}")
        print(f"Cleared contents of outputs")
    else:
        print(f"No outputs to delete")


if __name__ == "__main__":
    clear_logs()
    clear_outputs()
