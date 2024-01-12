from collections import Counter
import numpy as np
def createSlidingWindows(data, labels, windowSize):

    windows = []
    correspondingLabels = []
    for i in range(len(data) - windowSize + 1):
        window = data[i : i + windowSize]
        labelCounts = Counter(labels[i : i + windowSize])
        majority = labelCounts.most_common(1)[0][0]
        windows.append(window)
        correspondingLabels.append(majority)
        
    windows = np.array(windows)
    correspondingLabels = np.array(correspondingLabels)
    return windows, correspondingLabels
