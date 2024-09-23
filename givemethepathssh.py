import paramiko
import datetime

def main():
    # Solicitar datos al usuario
    ssh_host = input("Ingrese la dirección del servidor SSH: ")
    ssh_user = input("Ingrese el usuario SSH: ")
    
    # Pedir contraseña SSH
    while True:
        ssh_password = input("Ingrese la contraseña SSH: ")
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
        sudo_password = input("Ingrese la contraseña sudo: ")
        
        # Intentar cambiar a sudo
        stdin, stdout, stderr = client.exec_command('sudo -k -l')
        stdin.write(sudo_password + '\n')
        stdin.flush()
        
        # Verificar si la contraseña sudo es correcta
        if "may not run" not in stderr.read().decode():
            break
        else:
            print("Contraseña sudo incorrecta. Intente de nuevo.")

    global_or_regional = input("Ingrese 'global' o 'regional': ")
    environment = input("Ingrese el ambiente (dev/stage/prod): ")
    
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
