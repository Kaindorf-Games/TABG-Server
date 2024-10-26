import subprocess
from datetime import datetime 
import platform
from manager import Manager

def main():
    exe_path = "./TABG.exe"
    if platform.system().lower() == 'windows':
        exe_path = ".\\TABG.exe"

    # Run the .exe and capture the output
    process = subprocess.Popen([exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    manager = Manager()
    # Continuously read the output line by line
    try:
        with open(f"logs/log{datetime.now().strftime('%Y%m%d%H%M%S')}.txt", "w") as file:
            print("Started Server!")
            while True:
                output = process.stdout.readline()
                if output:
                    # print(output.strip())
                    # manager.feed_line(output)
                    file.write(output)
        
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