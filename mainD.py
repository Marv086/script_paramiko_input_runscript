import paramiko
import logging
import time
from getpass import getpass
import datetime

# Set up logging to save logs in a new file for each script run
log_filename = time.strftime("main_%Y%m%d_%H%M%S.log")
logging.basicConfig(
    level=logging.DEBUG,  # Log detailed information
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),  # Save logs to a file
        logging.StreamHandler()  # Also print logs to the console
    ]
)

logger = logging.getLogger(__name__)

def execute_command(client, command, sudo_password):
    logger.debug("Executing command: %s", command)
    stdin, stdout, stderr = client.exec_command(f'sudo -S {command}\n')

    # Pass the sudo password
    stdin.write(sudo_password + '\n')
    stdin.flush()

    # Read stdout and stderr in real-time, line-by-line
    while not stdout.channel.exit_status_ready():
        # Read stdout and log it
        line = stdout.readline()
        if line:
            logger.info(line.strip())
            print(line.strip())  # Optional, for real-time console output

    # Check if there's any error output
    error_output = stderr.read().decode()
    if error_output:
        logger.error("Error output:\n%s", error_output)
        print(error_output)  # Optional, for real-time console output

def main():
    ssh_host = '192.168.4.128'
    ssh_user = 'maximus'
    
    while True:
        ssh_password = getpass("Ingrese la contraseña SSH: ")
        try:
            logger.debug("Attempting to connect via SSH to %s", ssh_host)
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ssh_host, username=ssh_user, password=ssh_password)
            logger.info("SSH connection established with %s", ssh_host)
            break
        except paramiko.AuthenticationException:
            logger.error("Contraseña SSH incorrecta.")
            print("Contraseña SSH incorrecta. Intente de nuevo.")

    while True:
        sudo_password = getpass("Ingrese la contraseña sudo: ")
        stdin, stdout, stderr = client.exec_command('sudo -k -l')
        stdin.write(sudo_password + '\n')
        stdin.flush()
        
        if "may not run" not in stderr.read().decode():
            logger.info("Sudo password accepted.")
            break
        else:
            logger.error("Contraseña sudo incorrecta.")
            print("Contraseña sudo incorrecta. Intente de nuevo.")

    mongo_user = input("Ingrese el usuario de MongoDB: ")
    mongo_password = input("Ingrese la contraseña de MongoDB: ")
    cluster = input("Ingrese el cluster: ")
    db_name = input("Ingrese el nombre de la base de datos: ")
    collection_name = input("Ingrese el nombre de la colección: ")
    pr_number = input("Ingrese el número del PR: ")
    script_name = input("Ingrese el nombre del script: ")

    current_date = datetime.datetime.now().strftime("%d%m%Y")
    path = f"/data/bkup/global/dev/"

    commands = [
        f'cd {path}',
        f'mongodump --uri mongodb+srv://{mongo_user}:{mongo_password}@{cluster}/{db_name} '
        f'-c {collection_name} --gzip -o bkup_PR-{pr_number}-{script_name}_{current_date}'
    ]

    # Execute commands with real-time output
    for command in commands:
        execute_command(client, command, sudo_password)

    client.close()
    logger.info("SSH connection closed.")

if __name__ == "__main__":
    main()
