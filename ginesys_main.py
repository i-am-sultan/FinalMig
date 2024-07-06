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
    # Prepare the new properties
    oracle_url = f"jdbc:oracle:thin:@{OraHost}:{oracle_port}:{oracle_service}"
    postgres_url = f"jdbc:postgresql://{postgres_host}:{postgres_port}/{postgres_dbname}"
    
    properties_content = (
        f"SRC_DB_URL={oracle_url}\n"
        f"SRC_DB_USER={oracle_user}\n"
        f"SRC_DB_PASSWORD={oracle_password}\n\n"
        f"TARGET_DB_URL={postgres_url}\n"
        f"TARGET_DB_USER={postgres_user}\n"
        f"TARGET_DB_PASSWORD={postgres_password}\n"
    )
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
        oracon_path = r'C:\Program Files\edb\prodmig\RunCMDEdb_New\netcoreapp3.1\OraCon.txt'
        pgcon_path = r'C:\Program Files\edb\prodmig\RunCMDEdb_New\netcoreapp3.1\pgCon.txt'

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
        connection = psycopg2.connect(database=dbname, user='gslpgadmin', password='qs$3?j@*>CA6!#Dy', host="psql-erp-prod-01.postgres.database.azure.com", port=5432)
        cursor = connection.cursor()
        # Execute the SQL content
        cursor.execute(content)
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

def createJobs(schema_name, dbname, job_patch, log_window):
    connection = None
    cursor = None
    
    try:
        with open(job_patch, 'r') as f1:
            content = f1.read()

        patterns = [
            (r"select cron\.schedule_in_database\('GINESYS_AUTO_SETTLEMENT_JOB_[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_AUTO_SETTLEMENT_JOB_{schema_name.upper()}','*/15 * * * *','call main.db_pro_auto_settle_unpost()','{dbname}');"),
            (r"select cron\.schedule_in_database\('GINESYS_DATA_SERVICE_2[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_DATA_SERVICE_2_{schema_name.upper()}','*/1 * * * *','call main.db_pro_gds2_event_enqueue()','{dbname}');"),
            (r"select cron\.schedule_in_database\('GINESYS_INVSTOCK_INTRA_LOG_AGG[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_INVSTOCK_INTRA_LOG_AGG_{schema_name.upper()}','30 seconds','call main.invstock_intra_log_refresh()','{dbname}');"),
            (r"select cron\.schedule_in_database\('GINESYS_INVSTOCK_LOG_AGG[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_INVSTOCK_LOG_AGG_{schema_name.upper()}','30 seconds','call main.invstock_log_refresh()','{dbname}');"),
            (r"select cron\.schedule_in_database\('GINESYS_PERIOD_CLOSURE_JOB[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_PERIOD_CLOSURE_JOB_{schema_name.upper()}','*/2 * * * *','call main.db_pro_period_closure_dequeue()','{dbname}');"),
            (r"select cron\.schedule_in_database\('GINESYS_POS_STLM_AUDIT[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_POS_STLM_AUDIT_{schema_name.upper()}','*/5 * * * *','call main.db_pro_pos_stlm_audit()','{dbname}');"),
            (r"select cron\.schedule_in_database\('GINESYS_RECALCULATE_TAX_JOB[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_RECALCULATE_TAX_JOB_{schema_name.upper()}','*/30 * * * *','call main.db_pro_recalculategst()','{dbname}');"),
            (r"select cron\.schedule_in_database\('GINESYS_STOCK_BOOK_PIPELINE_DELTA_AGG[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_STOCK_BOOK_PIPELINE_DELTA_AGG_{schema_name.upper()}','*/5 * * * *','call db_pro_delta_agg_pipeline_stock()','{dbname}');"),
            (r"select cron\.schedule_in_database\('GINESYS_STOCK_BOOK_SUMMARY_DELTA_AGG[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_STOCK_BOOK_SUMMARY_DELTA_AGG_{schema_name.upper()}','*/5 * * * *','call db_pro_delta_agg_stock_book_summary()','{dbname}');"),
            (r"select cron\.schedule_in_database\('GINESYS_STOCK_AGEING_DELTA_AGG[^']+','[^']+','[^']+','[^']+'\);",
             f"select cron.schedule_in_database('GINESYS_STOCK_AGEING_DELTA_AGG_{schema_name.upper()}','*/5 * * * *','call db_pro_delta_agg_stock_age_analysis()','{dbname}');")
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        with open(job_patch, 'w') as f1:
            f1.write(content)

        # Connect to the PostgreSQL database and execute the patched SQL
        connection = psycopg2.connect(database='postgres', user='gslpgadmin', password='qs$3?j@*>CA6!#Dy', host="psql-erp-prod-01.postgres.database.azure.com", port=5432)
        cursor = connection.cursor()
        cursor.execute(content)
        connection.commit()

        log_window.append(f'Successfully executed job patch {job_patch} on database {dbname}.')
    except psycopg2.Error as e:
        log_window.append(f'Error executing job patch {job_patch} on database {dbname}: {e}')
    except Exception as e:
        log_window.append(f'Unexpected error executing job patch {job_patch} on database {dbname}: {e}')
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
            oracon_path = r'C:\Program Files\edb\prodmig\RunCMDEdb_New\netcoreapp3.1\OraCon.txt'
            pgcon_path = r'C:\Program Files\edb\prodmig\RunCMDEdb_New\netcoreapp3.1\pgCon.txt'
            toolkit_path = r'C:\Program Files\edb\mtk\etc\toolkit.properties'
            connection_json_path = r'C:\Program Files\edb\prodmig\Ora2PGCompToolKit\Debug\Connection.json'

            updateOraCon(OraSchema, OraHost, oracon_path, self.logWindow)
            updatepgCon(pgDbName, pgcon_path, self.logWindow)
            updateToolkit(OraSchema, OraHost, pgDbName, toolkit_path, self.logWindow)
            updateConnectionJson(OraSchema, OraHost, pgDbName, connection_json_path, self.logWindow)

            # Copy the files to the destination directory
            destination_dir = r'C:\Program Files\edb\prodmig\AuditTriggerCMDNew\netcoreapp3.1'
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
        pgCon_path = r'C:\Program Files\edb\prodmig\RunCMDEdb_New\netcoreapp3.1\pgCon.txt'

        with open(pgCon_path, 'r') as file:
            content = file.read()
        dbname_match = re.search(r'Database=([^;]+)', content)
        if dbname_match:
            pgDbname = dbname_match.group(1)

            if patch_choice == "Drill":
                patch_drill = r'C:\Program Files\edb\prodmig\PostMigPatches\patch_drill.sql'
                updatePatchDrill(pgDbname, patch_drill, self.logWindow)
                executePatch(pgDbname, patch_drill, self.logWindow)  # Example execution after update
            elif patch_choice == "Live Migration":
                patch_live = r'C:\Program Files\edb\prodmig\PostMigPatches\patch_live.sql'
                updatePatchLive(pgDbname, patch_live, self.logWindow)
                executePatch(pgDbname, patch_live, self.logWindow)  # Example execution after update
        else:
            QMessageBox.warning(self, 'Database not found', 'Unable to determine database name from pgCon.txt.')

    def createJobs(self):
        oracon_path = r'C:\Program Files\edb\prodmig\RunCMDEdb_New\netcoreapp3.1\OraCon.txt'
        pgcon_path = r'C:\Program Files\edb\prodmig\RunCMDEdb_New\netcoreapp3.1\pgCon.txt'
        job_patch = r'C:\Program Files\edb\prodmig\PostMigPatches\patch_jobs.sql'

        with open(oracon_path, 'r') as f1:
            content = f1.read()
        schema_match = re.search(r'User Id=([^;]+)', content)
        if schema_match:
            schema_name = schema_match.group(1)
            self.logWindow.append(f"Schema name found: {schema_name}")
        else:
            self.logWindow.append("Schema name not found in OraCon.txt")
            return

        with open(pgcon_path, 'r') as file:
            content = file.read()
        dbname_match = re.search(r'Database=([^;]+)', content)
        if dbname_match:
            dbname = dbname_match.group(1)
            self.logWindow.append(f"Database name found: {dbname}")
        else:
            self.logWindow.append("Database name not found in pgCon.txt")
            return

        createJobs(schema_name, dbname, job_patch, self.logWindow)

    def runMigrationApp(self):
        migrationapp = r'C:\Program Files\edb\prodmig\RunCMDEdb_New\netcoreapp3.1\RunEDBCommand.exe'
        self.runExternalApp(migrationapp)

    def runAuditApp(self):
        audittriggerapp = r'C:\Program Files\edb\prodmig\AuditTriggerCMDNew\netcoreapp3.1\TriggerConstraintViewCreationForAuditPostMigration.exe'
        self.runExternalApp(audittriggerapp)

    def runCompareToolApp(self):
        comparetoolapp = r'C:\Program Files\edb\prodmig\Ora2PGCompToolKit\Debug\OraPostGreSqlComp.exe'
        self.runExternalApp(comparetoolapp)

    def runExternalApp(self, app_path):
        try:
            if sys.platform.startswith('win'):
                subprocess.Popen(f'start cmd /c "{app_path}"', shell=True)
            elif sys.platform.startswith('linux'):
                subprocess.Popen(['gnome-terminal', '--', app_path])
            elif sys.platform.startswith('darwin'):
                subprocess.Popen(['open', '-a', 'Terminal', app_path])
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