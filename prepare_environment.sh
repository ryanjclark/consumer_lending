# echo "Creating Datastore/App Engine instance"
# gcloud app create --region "us-central"

echo "Creating bucket: gs://consumer-loan-bucket"
gsutil mb gs://consumer-loan-bucket

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

echo "Creating Datastore entities"
python add_entities.py

echo "Creating lending-account Service Account"
gcloud iam service-accounts create lending-account --display-name "Lending Account"
gcloud iam service-accounts keys create key.json --iam-account=lending-account@$DEVSHELL_PROJECT_ID.iam.gserviceaccount.com
export GOOGLE_APPLICATION_CREDENTIALS=key.json

echo "Setting lending-account IAM Role"
gcloud projects add-iam-policy-binding $DEVSHELL_PROJECT_ID --member serviceAccount:lending-account@$DEVSHELL_PROJECT_ID.iam.gserviceaccount.com --role roles/owner

echo "Project ID: $DEVSHELL_PROJECT_ID"
