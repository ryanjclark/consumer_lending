echo "Exporting GCLOUD_PROJECT and GCLOUD_BUCKET and GOOGLE_APPLICATION_CREDENTIALS"
export GCLOUD_PROJECT=$DEVSHELL_PROJECT_ID
export GCLOUD_BUCKET=$DEVSHELL_PROJECT_ID-media
export GOOGLE_APPLICATION_CREDENTIALS=key.json

# echo "Switching to virtual environment"
# source ~/venvs/developingapps/bin/activate

echo "Starting worker"
python -m flaskapp.console.worker