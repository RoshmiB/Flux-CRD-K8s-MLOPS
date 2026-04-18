from fastapi import FastAPI
import pickle
import pandas as pd

app = FastAPI()

# load model + feature names
model_data = pickle.load(open("model.pkl", "rb"))
model = model_data["model"]
features = model_data["features"]

@app.get("/")
def home():
    return {"message": "ML Model API Running"}

@app.post("/predict")
def predict(data: dict):

    # if set(data.keys()) != set(features):
    #     return {"error": f"Expected features: {features}"}
    
    # convert input to dataframe
    input_df = pd.DataFrame([data])
    # Create derived feature
    input_df["rooms_per_household"] = input_df["AveRooms"] / input_df["AveOccup"]

    print("Expected:", features)
    print("Input DF columns:", input_df.columns.tolist())

    # ensure ALL required columns exist
    missing = set(features) - set(input_df.columns)
    if missing:
        return {"error": f"Missing features: {missing}"}
            # input_df[col] = 0  # default fallback

    # reorder columns to match training
    input_df = input_df[features]
    prediction = model.predict(input_df)

    return {"prediction": float(prediction[0])}

# def predict(data: dict):
#     features = np.array(list(data.values())).reshape(1, -1)
#     prediction = model.predict(features)
