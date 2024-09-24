import paramiko
from getpass import getpass
import datetime

def main():
    # Solicitar datos al usuario
    ssh_host = '192.168.4.128'
    ssh_user = 'maximus'
    
    # Pedir contraseña SSH
    while True:
        ssh_password = getpass("Ingrese la contraseña SSH: ")
        try:
            # Conectar por SSH
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ssh_host, username=ssh_user, password=ssh_password)
            break
        except paramiko.AuthenticationException:
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
            break
        else:
            print("Contraseña sudo incorrecta. Intente de nuevo.")

    def global_or_regional():
            valid_paramenters = ['regional', 'global']
            while True:
               user_input1 = input("Ingrese 'global' o 'regional': ").strip().lower()
                
               if user_input1 in valid_paramenters:
                    print(f'You have selected{user_input1}')
                    return user_input1
                    
                

            else:
                print('you have selected a wrong parameter')
                    


                    


            
    def environment():
        valid_enviroments = ['dev', 'stage', 'prod']
        while True:

            user_input = input("Ingrese 'dev' , 'stage', or 'prod': ")
            if user_input in valid_enviroments:
                print(f'You have selected{user_input}')
                return user_input
                

            else:
                print('you have selected a wrong enviroment') 
                
    

    global_or_regional()
    environment()
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
    path = f"/data/bkup/{global_or_regional}/{environment}/"
    
    # Ejecutar comandos en la misma sesión
    commands = [
        f'cd {path}',
        f'mongodump --uri mongodb+srv://{mongo_user}:{mongo_password}@{cluster}/{db_name} '
        f'-c {collection_name} --gzip -o bkup_PR-{pr_number}-{script_name}_{current_date}'
    ]

    for command in commands:
        stdin, stdout, stderr = client.exec_command(f'sudo -S {command}\n')
        stdin.write(sudo_password + '\n')
        stdin.flush()
        
        # Leer la salida
        print(stdout.read().decode())
        print(stderr.read().decode())

    client.close()

if __name__ == "__main__":
    main()