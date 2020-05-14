export GOOGLE_APPLICATION_CREDENTIALS=key.json

# Create folder
sudo mkdir /cloudsql

# Give permissions
sudo chown -R $USER /cloudsql

# Connect existing CloudSQL with credential file
./cloud_sql_proxy -dir=/cloudsql --instances=$CLOUD_SQL_CONNECTION_NAME --credential_file=$GOOGLE_APPLICATION_CREDENTIALS
