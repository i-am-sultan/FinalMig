import subprocess

def runMigrationApp(app1path):
    try:
        result = subprocess.run(app1path,check=True,shell=True,capture_output=True, text=True)
        print('Migration App is run successfully')
    except subprocess.CalledProcessError as e:
        print(f'Error executing file {app1path}. Return Code {e.returncode}')
def runAuditApp(app1path):
    try:
        result = subprocess.run(app1path,check=True,shell=True,capture_output=True, text=True)
        print('Audit Trigger Creation App is run successfully')
    except subprocess.CalledProcessError as e:
        print(f'Error executing file {app1path}. Return Code {e.returncode}')
def runCompToolApp(app1path):
    try:
        result = subprocess.run(app1path,check=True,shell=True,capture_output=True, text=True)
        print('Compare Tool is run successfully')
    except subprocess.CalledProcessError as e:
        print(f'Error executing file {app1path}. Return Code {e.returncode}')


if __name__ == "__main__":
    migrationapp = r'C:\Users\sultan\Documents\GitHub\FinalMig\demo.bat'
    audittriggerapp = r'C:\Users\sultan\Documents\GitHub\FinalMig\demo.bat'
    comparetoolapp = r'C:\Users\sultan\Documents\GitHub\FinalMig\demo.bat'

    runMigrationApp(migrationapp)
    runAuditApp(audittriggerapp)
    runCompToolApp(comparetoolapp)