from tensorflow.keras import models
import csv
import numpy as np


def displayResult(result, interfaceConnection = False):
    """ To handle the final result

    Args:
        result (int): 1 means a fall 0 not a fall
        interfaceConnection (bool, optional): when set to true it does interface stuff. Defaults to False.
    """    
    if result == 1: 
        print("its a fall") 
    else:
        print ("No fall")

    if interfaceConnection:
        ## add interface stuff
        print("sent to Interface")
 
def makeDecision(predictAdl, predictFall):
    """just checks which one is larger  and then displays the result by printing it and if there is connection with the interface it will display it there.
        right now it prints the probabilities as well.
    Args:
        predictAdl (numpy.float32): model's output probability of an ADL.
        predictFall (numpy.float32): model's output probability of a fall.
    """    
    print("ADL prob: {}".format(predictAdl))
    print("Fall prob: {}".format(predictFall))

    result = 0
    if predictFall >= predictAdl:
        ## what to do in the case where they are equal? my guess would be that making it as a fall is better? since FP is safer than FN
        result = 1
        
    displayResult(result, False)
    
def handleLastWindow(window, myModel, windowSize=200):
    """This functions handles the last window when its size is less than the input shape of the model, and it it handles it by repeating the last sample until you reach the desired shape

    Args:
        window (list): the undersized window 
        myModel (keras seq. model): the .h5 model
        windowSize (int, optional): the input shape of the model. Defaults to 200.
    """    
    windowLength = len(window)
    if windowLength >= windowSize:
        return window
    
    repetitions = windowSize - windowLength
    lastSample = window[-1]
    repeatedWindow = np.concatenate([window, np.tile(lastSample, (repetitions, 1))])
    makePrediction(repeatedWindow, myModel)



def makePrediction(myWindow, myModel):
    """here the model predicts a window and sends both probabilities to the makeDecision function.

    Args:
        myWindow (array): thw window that the model will predict on
        myModel (keras sequential model): the .h5 model 
    """    
    win2 = np.array(myWindow)
    win2Reshaped = win2.reshape((1,200,3))
    prediction = myModel.predict(win2Reshaped)
    predictAdl = prediction[0][0]
    predictFall = prediction[0][1]
    makeDecision(predictAdl, predictFall)


def readCSV(filepath):
    """takes a CSV file and yields one row at a time to process further.

    Args:
        filepath (str): path to your csv file

    Yields:
        list: yields a row of the csv file 
    """    
    with open(filepath, 'r') as csvfile:
        csvReader = csv.reader(csvfile)
        for row in csvReader:
            yield row

def processFromCSV(csvfilepath, myModel):
    """This is the main loop when you are reading from a csv.

    Args:
        csvfilepath (str): csv file path
        myModel (keras seq. model): the .h5 model
    """    
    myWindow = []
    counter = 0
    windowCounter = 0
    for row in readCSV(csvfilepath):
        ax = float(row[0])
        ay = float(row[1])
        az = float(row[2])
        axNorm = ax + 2 / 4
        ayNorm = ay + 2 / 4
        azNorm = az + 2 / 4
        myWindow.append([axNorm, ayNorm, azNorm])  

        if counter == 199:
            makePrediction(myWindow, myModel)
            myWindow = []
            windowCounter += 1
            counter = -1
            
        counter += 1

    if len(myWindow) != 0:
        handleLastWindow(myWindow, myModel, 200)
        windowCounter += 1
    print("predicted a total of {} windows".format(windowCounter))


# def readDirectlyFromSensor(myModel):
    ### can we send data from the sensor directly here and process it like we do in the  processFromCSV() function?





def main():
    from datetime import datetime

    timeBefore = datetime.now()

    # csvpath = r'D:\TUDarmstadt\DSII\workspace\fff\fallDetection\dataSets\Data_Collection_Datanauts\Data(CSV)\02.02.2024\falling_hazim.csv'
    csvpath = r'D:\TUDarmstadt\DSII\workspace\fff\fallDetection\dataSets\Data_Collection_Datanauts\Data(CSV)\02.02.2024\walking_hazim.csv'
    modelpath = "software/savedModels/newModel.h5"

    myModel = models.load_model(modelpath)
    processFromCSV(csvpath, myModel)


    timeAfter = datetime.now()
    totalTime = timeAfter - timeBefore
    print("total time in seconds:", totalTime.total_seconds())
if __name__ == "__main__":
    main()