from pathlib import Path
import subprocess
from importlib import import_module
import time
import sys


message = """
- Ready!
- Open VSCode on your laptop and open the command prompt
- Select: 'Remote-Tunnels: Connect to Tunnel' to connect to colab
""".strip()


def start_tunnel() -> None:
    command = "./code tunnel --accept-server-license-terms --name colab-connect"
    p = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    show_outputs = False
    while True:
        line = p.stdout.readline().decode("utf-8")
        if show_outputs:
            print(line.strip())
        if "To grant access to the server" in line:
            print(line.strip())
        if "Open this link" in line:
            print("Starting the tunnel")
            time.sleep(5)
            print(message)
            print("Logs:")
            show_outputs = True
            line = ""
        if line == "" and p.poll() is not None:
            break
    return None

def login_tunnel(provider: str) -> None:
    command = f"./code tunnel user login --provider {provider}"
    p = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    while True:
        line = p.stdout.readline().decode("utf-8")
        if line == "" and p.poll() is not None:
            break
        print(line.strip())
    return None

def run(command: str) -> None:
    process = subprocess.run(command.split())
    if process.returncode == 0:
        print(f"Ran: {command}")

def is_colab():
    return 'google.colab' in sys.modules

def colabconnect(provider: str = "github") -> None:
    if is_colab():
        print("Mounting Google Drive...")
        drive = import_module("google.colab.drive")
        drive.mount("/content/drive")
    
        # Create a folder on drive to store all the code files
        drive_folder = '/content/drive/MyDrive/colab/'
        Path(drive_folder).mkdir(parents=True, exist_ok=True)
    
        # Make a /colab path to easily access the folder
        run(f'ln -s {drive_folder} /')

    print("Installing python libraries...")
    run("pip3 install --user flake8 black ipywidgets twine")
    run("pip3 install -U ipykernel")
    run("apt install htop -y")

    print("Installing vscode-cli...")
    run(
        "curl -Lk https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-x64 --output vscode_cli.tar.gz"
    )
    run("tar -xf vscode_cli.tar.gz")

    print("Starting the tunnel")
    if provider != 'github':
        login_tunnel(provider)
    start_tunnel()
