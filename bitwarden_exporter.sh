#!/bin/bash
#sudo docker run -v ./:/app backup_image bash ./bitwarden_exporter.sh "your_client_id" "your_client_secret" "your_master_password" "vault_file_name"

# Check if the correct number of arguments are passed
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <client_id> <client_secret> <master_password> <vault_file_name>"
    exit 1
fi

# Assign command-line arguments to variables
BW_CLIENTID=$1
BW_CLIENTSECRET=$2
BW_PASSWORD=$3
VAULT_FILE_NAME=$4
BACKUP_FOLDER=$5 #including "/" at the end

# Export the BW_PASSWORD variable so it can be used by bw unlock
export BW_PASSWORD

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

# Format the JSON data using jq and save it to a JSON file with the provided file name
echo "$VAULT_DATA" | jq '.' > "$BACKUP_FOLDER"$VAULT_FILE_NAME"

echo "Vault data exported successfully to $VAULT_FILE_NAME"

# Optionally log out of Bitwarden
bw logout
