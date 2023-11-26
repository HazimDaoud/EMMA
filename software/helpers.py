import pandas as pd
import os


def saveDataframe_as_csvfile(dataframe, directoryPath, filename):

    try:
        # Create the directory if it doesn't exist
        os.makedirs(directoryPath, exist_ok=True)

        # Construct the full file path
        file_path = os.path.join(directoryPath, filename)

        # Save the DataFrame to CSV
        dataframe.to_csv(file_path, index=False)
        
    except Exception as e:
        print(f"Error: {e}")

def shuffleDataframe(dataframe):

    shuffledDataframe = dataframe.sample(frac=1).reset_index(drop=True)
    return shuffledDataframe