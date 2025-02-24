import sys
import re
import json
import shutil
import subprocess
import psycopg2
import requests
import os
import zipfile
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QTextEdit, QMessageBox
)

oracon_path = r'C:\Program Files\edb\prodmig\RunCMDEdb_New\netcoreapp3.1\OraCon.txt'
pgcon_path = r'C:\Program Files\edb\prodmig\RunCMDEdb_New\netcoreapp3.1\pgCon.txt'
toolkit_path = r'C:\Program Files\edb\mtk\etc\toolkit.properties'
connection_json_path = r'C:\Program Files\edb\prodmig\Ora2PGCompToolKit\Debug\Connection.json'
audit_path = r'C:\Program Files\edb\prodmig\AuditTriggerCMDNew\netcoreapp3.1'
patch_drill_path = r'C:\Program Files\edb\prodmig\PostMigPatches\patch_drill.sql'
patch_live_path = r'C:\Program Files\edb\prodmig\PostMigPatches\patch_live.sql'
job_patch_path = r'C:\Program Files\edb\prodmig\PostMigPatches\patch_jobs.sql'
migrationapp_path = r'C:\Program Files\edb\prodmig\RunCMDEdb_New\netcoreapp3.1\RunEDBCommand.exe'
audittriggerapp_path = r'C:\Program Files\edb\prodmig\AuditTriggerCMDNew\netcoreapp3.1\TriggerConstraintViewCreationForAuditPostMigration.exe'
comparetoolapp_path = r'C:\Program Files\edb\prodmig\Ora2PGCompToolKit\Debug\OraPostGreSqlComp.exe'
version_path = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\version.txt'

def get_latest_release_info(repo, token):
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        release_info = response.json()
        return release_info
    else:
        print(f"Failed to fetch release information. Status code: {response.status_code}")
        return None

def checkForUpdates(log_window):
    log_window.append('Checking for updates...')
    try:
        repo = "i-am-sultan/FinalMig"
        token = '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'  # Replace with your personal access token
        latest_release = get_latest_release_info(repo, token)

        if latest_release:
            latest_version = latest_release['tag_name']
            assets = latest_release['assets']

            if assets:
                update_asset = assets[0]  # Assuming the first asset is the one you want to download
                print(update_asset)
                update_url = update_asset['browser_download_url']

                global version_path

                # Read the current version from a file (version.txt in the app directory)
                with open(version_path, 'r') as f:
                    current_version = f.read().strip()

                log_window.append(f'Current version: {current_version}')
                log_window.append(f'Latest version: {latest_version}')

                # Compare versions
                if latest_version != current_version:
                    log_window.append('New version available. Downloading and applying update...')

                    # Download the update
                    response = requests.get(update_url)
                    print(update_url)
                    print(response)

                    if response.status_code == 200:
                        update_filename = os.path.basename(update_url)
                        update_file_path = os.path.join(os.getcwd(), update_filename)

                        with open(update_file_path, 'wb') as f:
                            f.write(response.content)

                        log_window.append('Update downloaded successfully.')

                        # Update the current version
                        with open(version_path, 'w') as f:
                            f.write(latest_version)

                        log_window.append('Update applied successfully.')
                    else:
                        log_window.append(f"Failed to download update. Status code: {response.status_code}")
                else:
                    log_window.append('You are already using the latest version.')
            else:
                log_window.append('No assets found in the latest release.')
        else:
            log_window.append('Failed to fetch latest release information.')

    except Exception as e:
        log_window.append(f'Error checking and applying updates: {e}')


def updateOraCon(OraSchema, OraHost,oraPort, OraPass,OraService, filepath, log_window):
    content = (
            f"User Id={OraSchema};Password={OraPass};"
            f"Data Source=(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={OraHost})(PORT={oraPort}))"
            f"(CONNECT_DATA=(SERVICE_NAME={OraService})))"
        )
    with open(filepath, 'w') as f1:
        f1.write(content)
    log_window.append('OraCon: ')
    log_window.append(content)

def updatepgCon(pgHost,pgPort, pgUser,pgPass, pgDbName, filepath, log_window):
    content = (f"Server={pgHost};Port={pgPort};Database={pgDbName};User Id={pgUser};Password={pgPass};ApplicationName=w3wp.exe;Ssl Mode=Require;")
    with open(filepath, 'w') as f1:
        f1.write(content)
    log_window.append('\npgCon: ')
    log_window.append(content)

def updateToolkit(OraSchema, OraHost,OraPort, OraPass, OraService, pgHost, pgPort,pgUser, pgPass, pgDbName, filepath, log_window):
    # Prepare the new properties
    oracle_url = f"jdbc:oracle:thin:@{OraHost}:{OraPort}:{OraService}"
    postgres_url = f"jdbc:postgresql://{pgHost}:{pgPort}/{pgDbName}"
    
    content = (
        f"SRC_DB_URL={oracle_url}\n"
        f"SRC_DB_USER={OraSchema}\n"
        f"SRC_DB_PASSWORD={OraPass}\n\n"
        f"TARGET_DB_URL={postgres_url}\n"
        f"TARGET_DB_USER={pgUser}\n"
        f"TARGET_DB_PASSWORD={pgPass}\n"
    )   
    with open(filepath, 'w') as f1:
        f1.write(content)
    log_window.append('\ntoolkit.properties: ')
    log_window.append(content)

def updateConnectionJson(OraSchema, OraHost,OraPort, OraPass, OraService, pgHost,pgPort, pgUser, pgPass, pgDbName, filepath, log_window):
    try:
        with open(filepath, 'r') as f:
            connections = json.load(f)
        # Update the Oracle connection string
        connections["Connection_1"] = f"Data Source=(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={OraHost})(PORT={OraPort}))(CONNECT_DATA=(SERVICE_NAME={OraService})));User Id={OraSchema};Password={OraPass};DatabaseType=ORACLE"
        # Update the PostgreSQL connection string
        connections["Connection_2"] = f"Server={pgHost};Port={pgPort};Database={pgDbName};User Id={pgUser};Password={pgPass};ApplicationName=w3wp.exe;Ssl Mode=Require;DatabaseType=POSTGRES"
        with open(filepath, 'w') as f:
            json.dump(connections, f, indent=4)
        log_window.append('\nconnection.json updated successfully.')
        log_window.append(json.dumps(connections, indent=4))
    except FileNotFoundError:
        log_window.append(f'Error: File {filepath} not found.')
    except json.JSONDecodeError as e:
        log_window.append(f'Error: Failed to decode JSON from {filepath}. Details: {str(e)}')
    except Exception as e:
        log_window.append(f'Error updating connection.json: {str(e)}')

def updatePatchDrill(pgDbname, filepath, log_window):
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Modify the content to replace dbname with pgDbname
        content = re.sub(r"OPTIONS \(dbname '[^']+\'", f"OPTIONS (dbname '{pgDbname}'", content)
        content = re.sub(r'REVOKE ALL ON DATABASE "[^"]+',f'REVOKE ALL ON DATABASE "{pgDbname}',content)
        content = re.sub(r'GRANT CONNECT ON DATABASE "[^"]+',f'GRANT CONNECT ON DATABASE "{pgDbname}',content)

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
        content = re.sub(r'REVOKE ALL ON DATABASE "[^"]+',f'REVOKE ALL ON DATABASE "{pgDbname}',content)
        content = re.sub(r'GRANT CONNECT ON DATABASE "[^"]+',f'GRANT CONNECT ON DATABASE "{pgDbname}',content)

        with open(filepath, 'w') as f:
            f.write(content)

        log_window.append(f'Successfully updated patch_live.sql for database {pgDbname}.')
    except Exception as e:
        log_window.append(f'Error updating patch_live.sql: {e}')

def copyFiles(destination_dir, log_window):
    try:
        # Pre-specified file paths
        global oracon_path
        global pgcon_path

        shutil.copy(oracon_path, destination_dir)
        shutil.copy(pgcon_path, destination_dir)
        
        log_window.append('Files copied successfully.')
        log_window.append(f'Files copied from {oracon_path} and {pgcon_path} to {destination_dir}')
        return True
    except Exception as e:
        log_window.append(f'Error copying files: {e}')
        return False

def executePatch(pgHost,pgPort,pgUserName,pgPass,pgDbname, patch_path, log_window):
    connection = None
    cursor = None
    try:
        # Read the SQL patch file
        with open(patch_path, 'r') as f1:
            content = f1.read()
        content = re.sub(r"dbname [^,]+", f"dbname '{pgDbname}'", content)
        with open(patch_path, 'w') as f1:
            f1.write(content)
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(database=pgDbname, user=pgUserName, password=pgPass, host=pgHost, port=pgPort)
        cursor = connection.cursor()
        cursor.execute(content)
        connection.commit()
        
        connection = psycopg2.connect(database=pgDbname, user=pgUserName, password=pgPass, host=pgHost, port=pgPort)
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute('CALL populate_first_time_migdata()')
        # Commit the transaction
        connection.commit()
        # Log successful execution
        log_window.append(f'Success: Executed patch {patch_path} on database {pgDbname}.')
    except psycopg2.Error as e:
        # Log any psycopg2 database errors
        log_window.append(f'Error: Failed to execute patch {patch_path} on database {pgDbname}. Error: {e}')
    except Exception as e:
        # Log any other unexpected errors
        log_window.append(f'Error: Failed to execute patch {patch_path} on database {pgDbname}. Unexpected error: {e}')
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def createJobs(schema_name, pgHost, pgUserName, pgPort, pgPass, pgDbname, job_patch_path, log_window):
    connection = None
    cursor = None
    
    try:
        with open(job_patch_path, 'r') as f1:
            content = f1.read()

        patterns = [
            (r"select cron\.schedule_in_database\('GINESYS_AUTO_SETTLEMENT_JOB_[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_AUTO_SETTLEMENT_JOB_{schema_name.upper()}','*/15 * * * *','call main.db_pro_auto_settle_unpost()','{pgDbname}');"),
            (r"select cron\.schedule_in_database\('GINESYS_DATA_SERVICE_2[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_DATA_SERVICE_2_{schema_name.upper()}','*/1 * * * *','call main.db_pro_gds2_event_enqueue()','{pgDbname}');"),
            (r"select cron\.schedule_in_database\('GINESYS_INVSTOCK_INTRA_LOG_AGG[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_INVSTOCK_INTRA_LOG_AGG_{schema_name.upper()}','30 seconds','call main.invstock_intra_log_refresh()','{pgDbname}');"),
            (r"select cron\.schedule_in_database\('GINESYS_INVSTOCK_LOG_AGG[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_INVSTOCK_LOG_AGG_{schema_name.upper()}','30 seconds','call main.invstock_log_refresh()','{pgDbname}');"),
            (r"select cron\.schedule_in_database\('GINESYS_PERIOD_CLOSURE_JOB[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_PERIOD_CLOSURE_JOB_{schema_name.upper()}','*/2 * * * *','call main.db_pro_period_closure_dequeue()','{pgDbname}');"),
            (r"select cron\.schedule_in_database\('GINESYS_POS_STLM_AUDIT[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_POS_STLM_AUDIT_{schema_name.upper()}','*/5 * * * *','call main.db_pro_pos_stlm_audit()','{pgDbname}');"),
            (r"select cron\.schedule_in_database\('GINESYS_RECALCULATE_TAX_JOB[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_RECALCULATE_TAX_JOB_{schema_name.upper()}','*/30 * * * *','call main.db_pro_recalculategst()','{pgDbname}');"),
            (r"select cron\.schedule_in_database\('GINESYS_STOCK_BOOK_PIPELINE_DELTA_AGG[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_STOCK_BOOK_PIPELINE_DELTA_AGG_{schema_name.upper()}','*/5 * * * *','call db_pro_delta_agg_pipeline_stock()','{pgDbname}');"),
            (r"select cron\.schedule_in_database\('GINESYS_STOCK_BOOK_SUMMARY_DELTA_AGG[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_STOCK_BOOK_SUMMARY_DELTA_AGG_{schema_name.upper()}','*/5 * * * *','call db_pro_delta_agg_stock_book_summary()','{pgDbname}');"),
            (r"select cron\.schedule_in_database\('GINESYS_STOCK_AGEING_DELTA_AGG[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_STOCK_AGEING_DELTA_AGG_{schema_name.upper()}','*/5 * * * *','call db_pro_delta_agg_stock_age_analysis()','{pgDbname}');")
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        with open(job_patch_path, 'w') as f1:
            f1.write(content)

        # Connect to the PostgreSQL database and execute the patched SQL
        connection = psycopg2.connect(database=pgDbname, user=pgUserName, password=pgPass, host=pgHost, port=pgPort)
        cursor = connection.cursor()
        cursor.execute(content)
        connection.commit()

        log_window.append(f'Successfully executed job patch {job_patch_path} on database {pgDbname}.')
    except psycopg2.Error as e:
        log_window.append(f'Error executing job patch {job_patch_path} on database {pgDbname}: {e}')
    except Exception as e:
        log_window.append(f'Unexpected error executing job patch {job_patch_path} on database {pgDbname}: {e}')
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
        self.setWindowTitle('Ginesys Migration Application')
        main_layout = QVBoxLayout()
        form_layout = QGridLayout()

        # Oracle credentials
        self.oraHostLabel = QLabel('Oracle Host:')
        self.oraHostInput = QLineEdit()
        self.oraPortLabel = QLabel('Oracle Port:')
        self.oraPortInput = QLineEdit()
        self.oraSchemaLabel = QLabel('Oracle Schema:')
        self.oraSchemaInput = QLineEdit()
        self.oraPassLabel = QLabel('Oracle Password:')
        self.oraPassInput = QLineEdit()
        self.oraServiceLabel = QLabel('Oracle Service:')
        self.oraServiceInput = QLineEdit()

        # PostgreSQL credentials
        self.pgHostLabel = QLabel('PostgreSQL Host:')
        self.pgHostInput = QLineEdit()
        self.pgPortLabel = QLabel('PostgreSQL Port:')
        self.pgPortInput = QLineEdit()
        self.pgUserLabel = QLabel('PostgreSQL Username:')
        self.pgUserInput = QLineEdit()
        self.pgPassLabel = QLabel('PostgreSQL Password:')
        self.pgPassInput = QLineEdit()
        self.pgDbNameLabel = QLabel('PostgreSQL Database Name:')
        self.pgDbNameInput = QLineEdit()

        # Adding widgets to grid layout
        form_layout.addWidget(self.oraHostLabel, 0, 0)
        form_layout.addWidget(self.oraHostInput, 0, 1)
        form_layout.addWidget(self.pgHostLabel, 0, 2)
        form_layout.addWidget(self.pgHostInput, 0, 3)

        form_layout.addWidget(self.oraPortLabel, 1, 0)
        form_layout.addWidget(self.oraPortInput, 1, 1)
        form_layout.addWidget(self.pgPortLabel, 1, 2)
        form_layout.addWidget(self.pgPortInput, 1, 3)

        form_layout.addWidget(self.oraSchemaLabel, 2, 0)
        form_layout.addWidget(self.oraSchemaInput, 2, 1)
        form_layout.addWidget(self.pgUserLabel, 2, 2)
        form_layout.addWidget(self.pgUserInput, 2, 3)

        form_layout.addWidget(self.oraPassLabel, 3, 0)
        form_layout.addWidget(self.oraPassInput, 3, 1)
        form_layout.addWidget(self.pgPassLabel, 3, 2)
        form_layout.addWidget(self.pgPassInput, 3, 3)

        form_layout.addWidget(self.oraServiceLabel, 4, 0)
        form_layout.addWidget(self.oraServiceInput, 4, 1)
        form_layout.addWidget(self.pgDbNameLabel, 4, 2)
        form_layout.addWidget(self.pgDbNameInput, 4, 3)

        button_layout = QHBoxLayout()
        self.updateButton = QPushButton('Update Connections')
        self.updateButton.clicked.connect(self.updateConnections)
        button_layout.addWidget(self.updateButton)

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

        self.patchButton = QPushButton('Execute PostMig SQL')
        self.patchButton.clicked.connect(self.executeSQLPatch)
        button_layout.addWidget(self.patchButton)

        self.createJobsButton = QPushButton('Create Jobs')
        self.createJobsButton.clicked.connect(self.createJobs)
        button_layout.addWidget(self.createJobsButton)

        self.exitButton = QPushButton('Exit')
        self.exitButton.clicked.connect(self.closeApplication)
        button_layout.addWidget(self.exitButton)

        # New button for checking and applying updates
        self.update_app_button = QPushButton('Check and Apply Updates')
        self.update_app_button.clicked.connect(self.checkAndApplyUpdates)
        button_layout.addWidget(self.update_app_button) 

        self.logWindow = QTextEdit()
        self.logWindow.setReadOnly(True)

        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.logWindow)

        self.setLayout(main_layout)
        # Load initial credentials from configuration files
        self.loadCredentialsFromFiles()

    def checkAndApplyUpdates(self):
        checkForUpdates(self.logWindow)
    def loadCredentialsFromFiles(self):
        try:
            # Pre-specified file paths
            global oracon_path
            global pgcon_path

            with open(oracon_path, 'r') as f1:
                content = f1.read()
            schema_match = re.search(r'User Id=([^;]+);', content)
            host_match = re.search(r'HOST=([^)]+)', content)
            port_match = re.search(r'PORT=([^)]+)', content)
            pass_match = re.search(r'Password=([^;]+)', content)
            service_match = re.search(r'SERVICE_NAME=([^)]+)',content)
            if schema_match and host_match and port_match and pass_match and service_match:
                self.oraSchemaInput.setText(schema_match.group(1))
                self.oraHostInput.setText(host_match.group(1))
                self.oraPortInput.setText(port_match.group(1))
                self.oraPassInput.setText(pass_match.group(1))
                self.oraServiceInput.setText(service_match.group(1))
            else:
                self.logWindow.append("Error: Oracle credentials not found in OraCon.txt")

            with open(pgcon_path, 'r') as f1:
                content = f1.read()
            dbname_match = re.search(r'Database=([^;]+);', content)
            pghost_match = re.search(r'Server=([^;]+);', content)
            pgport_match = re.search(r'Port=([^;]+);', content)
            pgpass_match = re.search(r'Password=([^;]+);', content)
            pguser_match = re.search(r'User Id=([^;]+);', content)
            if dbname_match and pghost_match and pgport_match and pguser_match and pgpass_match:
                self.pgDbNameInput.setText(dbname_match.group(1))
                self.pgHostInput.setText(pghost_match.group(1))
                self.pgPortInput.setText(pgport_match.group(1))
                self.pgPassInput.setText(pgpass_match.group(1))
                self.pgUserInput.setText(pguser_match.group(1))
            else:
                self.logWindow.append("Error: PostgreSQL Credentials not found in pgCon.txt")

        except Exception as e:
            self.logWindow.append(f'Error loading credentials from files: {e}')

    def updateConnections(self):
        OraSchema = self.oraSchemaInput.text()
        OraHost = self.oraHostInput.text()
        OraPort = self.oraPortInput.text()
        OraPass = self.oraPassInput.text()
        OraService = self.oraServiceInput.text()
        pgHost = self.pgHostInput.text()
        pgPort = self.pgPortInput.text()
        pgPass = self.pgPassInput.text()
        pgUser = self.pgUserInput.text()
        pgDbName = self.pgDbNameInput.text()

        if not OraSchema or not OraHost or not OraPort or not OraPass or not OraService or not pgHost or not pgPass or not pgUser or not pgDbName or not pgPort:
            QMessageBox.warning(self, 'Input Error', 'Please fill in all fields.')
            return
        try:
            # Pre-specified file paths
            global oracon_path
            global pgcon_path
            global toolkit_path
            global connection_json_path
            global audit_path

            updateOraCon(OraSchema, OraHost,OraPort,OraPass,OraService, oracon_path, self.logWindow)
            updatepgCon(pgHost,pgPort, pgUser,pgPass,pgDbName, pgcon_path, self.logWindow)
            updateToolkit(OraSchema, OraHost,OraPort, OraPass, OraService, pgHost,pgPort, pgUser, pgPass, pgDbName, toolkit_path, self.logWindow)
            updateConnectionJson(OraSchema, OraHost, OraPort, OraPass, OraService, pgHost,pgPort, pgUser, pgPass, pgDbName, connection_json_path, self.logWindow)

            # Copy the files to the destination directory
            success = copyFiles(audit_path, self.logWindow)
            if success:
                QMessageBox.information(self, 'Success', 'Connections updated and files copied successfully.')
            else:
                QMessageBox.critical(self, 'Error', 'An error occurred while copying files.')

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}')
            self.logWindow.append(f'Error updating connections: {e}')

    def executeSQLPatch(self):
        patch_choice = self.patchComboBox.currentText()
        global pgcon_path
        global patch_drill_path
        global patch_live_path
        pgDbname = self.pgDbNameInput.text()
        pgUserName = self.pgUserInput.text()
        pgHost = self.pgHostInput.text()
        pgPort = self.pgPortInput.text()
        pgPass = self.pgPassInput.text()

        if pgDbname:
            if patch_choice == "Drill":
                updatePatchDrill(pgDbname, patch_drill_path, self.logWindow)
                executePatch(pgHost,pgPort,pgUserName,pgPass,pgDbname, patch_drill_path, self.logWindow)  # Example execution after update
            elif patch_choice == "Live Migration":
                updatePatchLive(pgDbname, patch_live_path, self.logWindow)
                executePatch(pgHost,pgPort,pgUserName,pgPass,pgDbname, patch_live_path, self.logWindow)  # Example execution after update
        else:
            QMessageBox.warning(self, 'Database not found', 'Unable to determine database name from pgCon.txt.')

    def createJobs(self):

        global oracon_path
        global pgcon_path
        global job_patch_path

        pgDbname = self.pgDbNameInput.text()
        pgUserName = self.pgUserInput.text()
        pgHost = self.pgHostInput.text()
        pgPort = self.pgPortInput.text()
        pgPass = self.pgPassInput.text()
        schema_name= self.oraSchemaInput.text()

        createJobs(schema_name, pgHost, pgUserName, pgPort, pgPass, pgDbname, job_patch_path, self.logWindow)

    def runMigrationApp(self):
        global migrationapp_path
        self.runExternalApp(migrationapp_path)

    def runAuditApp(self):
        global audittriggerapp_path
        self.runExternalApp(audittriggerapp_path)

    def runCompareToolApp(self):
        global comparetoolapp_path
        self.runExternalApp(comparetoolapp_path)

    def runExternalApp(self, app_path):
        try:
            if sys.platform.startswith('win'):
                subprocess.Popen(f'start cmd /c "{app_path}"', shell=True)
            else:
                self.logWindow.append('Unsupported OS.')
                QMessageBox.critical(self, 'Error', 'Unsupported OS.')
                return

            self.logWindow.append(f'{app_path} executed successfully.')
        except Exception as e:
            self.logWindow.append(f'Error running {app_path}: {e}')
            QMessageBox.critical(self, 'Error', f'Error running {app_path}: {e}')

    def closeApplication(self):
        self.close()

# Entry point for the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    update_app = UpdateConnectionApp()
    update_app.show()
    sys.exit(app.exec_())