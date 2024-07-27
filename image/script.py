import subprocess
from datetime import datetime 
import platform

exe_path = "./TABG.exe"
if platform.system().lower() == 'windows':
    exe_path = ".\\TABG.exe"

# Run the .exe and capture the output
process = subprocess.Popen([exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


# Continuously read the output line by line
try:
    with open(f"log{datetime.now().strftime('%Y%m%d%H%M%S')}.txt", "w") as file:
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip())
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