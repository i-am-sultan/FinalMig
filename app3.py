import psycopg2
import re

#read pgcon.txt
pgCon_path = r'C:\Users\sultan\Documents\GitHub\FinalMig\pgCon.txt'
with open(pgCon_path,'r') as file:
    content = file.read()
    dbname = re.search(r'Database=([^;]+)',content)
    dbname = dbname.group(1)
connection = psycopg2.connect(database=f"{dbname}",user='postgres',password='12345',host='localhost',port=5432)
cursor = connection.cursor()

file1=r'C:\Users\sultan\Documents\GitHub\FinalMig\patch.sql'
with open(file1,'r') as f1:
    content = f1.read()
cursor.execute(content)
result = cursor.fetchall()
print(result)