import configparser

def update_properties_file():
    config = configparser.ConfigParser()

    # Prepare the new properties
    oracle_url = f"jdbc:oracle:thin:@{oracle_host}:{oracle_port}:{oracle_service}"
    postgres_url = f"jdbc:postgresql://{postgres_host}:{postgres_port}/{postgres_dbname}"
    
    properties_content = (
        f"SRC_DB_URL={oracle_url}\n"
        f"SRC_DB_USER={oracle_user}\n"
        f"SRC_DB_PASSWORD={oracle_password}\n\n"
        f"TARGET_DB_URL={postgres_url}\n"
        f"TARGET_DB_USER={postgres_user}\n"
        f"TARGET_DB_PASSWORD={postgres_password}\n"
    )

    # Write the updated properties to file
    with open(toolkit_path, 'w') as configfile:
            configfile.write(properties_content)
    
    with open(toolkit_path,'r') as fileread:
        content = fileread.read()
    print(content)

# Run the update function
update_properties_file()
