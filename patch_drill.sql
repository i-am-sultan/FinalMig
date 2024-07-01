DELETE FROM Psite_Posapiconfig;
DELETE FROM Psite_webdb_configuration;
UPDATE GDS2_Subscr SET webhookurl = NULL;

CREATE EXTENSION DBLINK;
CREATE SERVER foreign_pgbase
    FOREIGN DATA WRAPPER dblink_fdw
    OPTIONS (dbname 'prod', host 'psql-erp-prod-01.postgres.database.azure.com', port '5432');

ALTER SERVER foreign_pgbase
    OWNER TO gslpgadmin;
CREATE USER MAPPING FOR gslpgadmin SERVER foreign_pgbase
    OPTIONS (password 'qs$3?j@*>CA6!#Dy', "user" 'gslpgadmin');
