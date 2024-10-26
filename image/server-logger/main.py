import subprocess
from datetime import datetime 
import platform
from manager import Manager
import os


def write_to_file(file, manager, line: str):
    file.write(line)
    
def write_to_logs(file, manager,  line: str):
    print(line.strip())

def write_to_manager(file, manager: Manager,  line: str):
    manager.feed_line(line)

def main():
    exe_path = "./TABG.exe"
    if platform.system().lower() == 'windows':
        exe_path = ".\\TABG.exe"

    # Run the .exe and capture the output
    process = subprocess.Popen([exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    manager = Manager()
    
    write_options = []
    if os.getenv("WRITE_TO_LOGS", 1) == "1":
        write_options.append(write_to_logs)
    if os.getenv("WRITE_TO_FILE", 0) == "1":
        write_options.append(write_to_file)
    if os.getenv("FEED_TO_MANAGER", 0) == "1":
        write_options.append(write_to_manager)
    # Continuously read the output line by line
    try:
        with open(f"logs/log{datetime.now().strftime('%Y%m%d%H%M%S')}.txt", "w") as file:
            print("Started Server!")
            while True:
                output = process.stdout.readline()
                if output:
                    for o in write_options:
                        o(file, manager, output)
        
        # Read the remaining output
        stderr = process.communicate()[1]
        if stderr:
            print("Standard Error:")
            print(stderr.strip())

    except KeyboardInterrupt:
        print("Process interrupted")
    finally:
        process.terminate()
    
if __name__ == "__main__":
    main()