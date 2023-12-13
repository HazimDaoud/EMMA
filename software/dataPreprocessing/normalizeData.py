from sklearn.preprocessing import MinMaxScaler

def normalizeDfCols(df, cols):
    scaler = MinMaxScaler()
    df[cols] = scaler.fit_transform(df[cols])
    return df
