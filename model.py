import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import datetime
data = pd.read_excel('пп_станции.xlsx')

data.set_index('Станция', inplace=True)

def predict_passenger_flow(station_name, target_date):
    station_data = data.loc[station_name][3:]
    steps = int((target_date-datetime.now()).days)+1
    model = SARIMAX(station_data.astype(float), order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    model_fit = model.fit(disp=False)
    prediction = list(model_fit.forecast(steps=steps))[-1]
    return prediction
  
predicted_flow = predict_passenger_flow("Электрозав-я БКЛ", datetime(2025,4,25))
print(predicted_flow)
