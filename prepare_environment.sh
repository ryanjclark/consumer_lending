# echo "Creating Datastore/App Engine instance"
# gcloud app create --region "us-central"

# echo "Creating bucket: gs://consumer-loan-bucket"
# gsutil mb gs://consumer-loan-bucket

echo "Exporting GCLOUD_PROJECT and GCLOUD_BUCKET"
export GCLOUD_PROJECT=$DEVSHELL_PROJECT_ID
export GCLOUD_BUCKET=consumer-loan-bucket

# echo "Creating virtual environment"
# mkdir ~/venvs
# virtualenv -p python3 ~/venvs/developingapps
# source ~/venvs/developingapps/bin/activate

echo "Installing Python libraries"
pip install --upgrade pip
pip install -r requirements.txt

echo "Creating Cloud Pub/Sub topic"
gcloud beta pubsub topics create lending-descr
gcloud beta pubsub subscriptions create worker-subscription --topic lending-descr

echo "Project ID: $DEVSHELL_PROJECT_ID"
