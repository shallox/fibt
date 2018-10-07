import pandas as pd
from sklearn.preprocessing import Imputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from itertools import product


def data_modle_smasher(data):
    for key in data:
        if 'datetime64' in str(data[key].dtype):
            data[key] = pd.to_numeric(data[key])
        try:
            float(data[key].iloc[0])
            data[key] = data[key].astype('float64')
        except ValueError:
            continue
        except TypeError:
            continue
    return data


def dat_molder(data):
    int_col_b = []
    for keyb in data:
        if data[keyb].dtypes == 'float64':
            int_col_b.append(keyb)
        elif data[keyb].dtypes == 'int64':
            int_col_b.append(keyb)
    int_oly_data_set = data[int_col_b]
    return int_oly_data_set


final = []


def rf_kgo(table_name, n_estimators, max_features, cores, data, choo):
    global final
    parms = [n_estimators,  # n_estimators
             max_features,  # max_features
             cores]
    best_market_score = float("-inf")
    for n, f, p in product(*parms):
        i = Imputer(strategy='median')
        i.fit(data)
        if len(choo) == 1:
            train_dat = data[choo[0]]
        else:
            train_dat = data[choo]
        imputed_test = i.transform(data)
        #train_test_split()
        AlgorithmTest = RandomForestRegressor(n_estimators=int(n), oob_score=True, n_jobs=int(p), max_features=float(f))
        AlgorithmTest.fit(imputed_test, train_dat)
        accuracy = AlgorithmTest.oob_score_
        predictions = AlgorithmTest.oob_prediction_
        pred_counter = 0
        pred_dict = {}
        for a in predictions:
            pred_dict.update({'prediction' + str(pred_counter): a})
            pred_counter += 1
        if accuracy > best_market_score:
            final.append({'table_name': table_name, 'accuracy': accuracy, 'n_estimators': n, 'max_features': f,
                         'cores': p, 'command': AlgorithmTest, 'best': 1, **pred_dict})
            best_market_score = accuracy
        else:
            final.append({'table_name': table_name, 'accuracy': accuracy, 'n_estimators': n, 'max_features': f,
                         'cores': p, 'command': AlgorithmTest, 'best': 0, **pred_dict})
    return final
