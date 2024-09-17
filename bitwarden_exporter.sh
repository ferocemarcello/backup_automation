#!/bin/bash

# Replace these with your Bitwarden API Key details
BW_CLIENTID="clientid"
BW_CLIENTSECRET="secret"
BW_PASSWORD="password"

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

# Format the JSON data using jq and save it to a JSON file
echo "$VAULT_DATA" | jq '.' > /app/backup/bitwarden_vault.json

echo "Vault data exported successfully to bitwarden_vault.json"

# Optionally log out of Bitwarden
bw logout
