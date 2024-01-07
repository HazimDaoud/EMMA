import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report

# Read the dataset
data = pd.read_csv('/dummy_data_all_shuffled')

# Map labels to 'ADL' and 'Fall'
data["fall"] = data["fall"].map({0: "ADL", 1: "Fall"})

# Select features (x) and labels (y)
x = data[['accelerometer_x','accelerometer_y','accelerometer_z','gyroscope_x','gyroscope_y','gyroscope_z']]
y = data['fall']

# Split the data into training and testing sets
xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.20, random_state=42)

# Calculate class weights to handle imbalance
class_weights = dict(zip(['ADL', 'Fall'], len(data) / (2 * data['fall'].value_counts())))

# Create a Random Forest classifier with class weights
rf_model = RandomForestClassifier(n_estimators=100, class_weight=class_weights, random_state=42)

# Train the Random Forest model
rf_model.fit(xtrain, ytrain)

# Make predictions on the test set
rf_prediction = rf_model.predict(xtest)

# Evaluate the performance using confusion matrix
confus_rf = confusion_matrix(ytest, rf_prediction)

# Evaluate the performance using classification report
confus_report_rf = classification_report(ytest, rf_prediction)

# Print the results
print("Random Forest Confusion Matrix:\n", confus_rf)
print("\nRandom Forest Classification Report:\n", confus_report_rf)
