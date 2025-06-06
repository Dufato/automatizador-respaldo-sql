import pyodbc
import os
from datetime import datetime

# Listado de bases de datos a respaldar
lista = [""]

# Configuración de la conexión a SQL Server
server = ''
username = ''  # usuario
password = ''  # contraseña

# Directorio de OneDrive donde se almacenarán los respaldos
onedrive_dir = r''  # Ruta a la carpeta de OneDrive

for database in lista:
    try:
        # Conexión a SQL Server
        connection = pyodbc.connect(
            'DRIVER={ODBC Driver 18 for SQL Server};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
            'Encrypt=no;',
            autocommit=True
        )
        print(f"Conexión exitosa con SQL Server a la base de datos '{database}'")
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Error al conectar con SQL Server: SQLState={sqlstate}, {ex}")
        exit()

    # Crear un respaldo de la base de datos
    try:
        fecha_actual = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'{database}_backup_{fecha_actual}.bak'
        backup_file = os.path.join(onedrive_dir, backup_filename)

        # Crear el comando SQL para hacer el backup
        backup_query = f"""
            BACKUP DATABASE [{database}]
            TO DISK = '{backup_file}'
            WITH FORMAT, INIT;
            """

        cursor = connection.cursor()
        cursor.execute(backup_query)
        while cursor.nextset():
            pass
        print(f"Respaldo realizado con éxito. Archivo de respaldo: {backup_file}")
        cursor.close()

    except Exception as e:
        print(f"Error al realizar el respaldo: {e}")
        for message in cursor.messages:
            print(message)

    finally:
        connection.close()
        print("Conexión cerrada con SQL Server.")
        # Eliminar respaldos antiguos, manteniendo solo los últimos 7 días (28 archivos)
    try:
        # Obtener la lista de archivos en el directorio de respaldo
        backup_files = [f for f in os.listdir(onedrive_dir) if f.endswith('.bak')]
        backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(onedrive_dir, x)))

        # Si hay más de 28 archivos, eliminar los más antiguos
        while len(backup_files) > 28:
            oldest_file = backup_files.pop(0)
            os.remove(os.path.join(onedrive_dir, oldest_file))
            print(f"Archivo de respaldo antiguo eliminado: {oldest_file}")

    except Exception as e:
        print(f"Error al eliminar respaldos antiguos: {e}")
        
