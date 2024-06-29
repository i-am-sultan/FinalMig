import subprocess

def combineApps(app1path):
    try:
        result = subprocess.run(app1path,check=True,shell=True)
        print('App1 is run successfully')
    except subprocess.CalledProcessError as e:
        print(f'Error executing file {app1path}. Return Code {e.returncode}')

if __name__ == "__main__":
    app1path = r'C:\Users\sultan\Documents\GitHub\FinalMig\OraCon.txt'
    combineApps(app1path)