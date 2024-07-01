import sys
import re
import json
import shutil
import subprocess
import psycopg2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
    QMessageBox, QTextEdit, QHBoxLayout, QComboBox
)

def updateOraCon(OraSchema, OraHost, filepath, log_window):
    with open(filepath, 'r') as f1:
        content = f1.read()
    content = re.sub(r'User Id=[^;]+;', f'User Id={OraSchema.upper()};', content)
    content = re.sub(r'HOST=[^)]*', f'HOST={OraHost}', content)
    with open(filepath, 'w') as f1:
        f1.write(content)
    log_window.append('OraCon: ')
    log_window.append(content)

def updatepgCon(pgDbName, filepath, log_window):
    with open(filepath, 'r') as f1:
        content = f1.read()
    content = re.sub(r'Database=[^;]+;', f'Database={pgDbName};', content)
    with open(filepath, 'w') as f1:
        f1.write(content)
    log_window.append('\npgCon: ')
    log_window.append(content)

def updateToolkit(OraSchema, OraHost, pgDbName, filepath, log_window):
    with open(filepath, 'r') as f1:
        content = f1.read()
    content = re.sub(r'SRC_DB_URL=jdbc:oracle:thin:@[^:]+', f'SRC_DB_URL=jdbc:oracle:thin:@{OraHost}', content)
    content = re.sub(r'SRC_DB_USER=[^\s]+', f'SRC_DB_USER={OraSchema.upper()}', content)
    content = re.sub(r':5432/[^\s]+', f':5432/{pgDbName}', content)
    with open(filepath, 'w') as f1:
        f1.write(content)
    log_window.append('\ntoolkit.properties: ')
    log_window.append(content)

def updateConnectionJson(OraSchema, OraHost, pgDbName, filepath, log_window):
    with open(filepath, 'r') as f:
        data = json.load(f)
    # Update Oracle connection
    ora_conn = data["Connection_1"]
    ora_conn = re.sub(r'User Id=[^;]+;', f'User Id={OraSchema.upper()};', ora_conn)
    ora_conn = re.sub(r'HOST=[^)]*', f'HOST={OraHost}', ora_conn)
    data["Connection_1"] = ora_conn

    # Update Postgres connection
    pg_conn = data["Connection_2"]
    pg_conn = re.sub(r'Database=[^;]+;', f'Database={pgDbName};', pg_conn)
    data["Connection_2"] = pg_conn

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

    log_window.append('\nconnection.json: ')
    log_window.append(json.dumps(data, indent=4))

def updatePatchDrill(pgDbname, filepath, log_window):
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Modify the content to replace dbname with pgDbname
        content = re.sub(r"OPTIONS \(dbname '[^']+\'", f"OPTIONS (dbname '{pgDbname}'", content)

        with open(filepath, 'w') as f:
            f.write(content)

        log_window.append(f'Successfully updated patch_drill.sql for database {pgDbname}.')
    except Exception as e:
        log_window.append(f'Error updating patch_drill.sql: {e}')

def updatePatchLive(pgDbname, filepath, log_window):
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Modify the content to replace dbname with pgDbname
        content = re.sub(r"OPTIONS \(dbname '[^']+\'", f"OPTIONS (dbname '{pgDbname}'", content)

        with open(filepath, 'w') as f:
            f.write(content)

        log_window.append(f'Successfully updated patch_live.sql for database {pgDbname}.')
    except Exception as e:
        log_window.append(f'Error updating patch_live.sql: {e}')


def copyFiles(destination_dir, log_window):
    try:
        # Pre-specified file paths
        oracon_path = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\OraCon.txt'
        pgcon_path = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\pgCon.txt'

        shutil.copy(oracon_path, destination_dir)
        shutil.copy(pgcon_path, destination_dir)
        
        log_window.append('Files copied successfully.')
        log_window.append(f'Files copied from {oracon_path} and {pgcon_path} to {destination_dir}')
        return True
    except Exception as e:
        log_window.append(f'Error copying files: {e}')
        return False

def executePatch(dbname, patch_path, log_window):
    connection = None
    cursor = None
    try:
        # Read the SQL patch file
        with open(patch_path, 'r') as f1:
            content = f1.read()
        content = re.sub(r"dbname [^,]+", f"dbname '{dbname}'", content)
        with open(patch_path, 'w') as f1:
            f1.write(content)
        print(dbname)
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(database=dbname, user='postgres', password='postgres', host="10.1.0.8", port=5432)
        cursor = connection.cursor()
        # Execute the SQL content
        cursor.execute(content)
        # Commit the transaction
        connection.commit()
        # Log successful execution
        log_window.append(f'Success: Executed patch {patch_path} on database {dbname}.')
    except psycopg2.Error as e:
        # Log any psycopg2 database errors
        log_window.append(f'Error: Failed to execute patch {patch_path} on database {dbname}. Error: {e}')
    except Exception as e:
        # Log any other unexpected errors
        log_window.append(f'Error: Failed to execute patch {patch_path} on database {dbname}. Unexpected error: {e}')
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

class UpdateConnectionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Update Connections')

        main_layout = QVBoxLayout()

        form_layout = QVBoxLayout()
        
        self.oraSchemaLabel = QLabel('Oracle Schema:')
        self.oraSchemaInput = QLineEdit()
        form_layout.addWidget(self.oraSchemaLabel)
        form_layout.addWidget(self.oraSchemaInput)

        self.oraHostLabel = QLabel('Oracle Host:')
        self.oraHostInput = QLineEdit()
        form_layout.addWidget(self.oraHostLabel)
        form_layout.addWidget(self.oraHostInput)

        self.pgDbNameLabel = QLabel('PostgreSQL Database Name:')
        self.pgDbNameInput = QLineEdit()
        form_layout.addWidget(self.pgDbNameLabel)
        form_layout.addWidget(self.pgDbNameInput)

        button_layout = QHBoxLayout()
        self.updateButton = QPushButton('Update Connections')
        self.updateButton.clicked.connect(self.updateConnections)
        button_layout.addWidget(self.updateButton)

        self.exitButton = QPushButton('Exit')
        self.exitButton.clicked.connect(self.closeApplication)
        button_layout.addWidget(self.exitButton)

        self.migrationButton = QPushButton('Run Migration App')
        self.migrationButton.clicked.connect(self.runMigrationApp)
        button_layout.addWidget(self.migrationButton)

        self.auditButton = QPushButton('Run Audit App')
        self.auditButton.clicked.connect(self.runAuditApp)
        button_layout.addWidget(self.auditButton)

        self.compareButton = QPushButton('Run Compare Tool')
        self.compareButton.clicked.connect(self.runCompareToolApp)
        button_layout.addWidget(self.compareButton)

        self.patchComboBox = QComboBox()
        self.patchComboBox.addItem("Drill")
        self.patchComboBox.addItem("Live Migration")
        button_layout.addWidget(self.patchComboBox)

        self.patchButton = QPushButton('Execute SQL Patch')
        self.patchButton.clicked.connect(self.executeSQLPatch)
        button_layout.addWidget(self.patchButton)

        self.logWindow = QTextEdit()
        self.logWindow.setReadOnly(True)

        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.logWindow)

        self.setLayout(main_layout)

    def updateConnections(self):
        OraSchema = self.oraSchemaInput.text()
        OraHost = self.oraHostInput.text()
        pgDbName = self.pgDbNameInput.text()

        if not OraSchema or not OraHost or not pgDbName:
            QMessageBox.warning(self, 'Input Error', 'Please fill in all fields.')
            return

        try:
            # Pre-specified file paths
            oracon_path = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\OraCon.txt'
            pgcon_path = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\pgCon.txt'
            toolkit_path = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\toolkit.properties'
            connection_json_path = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\connection.json'

            updateOraCon(OraSchema, OraHost, oracon_path, self.logWindow)
            updatepgCon(pgDbName, pgcon_path, self.logWindow)
            updateToolkit(OraSchema, OraHost, pgDbName, toolkit_path, self.logWindow)
            updateConnectionJson(OraSchema, OraHost, pgDbName, connection_json_path, self.logWindow)

            # Copy the files to the destination directory
            destination_dir = r'C:\Users\sultan.m\Documents\GitHub'
            success = copyFiles(destination_dir, self.logWindow)
            if success:
                QMessageBox.information(self, 'Success', 'Connections updated and files copied successfully.')
            else:
                QMessageBox.critical(self, 'Error', 'An error occurred while copying files.')

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}')
            self.logWindow.append(f'Error updating connections: {e}')

    def executeSQLPatch(self):
        patch_choice = self.patchComboBox.currentText()
        pgCon_path = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\pgCon.txt'

        with open(pgCon_path, 'r') as file:
            content = file.read()
        dbname_match = re.search(r'Database=([^;]+)', content)
        if dbname_match:
            pgDbname = dbname_match.group(1)

            if patch_choice == "Drill":
                patch_path = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\patch_drill.sql'
                updatePatchDrill(pgDbname, patch_path, self.logWindow)
                executePatch(pgDbname, patch_path, self.logWindow)  # Example execution after update
            elif patch_choice == "Live Migration":
                patch_path = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\patch_live.sql'
                updatePatchLive(pgDbname, patch_path, self.logWindow)
                executePatch(pgDbname, patch_path, self.logWindow)  # Example execution after update
        else:
            QMessageBox.warning(self, 'Database not found', 'Unable to determine database name from pgCon.txt.')


    def runMigrationApp(self):
        migrationapp = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\migrationapp.exe'
        self.runExternalApp(migrationapp)

    def runAuditApp(self):
        audittriggerapp = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\audittriggerapp.exe'
        self.runExternalApp(audittriggerapp)

    def runCompareToolApp(self):
        comparetoolapp = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\comparetoolapp.exe'
        self.runExternalApp(comparetoolapp)

    def runExternalApp(self, app_path):
        try:
            result = subprocess.run(app_path, check=True, shell=True, capture_output=True, text=True)
            self.logWindow.append(f'{app_path} executed successfully.')
        except subprocess.CalledProcessError as e:
            self.logWindow.append(f'Error executing {app_path}: {e}')
            QMessageBox.critical(self, 'Execution Error', f'Error executing {app_path}. Return Code {e.returncode}')

    def closeApplication(self):
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = UpdateConnectionApp()
    ex.show()
    sys.exit(app.exec_())
