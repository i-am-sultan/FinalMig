import re

def updateOraCon(OraSchema, OraHost, filepath):
    with open(filepath, 'r') as f1:
        content = f1.read()
    content = re.sub(r'User Id=[^;]+;', f'User Id={OraSchema.upper()};', content)
    content = re.sub(r'HOST=[^)]*', f'HOST={OraHost}', content)
    print('oracon')
    print(content)

def updatepgCon(pgDbName, filepath):
    with open(filepath, 'r') as f1:
        content = f1.read()
    content = re.sub(r'Database=[^;]+;', f'Database={pgDbName};', content)
    print('pgcon')
    print(content)

def updateToolkit(OraSchema, OraHost, pgDbName, filepath):
    with open(filepath, 'r') as f1:
        content = f1.read()
    content = re.sub(r'SRC_DB_URL=jdbc:oracle:thin:@[^:]+', f'SRC_DB_URL=jdbc:oracle:thin:@{OraHost}', content)
    content = re.sub(r'SRC_DB_USER=[^\s]+', f'SRC_DB_USER={OraSchema.upper()}', content)
    content = re.sub(r':5432/[^\s]+', f':5432/{pgDbName}', content)
    print('toolkit')
    #print(content)

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

