import paramiko
from getpass import getpass
import datetime
import logging
import time

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

def main():
    # Solicitar datos al usuario
    ssh_host = '192.168.4.128'
    ssh_user = 'maximus'
    
    # Pedir contraseña SSH
    while True:
        ssh_password = getpass("Ingrese la contraseña SSH: ")
        try:
            # Conectar por SSH
            logger.debug("Attempting to connect via SSH to %s", ssh_host)
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ssh_host, username=ssh_user, password=ssh_password)
            logger.info("SSH connection established with %s", ssh_host)
            break
        except paramiko.AuthenticationException:
            logger.error("Contraseña SSH incorrecta.")
            print("Contraseña SSH incorrecta. Intente de nuevo.")

    # Pedir contraseña sudo
    while True:
        sudo_password = getpass("Ingrese la contraseña sudo: ")
        
        # Intentar cambiar a sudo
        stdin, stdout, stderr = client.exec_command('sudo -k -l')
        stdin.write(sudo_password + '\n')
        stdin.flush()
        
        # Verificar si la contraseña sudo es correcta
        if "may not run" not in stderr.read().decode():
            logger.info("Sudo password accepted.")
            break
        else:
            logger.error("Contraseña sudo incorrecta.")
            print("Contraseña sudo incorrecta. Intente de nuevo.")

    def global_or_regional():
        valid_parameters = ['regional', 'global']
        while True:
            user_input1 = input("Ingrese 'global' o 'regional': ").strip().lower()
            if user_input1 in valid_parameters:
                logger.info("User selected: %s", user_input1)
                print(f"You have selected {user_input1}")
                return user_input1
            else:
                logger.warning("Invalid global or regional selection: %s", user_input1)
                print('You have selected a wrong parameter')

    def environment():
        valid_environments = ['dev', 'stage', 'prod']
        while True:
            user_input = input("Ingrese 'dev', 'stage', or 'prod': ")
            if user_input in valid_environments:
                logger.info("User selected environment: %s", user_input)
                print(f"You have selected {user_input}")
                return user_input
            else:
                logger.warning("Invalid environment selection: %s", user_input)
                print('You have selected a wrong environment') 

    global_regional = global_or_regional()
    env = environment()
    
    mongo_user = input("Ingrese el usuario de MongoDB: ")
    mongo_password = input("Ingrese la contraseña de MongoDB: ")
    cluster = input("Ingrese el cluster: ")
    db_name = input("Ingrese el nombre de la base de datos: ")
    collection_name = input("Ingrese el nombre de la colección: ")
    pr_number = input("Ingrese el número del PR: ")
    script_name = input("Ingrese el nombre del script: ")

    # Obtener la fecha actual en el formato requerido
    current_date = datetime.datetime.now().strftime("%d%m%Y")

    # Navegar al directorio deseado
    path = f"/data/bkup/{global_regional}/{env}/"
    
    # Ejecutar comandos en la misma sesión
    commands = [
        f'cd {path}',
        f'mongodump --uri mongodb+srv://{mongo_user}:{mongo_password}@{cluster}/{db_name} '
        f'-c {collection_name} --gzip -o bkup_PR-{pr_number}-{script_name}_{current_date}'
    ]

    for command in commands:
        logger.debug("Executing command: %s", command)
        stdin, stdout, stderr = client.exec_command(f'sudo -S {command}\n')
        stdin.write(sudo_password + '\n')
        stdin.flush()
        
        # Leer la salida
        stdout_output = stdout.read().decode()
        stderr_output = stderr.read().decode()

        logger.info("Command output:\n%s", stdout_output)
        if stderr_output:
            logger.error("Error output:\n%s", stderr_output)

        print(stdout_output)
        print(stderr_output)

    client.close()
    logger.info("SSH connection closed.")

if __name__ == "__main__":
    main()
