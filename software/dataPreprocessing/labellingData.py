import pandas as pd
import os
import helpers
from io import StringIO

def addTargetVariable(filename):

    return 1 if 'fall' in filename.lower() else 0

def labelSingle_csvfile(filename):

    df = pd.read_csv(filename, header=None)
    df.columns = ['accelerometer_x', 'accelerometer_y', 'accelerometer_z', 'gyroscope_x', 'gyroscope_y', 'gyroscope_z']
    df['fall'] = addTargetVariable(filename)
    return df

def labelMultiple_Csvfiles(directiory):

    csvFiles = [file for file in os.listdir(directiory) if file.endswith('.csv')]
    columns = ['accelerometer_x', 'accelerometer_y', 'accelerometer_z', 'gyroscope_x', 'gyroscope_y', 'gyroscope_z']
    finalDf = pd.DataFrame(columns=columns)
    for file in csvFiles:
        filepath = os.path.join(directiory, file)
        df = pd.read_csv(filepath, header=None)
        df.columns = columns
        df['fall'] = addTargetVariable(filepath)
        finalDf = pd.concat([finalDf, df], ignore_index=True)
    return finalDf

def readData_fromMobitxt(filepath):
    with open(filepath, 'r') as file:

        for i, line in enumerate(file):
            if line.startswith('@DATA'):
                break

        data_content = file.read()
    df = pd.read_csv(StringIO(data_content), delimiter=',', header=None)
    if 'acc' in filepath:
        df.columns = ['timestamp', 'accelerometer_x', 'accelerometer_y', 'accelerometer_z']
    elif 'gyro' in filepath:
        df.columns = ['timestamp', 'gyroscope_x', 'gyroscope_y', 'gyroscope_z']
    elif 'ori' in filepath:
        df.columns = ['timestamp', 'azimuth', 'pitch', 'roll']
    # df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ns')

    return df

def labelMobi(df, filepath):
    activityMap = {
    "STD":1,
    "WAL":2,
    "JOG":3,
    "JUM":4,
    "STU":5,
    "STN":6,
    "SCH":7,
    "CSI":8,
    "CSO":9,
    "BSC": 12,
    "FKL": 11,
    "FOL": 10,
    "SDL": 14,
    }
    activityLabel = next((activity for activity in activityMap if activity in filepath), None)
    target_value = activityMap.get(activityLabel, None)
    df['fall'] = target_value

def processActivityDirs(activityPath):
    baseDirectory_raw = "MobiFall_Dataset_v2.0_raw"
    baseDirectory_labelled = "MobiFall_Dataset_v2.0_labelled"
    filepathLabelled = activityPath.replace(baseDirectory_raw, baseDirectory_labelled)
    for filename in os.listdir(activityPath):
        filepath = os.path.join(activityPath, filename)
        if os.path.isfile(filepath):
            df = readData_fromMobitxt(filepath)
            labelMobi(df, filepath)
            helpers.saveDataframe_as_csvfile(df, filepathLabelled, filename+"_labelled")

def processSubdirectory(rootDirectory, activityType):
    activityDirectoryPath = os.path.join(rootDirectory, activityType)
    subdirectoriesMap = {
        'FALLS': ['BSC', 'FKL', 'FOL', 'SDL'],
        'ADL': ['STD', 'WAL', 'JOG', 'JUM', 'STU', 'STN', 'SCH', 'CSI', 'CSO']
    }
    if os.path.exists(activityDirectoryPath):
        expectedSubdirectories = subdirectoriesMap.get(activityType, [])

        for subdirectory in expectedSubdirectories:
            subdirectoryPath = os.path.join(activityDirectoryPath, subdirectory)

            if os.path.exists(subdirectoryPath):
                processActivityDirs(subdirectoryPath)

def readSubsCsvs(subdir):
    dfs = []
    for root, dirs, files in os.walk(subdir):
        for file in files:
            if "acc" in file:
                filepath = os.path.join(root, file)
                df = pd.read_csv(filepath)
                dfs.append(df)

    if dfs:
        finalDf = pd.concat(dfs, ignore_index=True)
        return finalDf

def preprocess_fallalld(fallalld):
    fallalld = fallalld[fallalld['Device'] == 'Waist']
    count = 0

    for subject_id, subject_group in fallalld.groupby('SubjectID'):
        for activity_id, activity_group in subject_group.groupby('ActivityID'):
            for trial_no, trial_group in activity_group.groupby('TrialNo'):
                acc_data = trial_group['Acc'].iloc[0]
                acc = pd.DataFrame(acc_data, columns=['accelerometer_x', 'accelerometer_y', 'accelerometer_z'])
                acc['fall'] = 1 if activity_id > 100 else 0
                # Example of creating lagged features
                acc['x_lag_1'] = acc['accelerometer_x'].shift(1)
                acc['x_lag_2'] = acc['accelerometer_x'].shift(2)
                acc['y_lag_1'] = acc['accelerometer_y'].shift(1)
                acc['y_lag_2'] = acc['accelerometer_y'].shift(2)
                acc['z_lag_1'] = acc['accelerometer_z'].shift(1)
                acc['z_lag_2'] = acc['accelerometer_z'].shift(2)
                name = f'acc_{count}'
                acc.to_csv(os.path.join('..', '..', 'dataSets', 'FallAllD_labelled', f'{name}.csv'), index=False)
                count += 1

    return fallalld

def main():
    ## Sensor
    # directory = 'dataSets/dummy_data_raw'
    # df = labelMultiple_Csvfiles(directory)
    # helpers.saveDataframe_as_csvfile(df,'dataSets/dummy_data_labelled', 'dummy_data_all' )
    # dfShuffled = helpers.shuffleDataframe(df)
    # helpers.saveDataframe_as_csvfile(df,'dataSets/dummy_data_labelled', 'dummy_data_all_shuffled' )

    ##Mobi
    rootDirectory =  "../../dataSets/MobiFall_Dataset_v2.0_raw"
    for sub_directory in os.listdir(rootDirectory):
        sub_directory_path = os.path.join('..', '..', rootDirectory, sub_directory)
        processSubdirectory(sub_directory_path, 'FALLS')
        processSubdirectory(sub_directory_path, 'ADL')

    ##FallAllD_raw
    fallalld_directory = 'dataSets/FallAllD_raw'
    fallalld_csv = pd.read_pickle(os.path.join('..', '..', fallalld_directory, 'FallAllD_raw.pkl'))
    fallalld = preprocess_fallalld(fallalld_csv)
    print(fallalld)


if __name__ == "__main__":
    main()