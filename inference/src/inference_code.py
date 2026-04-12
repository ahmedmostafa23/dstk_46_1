import pickle
import numpy as np
import pandas as pd

def load_model():
    with open("models/model.pkl", "rb") as f:
        model = pickle.load(f)
    return model

def model_inference(model, employee_data):
    employee_data_as_df = pd.DataFrame([employee_data])
    pred = model.predict(employee_data_as_df)[0]
    proba = model.predict_proba(employee_data_as_df)
    confidence = round(float(np.max(proba)), 3)
    return {
        "pred": pred,
        "confidence": confidence
    }

def batch_inference(model, list_of_employee_data):
    sample_batch_data_as_df = pd.DataFrame(list_of_employee_data)
    preds = model.predict(sample_batch_data_as_df)
    probas = model.predict_proba(sample_batch_data_as_df)
    confidences = np.max(probas, axis=1)
    return [
        {"pred": pred, "confidence": round(float(confidence), 3)}
        for pred, confidence in zip(preds, confidences)
    ]
