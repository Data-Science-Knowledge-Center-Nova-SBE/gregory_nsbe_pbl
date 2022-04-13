from joblib import load
from gregory.utils.model_utils import DenseTransformer
import json
from sys import argv
from datetime import date
import requests
import json
import pandas as pd
import html
from gregory.utils.text_utils import cleanHTML
from gregory.utils.text_utils import cleanText
from joblib import load
from pandas.io.json import json_normalize #package for flattening json in pandas df
from gregory.models import Articles

# These are the different model names
GNB = "gnb"
LSVC = "lsvc"
MNB = "mnb"
LR = "lr"

models = [GNB, LSVC, MNB, LR]

# This is the dict that will store the pipelines
pipelines = {}

for model in models:
    pipelines[model] = load('ml_models/model_' + model + '.joblib')

# Now let's fetch a new set of data
today = date.today()
year_month = today.strftime("%Y/%m")

dataset_file_json = 'data/' + today.strftime("%Y-%B") + '.json'
dataset_file_csv = 'data/' + today.strftime("%Y-%B") + '.csv'

data = pd.DataFrame(list(Articles.objects.filter(ml_prediction_gnb=None).values("title", "summary", "relevant", "article_id")[:20]))
dataset = pd.json_normalize(data=data['results'])
# KeyError: 'results'


# Clean the title column with the cleanText utility
dataset["title"] = dataset["title"].apply(cleanText)

# Some columns in the summary column seem to be encoded in HTML, let's decode it
dataset["summary"] = dataset["summary"].apply(html.unescape)

# Now let's remove all those HTML tags
dataset["summary"] = dataset["summary"].apply(cleanHTML)

# Now let's clean the resulting text in the summary column
dataset["summary"] = dataset["summary"].apply(cleanText)

# Let's join the two text columns into a single 'terms' column
dataset["terms"] = dataset["title"].astype(str) + " " + dataset["summary"].astype(str)

# We no longer need some text columns, let's remove them
dataset = dataset[["terms", "relevant", "article_id"]]

# There are several records in the "relevant" column as NaN. Let's convert them to zeros
dataset["relevant"] = dataset["relevant"].fillna(value=0)

# A value is trying to be set on a copy of a slice from a DataFrame.
# Try using .loc[row_indexer,col_indexer] = value instead

# See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy

# change true/false to 1/0
dataset["relevant"] = dataset["relevant"].astype(int)



# Save the dataset
dataset.to_csv(dataset_file_csv, index=False)

# Load the source data into a Pandas dataframe
dataset = pd.read_csv(dataset_file_csv)

# Replace any NaN with zero
dataset['relevant'] = dataset['relevant'].fillna(value=0)


# Models to use from the list above
models = [GNB,LR]

# This is the dict that will store the pipelines
pipelines = {}

for model in models:
    pipelines[model] = load('ml_models/model_' + model + '.joblib')


def predictor(dataset):
    data = {"O": []}
    result = {}
    result["models"] = {}
    for model in models:
        data[model] = []    
        result["models"][model] = []
    for index, row in dataset.iterrows():
        input = row['terms']
        output = row['relevant']
        data["O"].append(output)
        test = "TEST " + str(index + 1) +             " (provided: " + str(int(output)) + ")"
        for model in models:
            prediction = pipelines[model].predict([input])
            data[model].append(prediction)
            test += " - " + model + ": " + str(int(prediction))
            result["models"][model].append({
                "article_id": row['article_id'],
                "prediction": str(int(prediction))
            })
    return result,data

data = predictor(dataset)
# /usr/local/lib/python3.10/site-packages/sklearn/utils/validation.py:593: FutureWarning: np.matrix usage is deprecated in 1.0 and will raise a TypeError in 1.2. 
# Please convert to a numpy array with np.asarray. For more information see: https://numpy.org/doc/stable/reference/generated/numpy.matrix.html

# The predictor returns two elements, result and data. 
# "result" is index 0 and is a JSON object
print(json.dumps(data[0]))

# TO DO 
# - [ ] save the result in the database
