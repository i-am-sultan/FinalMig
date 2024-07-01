import re

def executePatch(dbname, patch_path):
    with open(patch_path, 'r') as f1:
        content = f1.read()
        
    # Replace dbname='...' with the new dbname
    content = re.sub(r"dbname='[^']+'", f"dbname='{dbname}'", content)
    
    print(content)  # For testing - remove this in actual usage
    # Now you can execute the patched SQL content

if __name__ == "__main__":
    patch_drill = r'C:\Users\sultan\Documents\GitHub\FinalMig\patch_drill.sql'
    patch_live = r'C:\Users\sultan\Documents\GitHub\FinalMig\patch_live.sql'
    pgCon_path = r'C:\Users\sultan\Documents\GitHub\FinalMig\pgCon.txt'
    
    with open(pgCon_path, 'r') as file:
        content = file.read()
        dbname = re.search(r'Database=([^;]+)', content)
        dbname = dbname.group(1)
        dbname = "'" + dbname + "'"
        print(dbname)
    
    # Modify patch_drill
    with open(patch_drill, 'r') as f1:
        content = f1.read()
        content = re.sub(r"dbname [^,]+", f"dbname {dbname}", content)
    
    with open(patch_drill, 'w') as f1:
        f1.write(content)

    # Modify patch_live
    with open(patch_live , 'r') as f1:
        content = f1.read()
        content = re.sub(r"dbname [^,]+", f"dbname {dbname}", content)
    
    with open(patch_drill, 'w') as f1:
        f1.write(content)
    
    # Example of execution (replace with actual logic)
    inp = int(input("Enter 1 for Drill and 2 for Live Migration: "))
    if inp == 1:
        executePatch(dbname, patch_drill)
    elif inp == 2:
        executePatch(dbname, patch_live)