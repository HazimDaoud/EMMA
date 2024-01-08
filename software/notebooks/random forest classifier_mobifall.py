import os
import pandas as pd
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,confusion_matrix




def list_files(directory):
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if 'acc' in file:
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
    return file_paths

def load_dataframes(directory):
    dataframes = []
    for file_path in list_files(directory):
        df = pd.read_csv(file_path, sep=',')
        dataframes.append(df)
    return dataframes

def concatenate_dataframes(dataframes):
    df_concatenated = pd.concat(dataframes, ignore_index=True)
    return df_concatenated

directory = 'C:/Users/Ardra/PycharmProjects/pythonProject2/MobiFall_Dataset_v2.0_labelled/'
dataframes = load_dataframes(directory)
df_concatenated = concatenate_dataframes(dataframes)
df_concatenated = df_concatenated.drop('timestamp', axis=1)

scaler = MinMaxScaler()
df_normalized = scaler.fit_transform(df_concatenated)
df_normalized = pd.DataFrame(df_normalized, columns=df_concatenated.columns)

# Ensure the 'y' column has only two distinct values
print('Distribution of the y column:')
print(df_normalized['fall'].value_counts())

df_normalized['fall'] = df_normalized['fall'].apply(lambda x: 0 if x < 0.5 else 1)
print('Modified Distribution of the y column:')
print(df_normalized['fall'])

X = df_normalized.drop('fall', axis=1)
y = df_normalized['fall']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Calculate class weights to handle imbalance
class_weights = dict(zip([0, 1], len(df_normalized) / (2 * df_normalized['fall'].value_counts())))

clf = RandomForestClassifier(n_estimators=100, class_weight=class_weights, random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print('Accuracy:', accuracy_score(y_test, y_pred))
# Confusion matrix
print('Confusion Matrix:')
confMat=confusion_matrix(y_test, y_pred)
confMat
plt.figure()
sns.heatmap(confMat.astype('int') , annot=True, fmt='0.2f', cmap='Blues', xticklabels=[0, 1], yticklabels=[0, 1])
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.show()
