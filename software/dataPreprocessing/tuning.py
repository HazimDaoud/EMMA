import tensorflow
from keras_tuner import BayesianOptimization
import keras_tuner
from keras import models, layers, metrics
from labellingData import readSubsCsvs
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
import pandas as pd
from keras.utils import to_categorical
import numpy as np
from sklearn.utils.class_weight import compute_class_weight
from windowData import createSlidingWindows

class MyHyperModel(keras_tuner.HyperModel):
    def build(self, hp):
        model = models.Sequential()
        model.add(layers.Conv1D(hp.Int('filters_1', min_value=2, max_value=16, step=2),
                                kernel_size=hp.Int('kernel_size_1', min_value=2, max_value=8),
                                activation='relu', input_shape=(200, 3), padding='same'))
        model.add(layers.BatchNormalization())
        model.add(layers.MaxPooling1D(pool_size=hp.Int('pool_size_1', min_value=2, max_value=8),
                                        strides=hp.Int('strides_1', min_value=2, max_value=8)))

        model.add(layers.Conv1D(hp.Int('filters_2', min_value=2, max_value=16, step=2),
                                kernel_size=hp.Int('kernel_size_2', min_value=2, max_value=8),
                                activation='relu', padding='same'))
        model.add(layers.BatchNormalization())
        model.add(layers.MaxPooling1D(pool_size=hp.Int('pool_size_2', min_value=2, max_value=8),
                                        strides=hp.Int('strides_2', min_value=2, max_value=8)))

        model.add(layers.Flatten())
        model.add(layers.Dense(hp.Int('units', min_value=32, max_value=320, step=32), activation='relu'))
        model.add(layers.BatchNormalization())

        model.add(layers.Dropout(hp.Float('dropout_rate', min_value=0.1, max_value=0.5, step=0.1)))

        model.add(layers.Dense(2, activation='softmax'))

        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model

    def fit(self, hp, model, *args, **kwargs):
        return model.fit(
            *args,
            batch_size=hp.Choice("batch_size", [16, 100]),
            **kwargs,
        )

def main():
    absolutepath = ''
    df = readSubsCsvs(absolutepath)
    df['fall'] = df['fall'].map(lambda x : 0 if x in range(1,10) else 1)
    fallRaw = df["fall"]
    featuresRaw = df.drop(["fall", "id", "Name", "Age", "Height", "Weight", "Gender", "timestamp"], axis = 1)
    scaler = MinMaxScaler()
    numerical = ["accelerometer_x", "accelerometer_y", "accelerometer_z",]
    featuresTransformed = pd.DataFrame(data = featuresRaw)
    featuresTransformed[numerical] = scaler.fit_transform(featuresTransformed[numerical])
    y = fallRaw.values
    labelEncoder = LabelEncoder()
    yEncoded = labelEncoder.fit_transform(y)
    windows, labels = createSlidingWindows(featuresTransformed.values, yEncoded, 200)

    x_train, x_test, y_train, y_test = train_test_split(windows, labels, test_size = 0.2, random_state = 0)
    print('Training set has {} samples'.format(x_train.shape))
    print('Testing set has {} samples'.format(x_test.shape))


    numClasses = len(np.unique(y))
    y_trainCat = to_categorical(y_train, num_classes=numClasses)
    y_testCat = to_categorical(y_test, num_classes=numClasses)
    class_labels = np.unique(y_train)
    classWeights = compute_class_weight(class_weight ='balanced', classes = class_labels, y= y_train)
    classWeights
    classWeightsDict = dict(zip(class_labels, classWeights))


    tuner = BayesianOptimization(
        MyHyperModel(),
        objective=keras_tuner.Objective('val_f1', direction='max'),  
        max_trials=10,
  
    )
    tuner.search(x_train, y_trainCat, epochs=10, validation_data=(x_test, y_testCat), class_weight=classWeightsDict)
    bestParameters = tuner.oracle.get_best_trials(1)[0].hyperparameters.values
    print("Best Hyperparameters:", bestParameters)

if __name__ == "__main__":
    main() 