# 1. create a python script to generate(or replace) toolkit.properties, connection.json, oracon.txt and pgcon.txt
import re

def updateOraCon(OraSchema,OraHost,filepath):
    with open(filepath,'r') as f1:
        content = f1.read()
    content = re.sub(r'User Id=[^;]+;',f'User Id={OraSchema.upper()};',content)
    content = re.sub(r'HOST=[^)]*',f'HOST={OraHost}',content)
    print(content)

def updatepgCon(pgDbName,filepath):
    with open(filepath,'r') as f1:
        content = f1.read()
    content = re.sub(r'Database=[^;]+;',f'Database={pgDbName};',content)
    print(content)

if __name__ == "__main__":
    OraSchema = input('Enter Oracle Schema Name: ')
    OraHost = input('Enter Oracle Host: ')
    pgDbName = input('Enter Postgres Database Name: ')

    #Modify Oracon.txt
    file1 = r'C:\Users\sultan\Documents\GitHub\FinalMig\OraCon.txt'
    updateOraCon(OraSchema,OraHost,file1)

    #Modify PgCon.txt
    file2 = r'C:\Users\sultan\Documents\GitHub\FinalMig\pgCon.txt'
    updatepgCon(pgDbName,file2)