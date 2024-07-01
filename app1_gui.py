import sys
import re
import json
import shutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
    QMessageBox, QTextEdit, QHBoxLayout
)

def updateOraCon(OraSchema, OraHost, filepath, log_window):
    with open(filepath, 'r') as f1:
        content = f1.read()
    content = re.sub(r'User Id=[^;]+;', f'User Id={OraSchema.upper()};', content)
    content = re.sub(r'HOST=[^)]*', f'HOST={OraHost}', content)
    with open(filepath, 'w') as f1:
        f1.write(content)
    log_window.append('oracon updated')

def updatepgCon(pgDbName, filepath, log_window):
    with open(filepath, 'r') as f1:
        content = f1.read()
    content = re.sub(r'Database=[^;]+;', f'Database={pgDbName};', content)
    with open(filepath, 'w') as f1:
        f1.write(content)
    log_window.append('pgcon updated')

def updateToolkit(OraSchema, OraHost, pgDbName, filepath, log_window):
    with open(filepath, 'r') as f1:
        content = f1.read()
    content = re.sub(r'SRC_DB_URL=jdbc:oracle:thin:@[^:]+', f'SRC_DB_URL=jdbc:oracle:thin:@{OraHost}', content)
    content = re.sub(r'SRC_DB_USER=[^\s]+', f'SRC_DB_USER={OraSchema.upper()}', content)
    content = re.sub(r':5432/[^\s]+', f':5432/{pgDbName}', content)
    with open(filepath, 'w') as f1:
        f1.write(content)
    log_window.append('toolkit updated')

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

    log_window.append('connection.json updated')
    log_window.append(json.dumps(data, indent=4))

def copyFiles(destination_dir, log_window):
    try:
        # Pre-specified file paths
        oracon_path = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\OraCon.txt'
        pgcon_path = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\pgCon.txt'

        shutil.copy(oracon_path, destination_dir)
        shutil.copy(pgcon_path, destination_dir)
        
        log_window.append('Files copied successfully.')
        return True
    except Exception as e:
        log_window.append(f'Error copying files: {e}')
        return False

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

        self.copyButton = QPushButton('Copy Files')
        self.copyButton.clicked.connect(self.copyFilesToDestination)
        button_layout.addWidget(self.copyButton)

        self.exitButton = QPushButton('Exit')
        self.exitButton.clicked.connect(self.closeApplication)
        button_layout.addWidget(self.exitButton)

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

            QMessageBox.information(self, 'Success', 'Connections updated successfully.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}')
            self.logWindow.append(f'Error updating connections: {e}')

    def copyFilesToDestination(self):
        destination_dir = r'C:\Users\sultan.m\Documents\GitHub'

        success = copyFiles(destination_dir, self.logWindow)
        if success:
            QMessageBox.information(self, 'Success', 'Files copied successfully.')
        else:
            QMessageBox.critical(self, 'Error', 'An error occurred while copying files.')

    def closeApplication(self):
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = UpdateConnectionApp()
    ex.show()
    sys.exit(app.exec_())
