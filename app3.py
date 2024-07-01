import re
import psycopg2

def executePatch(dbname, patch_path):    
    with open(patch_path, 'r') as f1:
        content = f1.read()
    
    # Verify and print the content to debug
    print("Content before substitution:")
    print(content)
    
    # Perform substitution with proper formatting
    content = re.sub(r"dbname [^,]+", f"dbname '{dbname}'", content)
    
    # Print the content after substitution for verification
    print("Content after substitution:")
    print(content)

    # Establish connection and execute the patched SQL
    # print(f"Connecting to database '{dbname}'...")
    print(dbname)
    connection = psycopg2.connect(database=dbname, user='postgres', password='postgres', host="10.1.0.8", port=5432)
    cursor = connection.cursor()
    
    try:
        cursor.execute(content)
        connection.commit()
        print("Patch executed successfully.")
    except psycopg2.Error as e:
        print(f"Error executing patch: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    patch_drill = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\patch_drill.sql'
    patch_live = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\patch_live.sql'
    pgCon_path = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\pgCon.txt'

    with open(pgCon_path, 'r') as file:
        content = file.read()
        
    dbname_match = re.search(r'Database=([^;]+)', content)
    if dbname_match:
        dbname = dbname_match.group(1)
        print(f"Database name found: {dbname}")
    else:
        print("Database name not found in pgCon.txt")
        exit(1)
    
    # Example of execution (replace with actual logic)
    inp = int(input("Enter 1 for Drill and 2 for Live Migration: "))
    if inp == 1:
        executePatch(dbname, patch_drill)
    elif inp == 2:
        executePatch(dbname, patch_live)
