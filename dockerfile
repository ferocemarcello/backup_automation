#sudo docker build -t backup_image .
#sudo docker run -v ./:/app backup_image python ./notion_exporter.py --output notion_workspace.json --token notion_token
#sudo docker run -v ./:/app backup_image bash ./bitwarden_exporter.sh "your_client_id" "your_client_secret" "your_master_password"
#sudo docker run -v ./:/app backup_image python ./upload_to_drive.py --folder_id drive_folder --file_path ./backup/notion_workspace.json --file_name notion_workspace.json --service_account ./backupautomation_service_account_key.json
#sudo docker run -v ./:/app backup_image python ./upload_to_drive.py --folder_id drive_folder --file_path ./backup/bitwarden_vault.json --file_name bitwarden_vault.json --service_account ./backupautomation_service_account_key.json

# Use an official Alpine image as a base
FROM alpine:3.18

# Install Python 3.11, pip, npm, and other dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    npm \
    bash \
    jq \
    && pip install --upgrade pip

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Install the Python dependencies from requirements.txt
RUN pip install -r requirements.txt

# Install Bitwarden CLI globally using npm
RUN npm install -g @bitwarden/cli

# Set CMD to allow the container to run any script passed at runtime
CMD ["bash"]
