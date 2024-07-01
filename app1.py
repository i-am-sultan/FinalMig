import re
import json

def updateOraCon(OraSchema, OraHost, filepath):
    with open(filepath, 'r') as f1:
        content = f1.read()
    content = re.sub(r'User Id=[^;]+;', f'User Id={OraSchema.upper()};', content)
    content = re.sub(r'HOST=[^)]*', f'HOST={OraHost}', content)
    print('oracon')
    with open(filepath,'w') as f1:
        f1.write(content)

def updatepgCon(pgDbName, filepath):
    with open(filepath, 'r') as f1:
        content = f1.read()
    content = re.sub(r'Database=[^;]+;', f'Database={pgDbName};', content)
    print('pgcon')
    with open(filepath,'w') as f1:
        f1.write(content)

def updateToolkit(OraSchema, OraHost, pgDbName, filepath):
    with open(filepath, 'r') as f1:
        content = f1.read()
    content = re.sub(r'SRC_DB_URL=jdbc:oracle:thin:@[^:]+', f'SRC_DB_URL=jdbc:oracle:thin:@{OraHost}', content)
    content = re.sub(r'SRC_DB_USER=[^\s]+', f'SRC_DB_USER={OraSchema.upper()}', content)
    content = re.sub(r':5432/[^\s]+', f':5432/{pgDbName}', content)
    print('toolkit')
    with open(filepath,'w') as f1:
        f1.write(content)

def updateConnectionJson(OraSchema, OraHost, pgDbName, filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    # Update Oracle connection
    ora_conn = data["Connection_1"]
    print(ora_conn)
    ora_conn = re.sub(r'User Id=[^;]+;', f'User Id={OraSchema.upper()};', ora_conn)
    ora_conn = re.sub(r'HOST=[^)]*', f'HOST={OraHost}', ora_conn)
    data["Connection_1"] = ora_conn

    # Update Postgres connection
    pg_conn = data["Connection_2"]
    pg_conn = re.sub(r'Database=[^;]+;', f'Database={pgDbName};', pg_conn)
    data["Connection_2"] = pg_conn

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

    print('connection.json')
    print(json.dumps(data, indent=4))

if __name__ == "__main__":
    OraSchema = input('Enter Oracle Schema Name: ')
    OraHost = input('Enter Oracle Host: ')
    pgDbName = input('Enter Postgres Database Name: ')

    # Modify Oracon.txt
    file1 = r'C:\Users\sultan\Documents\GitHub\FinalMig\OraCon.txt'
    updateOraCon(OraSchema, OraHost, file1)

    # Modify PgCon.txt
    file2 = r'C:\Users\sultan\Documents\GitHub\FinalMig\pgCon.txt'
    updatepgCon(pgDbName, file2)

    # Modify toolkit.properties
    toolkit_path = r'C:\Users\sultan\Documents\GitHub\FinalMig\toolkit.properties'
    updateToolkit(OraSchema, OraHost, pgDbName, toolkit_path)

    #Modify the connection.json
    connection_json = r'C:\Users\sultan\Documents\GitHub\FinalMig\connection.json'
    updateConnectionJson(OraSchema, OraHost, pgDbName, connection_json)