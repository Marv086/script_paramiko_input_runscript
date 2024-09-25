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

# Function to prompt user for selection: global or regional
def global_or_regional():
    valid_parameters = ['global', 'regional']
    while True:
        print("1. Global\n2. Regional")
        user_input = input("Seleccione una opción (1 o 2): ").strip()
        
        if user_input == '1':
            logger.info("User selected: global")
            return 'global'
        elif user_input == '2':
            logger.info("User selected: regional")
            return 'regional'
        else:
            logger.warning("Invalid selection: %s", user_input)
            print("Opción incorrecta. Por favor seleccione '1' para global o '2' para regional.")

# Function to prompt user for environment selection: dev, stage, prod
def environment():
    valid_environments = ['dev', 'stage', 'prod']
    while True:
        print("1. Dev\n2. Stage\n3. Prod")
        user_input = input("Seleccione el entorno (1, 2 o 3): ").strip()
        
        if user_input == '1':
            logger.info("User selected environment: dev")
            return 'dev'
        elif user_input == '2':
            logger.info("User selected environment: stage")
            return 'stage'
        elif user_input == '3':
            logger.info("User selected environment: prod")
            return 'prod'
        else:
            logger.warning("Invalid environment selection: %s", user_input)
            print("Opción incorrecta. Por favor seleccione '1' para dev, '2' para stage, o '3' para prod.")

# Function to execute commands and read outputs in real-time
def execute_command(client, command, sudo_password):
    logger.debug("Executing command: %s", command)
    stdin, stdout, stderr = client.exec_command(f'sudo -S {command}\n')

    # Pass the sudo password
    stdin.write(sudo_password + '\n')
    stdin.flush()

    # Read stdout and log it in real-time
    while not stdout.channel.exit_status_ready():
        line = stdout.readline()
        if line:
            logger.info(line.strip())
            print(line.strip())  # Optional, for real-time console output

    # Check for any errors
    error_output = stderr.read().decode()
    if error_output:
        logger.error("Error output:\n%s", error_output)
        print(error_output)

def main():
    ssh_host = '192.168.4.128'
    ssh_user = 'maximus'

    # Get SSH password from the user
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

    # Get sudo password from the user
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

    # Get global or regional selection from the user
    global_regional = global_or_regional()

    # Get environment selection from the user
    env = environment()
    
    # Prompt user for MongoDB details
    mongo_user = input("Ingrese el usuario de MongoDB: ")
    mongo_password = input("Ingrese la contraseña de MongoDB: ")
    cluster = input("Ingrese el cluster: ")
    db_name = input("Ingrese el nombre de la base de datos: ")
    collection_name = input("Ingrese el nombre de la colección: ")
    pr_number = input("Ingrese el número del PR: ")
    script_name = input("Ingrese el nombre del script: ")

    # Get the current date in the required format
    current_date = datetime.datetime.now().strftime("%d%m%Y")

    # Build the path based on the user's selections
    path = f"/data/bkup/{global_regional}/{env}/"
    logger.info("Navigating to path: %s", path)

    # Define commands to execute
    commands = [
        f'cd {path}',
        f'mongodump --uri mongodb+srv://{mongo_user}:{mongo_password}@{cluster}/{db_name} '
        f'-c {collection_name} --gzip -o bkup_PR-{pr_number}-{script_name}_{current_date}'
    ]

    # Execute each command with real-time output
    for command in commands:
        execute_command(client, command, sudo_password)

    # Close SSH connection
    client.close()
    logger.info("SSH connection closed.")

if __name__ == "__main__":
    main()
