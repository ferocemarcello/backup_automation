#!/bin/bash
#sudo docker run -v ./:/app backup_image bash ./bitwarden_exporter.sh "your_client_id" "your_client_secret" "your_master_password" "bitwarden_vault_path"

# Check if the correct number of arguments are passed
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <client_id> <client_secret> <master_password> <bitwarden_vault_path>"
    exit 1
fi

# Assign command-line arguments to variables
BW_CLIENTID=$1
BW_CLIENTSECRET=$2
BW_PASSWORD=$3
BITWARDEN_VAULT_PATH=$4

# Export the BW_PASSWORD variable so it can be used by bw unlock
export BW_PASSWORD

bw logout

# Log in to Bitwarden using the API key
BW_CLIENTID=$BW_CLIENTID BW_CLIENTSECRET=$BW_CLIENTSECRET bw login --apikey

# Unlock the vault (this will require your master password)
BW_SESSION=$(bw unlock --raw --passwordenv BW_PASSWORD)

# Check if the vault was unlocked successfully
if [ -z "$BW_SESSION" ]; then
    echo "Failed to unlock the vault."
    exit 1
fi

# Export the vault data as JSON
VAULT_DATA=$(bw list items --session "$BW_SESSION")

# Check if the vault data was retrieved successfully
if [ -z "$VAULT_DATA" ]; then
    echo "Failed to retrieve vault data."
    exit 1
fi

# Extract the directory path from BITWARDEN_VAULT_PATH
VAULT_DIR=$(dirname "$BITWARDEN_VAULT_PATH")

# Check if the directory exists, if not, create it
if [ ! -d "$VAULT_DIR" ]; then
    echo "Directory $VAULT_DIR does not exist. Creating it..."
    mkdir -p "$VAULT_DIR"
    if [ $? -ne 0 ]; then
        echo "Failed to create directory $VAULT_DIR. Exiting."
        exit 1
    fi
fi

# Set full permissions for everyone on the directory
chmod 777 "$VAULT_DIR"

# Format the JSON data using jq and save it to a JSON file with the provided file name
echo "$VAULT_DATA" | jq '.' > "$BITWARDEN_VAULT_PATH"

# Check if the vault data was saved successfully
if [ $? -eq 0 ]; then
    echo "Vault data saved successfully to $BITWARDEN_VAULT_PATH"
    # Set full permissions for everyone on the file
    chmod 777 "$BITWARDEN_VAULT_PATH"
else
    echo "Failed to save vault data to $BITWARDEN_VAULT_PATH"
    exit 1
fi

# Optionally log out of Bitwarden
bw logout
