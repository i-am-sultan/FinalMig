import re
import psycopg2

def createJobs(schema_name, dbname, job_patch):
    print(schema_name,dbname)
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

    with open(job_patch,'w') as f1:
        f1.write(content)

    # Establish connection and execute the patched SQL
    # print(f"Connecting to database '{dbname}'...")
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
    oracon_path = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\OraCon.txt'
    pgCon_path = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\pgCon.txt'
    job_patch = r'C:\Users\sultan.m\Documents\GitHub\FinalMig\patch_jobs.sql'

    with open(oracon_path, 'r') as f1:
        content = f1.read()
    schema_match = re.search(r'User Id=([^;]+)', content)
    if schema_match:
        schema_name = schema_match.group(1)
        print(f"Schema name found: {schema_name}")
    else:
        print("Schema name not found in OraCon.txt")
        exit(1)

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
    if inp == 1 or inp == 2:
        createJobs(schema_name, dbname, job_patch)
    else:
        print("Invalid input. Exiting...")
