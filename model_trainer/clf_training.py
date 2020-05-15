import datetime
import os
import subprocess
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle


BUCKET_FOLDER = 'lending-274219.appspot.com/models'
data_filename = 'loans.csv'
target_filename = 'targets.csv'
data_dir = 'gs://lending-274219.appspot.com/data/'

# gsutil outputs everything to stderr so we need to divert it to stdout.
subprocess.check_call(['gsutil', 'cp', os.path.join(data_dir,
                                                    data_filename),
                       data_filename], stderr=sys.stdout)

subprocess.check_call(['gsutil', 'cp', os.path.join(data_dir,
                                                    target_filename),
                       target_filename], stderr=sys.stdout)

# Define df from csv, training df
start_df = pd.read_csv(data_filename, header=None,
                       names = ["emp_length_cat",
                                "home_status", "zip3", "total_acc",
                                "annual_inc", "dti", "descr", "scores"])
X_train = start_df.drop(['descr'], axis=1)
targets_df = pd.read_csv(target_filename, header=None)
y_train = targets_df

clf_rf = RandomForestClassifier(n_estimators=10, random_state=21)
clf_rf.fit(X_train, np.ravel(y_train))

# Export model to a file
model_filename = 'model.pkl'
with open('model.pkl', 'wb') as model_file:
    pickle.dump(clf_rf, model_file)

# Upload the saved model file to Cloud Storage
gcs_model_path = os.path.join('gs://', BUCKET_FOLDER,
    datetime.datetime.now().strftime('clf_%Y%m%d_%H%M%S'), model_filename)
subprocess.check_call(['gsutil', 'cp', model_filename, gcs_model_path],
    stderr=sys.stdout)
