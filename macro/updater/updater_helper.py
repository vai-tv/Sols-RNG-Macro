import shutil
import subprocess
import sys
import time

def main():
    if len(sys.argv) < 3:
        sys.exit(1)

    target_path = sys.argv[1]    # -> local main.py
    new_file_path = sys.argv[2]  # -> downloaded temporary file

    time.sleep(2)

    try:
        # overwrite the old main file with the new one
        shutil.copy2(new_file_path, target_path)
        print("Update applied successfully!")

        # restart the launcher
        subprocess.Popen([sys.executable, "launcher.py"])
    except Exception as e:
        print(f"Failed to apply update: {e}")

if __name__ == "__main__":
    main()