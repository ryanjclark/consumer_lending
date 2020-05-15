export BUCKET_NAME=lending-274219.appspot.com
export JOB_NAME="scikit_learn_$(date +"%Y%m%d_%H%M%S")"
export JOB_DIR=gs://$BUCKET_NAME/scikit_learn_job_dir
export TRAINING_PACKAGE_PATH="./model_trainer/"
export MAIN_TRAINER_MODULE="model_trainer.clf_training"
export REGION=us-central1
export RUNTIME_VERSION=1.15
export PYTHON_VERSION=3.7
export SCALE_TIER=BASIC