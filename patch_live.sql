CREATE EXTENSION DBLINK;
CREATE SERVER foreign_pgbase
    FOREIGN DATA WRAPPER dblink_fdw
    OPTIONS (dbname 'db', host 'psql-erp-prod-01.postgres.database.azure.com', port '5432');

ALTER SERVER foreign_pgbase
    OWNER TO gslpgadmin;
CREATE USER MAPPING FOR gslpgadmin SERVER foreign_pgbase
    OPTIONS (password 'qs$3?j@*>CA6!#Dy', "user" 'gslpgadmin');
    
DO $$  
DECLARE
    DTFR DATE;
BEGIN
    SELECT CURRENT_DATE - (365+180)
    INTO DTFR;
    --FOR SITE_TO_SITE:
    call main.db_pro_sitetositemovement_firsttimepopulation_outward(DTFR, CURRENT_DATE);
    call main.db_pro_sitetositemovement_firsttimepopulation_inward(DTFR, CURRENT_DATE);
    call main.db_pro_sitetositemovement_not_in_outward();
    call main.db_proc_sitetosite_intransum(DTFR); --start DATE
    --FOR COMPOSITE_GST:
    call main.db_pro_compositegst_firsttimepopulation(DTFR, CURRENT_DATE);
    --FOR STOCK BOOK SUMMARY:
    call main.db_pro_stk_bk_summary_master_build(DTFR);
END $$