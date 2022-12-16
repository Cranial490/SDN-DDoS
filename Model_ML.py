import pickle
import sklearn
import numpy

def check_DDoS(datapoint):
    filename = 'DDoS_Pred_model2.sav'
    loaded_model = pickle.load(open(filename, 'rb'))
    # loaded_scaler = pickle.load(open('scaler.pkl', 'rb'))
    # X_test = loaded_scaler.transform(numpy.array(datapoint).reshape(1,-1))
    X_test =numpy.array(datapoint).reshape(1,-1)
    result = loaded_model.predict(X_test.reshape(1,-1))
    return result
