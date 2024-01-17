import os
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from sklearn.preprocessing import MinMaxScaler

# Directory path
directory = 'C:/Users/Ardra/PycharmProjects/pythonProject2/MobiFall_Dataset_v2.0_labelled/'

# Function to list files in the directory
def list_files(directory):
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if 'acc' in file:
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
    return file_paths

# Function to load dataframes from files
def load_dataframes(file_paths):
    dataframes = []
    for file_path in file_paths:
        df = pd.read_csv(file_path, sep=',')
        dataframes.append(df)
    return dataframes

def display_results(model_name, accuracy, confusion_matrix_result):
    print(f"Results for {model_name}:")
    print(f"Accuracy: {accuracy}")
    print("Confusion Matrix:")
    print(confusion_matrix_result)
    print("\n")

# Load dataframes
dataframes = load_dataframes(list_files(directory))

# Concatenate dataframes
df_concatenated = pd.concat(dataframes, ignore_index=True)

# Create a new column for binary labels
df_concatenated['binary_fall'] = df_concatenated['fall'].apply(lambda x: 1 if x in [10, 11, 12, 13] else 0)

# Separate features and target variable
X = df_concatenated.drop(['fall', 'binary_fall'], axis=1)
Y_binary = df_concatenated['binary_fall']

# Train-test split on the entire dataset
X_train, X_test, Y_train, Y_test = train_test_split(X, Y_binary, test_size=0.2, random_state=42, stratify=Y_binary)

# Normalize features using MinMaxScaler
scaler = MinMaxScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


# Create a representative subset for hyperparameter tuning just with train set
X_subset_train, _, Y_subset_train, _ = train_test_split(X_train, Y_train, test_size=0.99, random_state=42, stratify=Y_train)

# Write the subset to a file
subset_df = pd.DataFrame(X_subset_train, columns=X.columns)
subset_df['binary_fall'] = Y_subset_train
subset_df.to_csv(r'C:\Users\Ardra\PycharmProjects\pythonProject2\subset_data_test.csv', index=False)


# Train Normal Random Forest on the training set
print("Training Normal Random Forest on the training set...")
rf_normal = RandomForestClassifier(random_state=42)
rf_normal.fit(X_subset_train, Y_subset_train)
Y_pred_normal_rf = rf_normal.predict(X_test)
accuracy_normal_rf = accuracy_score(Y_test, Y_pred_normal_rf)
cm_normal_rf = confusion_matrix(Y_test, Y_pred_normal_rf)
print("Normal Random Forest trained and evaluated.\n")

# Define search space for hyperparameter tuning
param_grid_rf_tuned = {
    'n_estimators': [150, 200, 250, 300],
    'max_depth': [None, 8, 10, 12],
    'min_samples_split': [2, 3, 4],
    'min_samples_leaf': [1, 2, 3],
    'bootstrap': [True]
}



# Initialize GridSearchCV for tuning on the subset
grid_search_rf_tuned = GridSearchCV(
    estimator=RandomForestClassifier(random_state=42),
    param_grid=param_grid_rf_tuned,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)

# Performing GridSearchCV for Hyperparameter Tuned RandomForest on the subset
print("Performing GridSearchCV for Hyperparameter Tuned RandomForest on the subset...")
grid_search_rf_tuned.fit(X_subset_train, Y_subset_train)
print("Hyperparameter Tuned RandomForest  trained and evaluated.\n")

# Best hyperparameters for the tuned RandomForest
best_rf_tuned = grid_search_rf_tuned.best_estimator_

# Make predictions with the best estimator on the testing set
best_rf_pred = best_rf_tuned.predict(X_test)
accuracy_rftuned = accuracy_score(Y_test, best_rf_pred)
cm_rftuned = confusion_matrix(Y_test, best_rf_pred)


# Training Normal AdaBoost
print("Training Normal AdaBoost...")
ada_normal = AdaBoostClassifier(random_state=42)
ada_normal.fit(X_subset_train, Y_subset_train)
Y_pred_normal_ada = ada_normal.predict(X_test)
accuracy_normal_ada = accuracy_score(Y_test, Y_pred_normal_ada)
cm_normal_ada = confusion_matrix(Y_test, Y_pred_normal_ada)
print("Normal AdaBoost trained and evaluated.\n")

# Training Normal XGBoost
print("Training Normal XGBoost...")
xgb_normal = XGBClassifier(random_state=42)
xgb_normal.fit(X_subset_train, Y_subset_train)
Y_pred_normal_xgb = xgb_normal.predict(X_test)
accuracy_normal_xgb = accuracy_score(Y_test, Y_pred_normal_xgb)
cm_normal_xgb = confusion_matrix(Y_test, Y_pred_normal_xgb)
print("Normal XGBoost trained and evaluated.\n")

# Training AdaBoost with Hyperparameter-tuned RandomForest as Base
print("Training AdaBoost with Hyperparameter-tuned RandomForest as Base...")
ada_tuned_rf = AdaBoostClassifier(base_estimator=best_rf_tuned, random_state=42)
ada_tuned_rf.fit(X_subset_train, Y_subset_train)
Y_pred_ada_tuned_rf = ada_tuned_rf.predict(X_test)
accuracy_ada_tuned_rf = accuracy_score(Y_test, Y_pred_ada_tuned_rf)
cm_ada_tuned_rf = confusion_matrix(Y_test, Y_pred_ada_tuned_rf)
print("AdaBoost with Hyperparameter-tuned RandomForest as Base trained and evaluated.\n")


# Training XGBoost with Hyperparameter-tuned RandomForest as Base
print("Training XGBoost with Hyperparameter-tuned RandomForest as Base...")
xgb_tuned_rf = XGBClassifier(random_state=42)
xgb_tuned_rf.set_params(**best_rf_tuned.get_params())
xgb_tuned_rf.fit(X_subset_train, Y_subset_train)
Y_pred_xgb_tuned_rf = xgb_tuned_rf.predict(X_test)
accuracy_xgb_tuned_rf = accuracy_score(Y_test, Y_pred_xgb_tuned_rf)
cm_xgb_tuned_rf = confusion_matrix(Y_test, Y_pred_xgb_tuned_rf)
print("XGBoost with Hyperparameter-tuned RandomForest as Base trained and evaluated.\n")

# Displaying Results
display_results("Normal_RF", accuracy_normal_rf, cm_normal_rf)
display_results("Tuned_RF", accuracy_rftuned, cm_rftuned)
display_results("Normal_AdaBoost", accuracy_normal_ada, cm_normal_ada)
display_results("Normal_XGBoost", accuracy_normal_xgb, cm_normal_xgb)
display_results("AdaBoost_Tuned_RF", accuracy_ada_tuned_rf, cm_ada_tuned_rf)
display_results("XGBoost_Tuned_RF", accuracy_xgb_tuned_rf, cm_xgb_tuned_rf)

# With SMOTE

# Define a new pipeline that includes SMOTE and XGBoost Tuned
xgb_smote_tuned_rf = Pipeline([
    ('smote', SMOTE()),
    ('xgb_tuned_rf', xgb_tuned_rf)
])
# Fit the new pipeline to the training data
xgb_smote_tuned_rf.fit(X_subset_train, Y_subset_train)
# Make predictions on the test data using the new pipeline
Y_pred_xgb_smote_tuned_rf = xgb_smote_tuned_rf.predict(X_test)
# Calculate the accuracy score and confusion matrix for the new pipeline
accuracy_xgb_smote_tuned_rf = accuracy_score(Y_test, Y_pred_xgb_smote_tuned_rf)
cm_xgb_smote_tuned_rf = confusion_matrix(Y_test, Y_pred_xgb_smote_tuned_rf)

# Display the results for XGBoost Tuned with SMOTE
display_results("XGBoost_Tuned_RF_with_SMOTE", accuracy_xgb_smote_tuned_rf, cm_xgb_smote_tuned_rf)