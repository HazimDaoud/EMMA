import pandas as pd
import os
import helpers

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

def main():
    directory = 'dataSets/dummy_data_raw'
    df = labelMultiple_Csvfiles(directory)
    helpers.saveDataframe_as_csvfile(df,'dataSets/dummy_data_labelled', 'dummy_data_all' )
    dfShuffled = helpers.shuffleDataframe(df)
    helpers.saveDataframe_as_csvfile(df,'dataSets/dummy_data_labelled', 'dummy_data_all_shuffled' )


if __name__ == "__main__":
    main()