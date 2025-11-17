import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib


DF_PATH = "logs.json"
MODEL_OUT = "if_model.joblib"
SCALER_OUT = "scaler.joblib"


def load_features(path):
    df = pd.read_json(path)
    # choose numeric features
    df = df.fillna(0)
    df['bytes_out_log'] = np.log1p(df['bytes_out'])
    df['bytes_in_log'] = np.log1p(df['bytes_in'])
    features = ['bytes_out_log', 'bytes_in_log', 'duration', 'pkts']
    X = df[features]
    return X, df


if __name__ == '__main__':
    X, df = load_features(DF_PATH)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)


model = IsolationForest(n_estimators=200, contamination=0.25, random_state=42)
model.fit(Xs)


joblib.dump(model, MODEL_OUT)
joblib.dump(scaler, SCALER_OUT)
print("Saved model and scaler:", MODEL_OUT, SCALER_OUT)