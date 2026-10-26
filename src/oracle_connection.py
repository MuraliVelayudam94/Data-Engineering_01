import oracledb
import getpass




oracledb.init_oracle_client(
    lib_dir=r"C:/oracle/instantclient_19"
)


def get_connection():

    user_name = input('Enter username : ')
    password =  getpass.getpass('Enter password : ')


    connection = oracledb.connect(
            user = user_name,
            password = password,
            dsn="localhost:1521/xe"
        )
    
    print('Oracle connection successful . . .')
    return connection

