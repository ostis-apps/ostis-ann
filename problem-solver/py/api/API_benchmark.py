#metrics
from sklearn.metrics.pairwise import cosine_similarity
from nltk.translate.bleu_score import sentence_bleu,SmoothingFunction
from nltk.translate.meteor_score import meteor_score

#utils
from chroma_utils import embedding_function
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import pandas as pd
import numpy as np
import re

#metric functions
def preprocess_text(text):
    text = re.sub(r'[^\w\s]',"",text)
    text = text.lower()
    return text

def calculate_bleu_score(response,reference):
     reference_tokens = reference.split()
     responce_tokens = response.split()
     smoothin_func = SmoothingFunction().method1
     score = sentence_bleu([reference_tokens],responce_tokens,weights=(0.5,0.5,0,0),smoothing_function=smoothin_func)
     return score

def meteor(response,reference):
    return meteor_score([reference.split()],response.split())

def calculate_jaccard_similarity(response, reference):
    response_set = set(response.split())
    reference_set = set(reference.split())
    intersection = len(response_set.intersection(reference_set))
    union = len(response_set.union(reference_set))
    return intersection / union if union != 0 else 0

def calculate_cos_query(response,reference):
    resp = embedding_function.embed_query(response)
    refr = embedding_function.embed_query(reference)
    resp = np.array(resp).reshape(1, -1) 
    refr = np.array(refr).reshape(1, -1)
    result = cosine_similarity(resp,refr)
    return result[0][0]

def calculate_f1_score(response,reference):
    ref_tokens = set(reference)
    res_tokens = set(response)
    common = ref_tokens.intersection(res_tokens)
      
    precision = len(common) / len(res_tokens)
    recall = len(common) / len(ref_tokens)
    f1 = 2 * (precision * recall) / (precision + recall)
    return f1

#dataset
file_names = ["kinematics.pdf"]

dataset = [
    {
        "question": "Что изучает механика?",
        "answer": "Механика изучает механическое движение тел, то есть изменение их положения в пространстве относительно других тел с течением времени.",
    },
    {
        "question": "Какие разделы включает механика?",
        "answer": "Механика подразделяется на кинематику, динамику и статику.",
    },
    {
        "question": "Что изучает кинематика?",
        "answer": "Кинематика изучает способы описания движения и связь между величинами, характеризующими эти движения, без рассмотрения причин, вызывающих движение.",
    },
    {
        "question": "Что такое механическое движение?",
        "answer": "Механическое движение — это изменение положения тела относительно других тел с течением времени.",  
    },
    {
        "question": "Какие виды механического движения существуют?",
        "answer": "Механическое движение бывает поступательным и вращательным. При поступательном движении любая прямая, проведённая в теле, остаётся параллельной себе. При вращательном движении все точки тела движутся по окружностям, центры которых лежат на оси вращения.",  
    },
    {
        "question": "Что такое система отсчёта?",
        "answer": "Система отсчёта включает систему координат, тело отсчёта и прибор для измерения времени. Она необходима для описания движения.",
    },
    {
        "question": "Какие величины используются для описания движения?",
        "answer": "Для описания движения используются векторные (например, скорость, ускорение) и скалярные (например, путь, время) величины.",
    },
    {
        "question": "Как умножается вектор на скаляр?",
        "answer": "При умножении вектора на скаляр его длина изменяется в соответствующее число раз, а направление сохраняется, если скаляр положительный, или меняется на противоположное, если скаляр отрицательный.",
    }
]

#loading file
for filename in file_names:
    with open(filename, "rb") as f:
        files = {'file': (f.name,f,'pdf')}
        response = requests.post("http://localhost:8000/upload-doc", files=files)
        assert response.status_code == 200

#creating a new dataset
system_answers = []
metrics = []

headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

for example in dataset:
    data = {
        "question":example['question'],
        "model":"llama3.2"
    }
    
    response = requests.post("http://localhost:8000/chat",headers=headers, json=data)
    assert response.status_code == 200
    res = response.json()

    #The main problem is that our model generates much more text than the reference response
    #So we have to 'crop' it to delete some text, that may create a trouble with accuary of our answer 

    preprocessed_reference = preprocess_text(example['answer'])
    answer_list = res['answer'].split()
    length_of_reference = len(preprocessed_reference.split())
    amount_of_extra_words = 4
    #Our response, the size of the expected one
    answer_as_example = " ".join(answer_list[:length_of_reference+amount_of_extra_words])
    answer_as_example = preprocess_text(answer_as_example)
    
    cosine_answer = calculate_cos_query(answer_as_example,preprocessed_reference)
    bleu_score = calculate_bleu_score(answer_as_example,preprocessed_reference)
    f1 = calculate_f1_score(answer_as_example,preprocessed_reference)
    jaccard = calculate_jaccard_similarity(answer_as_example, preprocessed_reference)
    meteor_val = meteor(answer_as_example,preprocessed_reference)
    
    metrics.append(
        {
            "cosine_answer": cosine_answer,
            "bleu_score": bleu_score,
            "f1": f1,
            "jaccard_similarity": jaccard,
            "meteor":meteor_val
        }
    )
    
    system_answers.append({
        "user_input":example['question'],
        "system_answer":answer_as_example,
        "reference_answer":example['answer'],
    })

    
#dataframes
answers_df = pd.DataFrame(system_answers)
metrics_df = pd.DataFrame(metrics)
results_df = pd.concat([answers_df,metrics_df],axis=1)
results_df.to_csv("./benchmark/API_results.csv",index=False)

sns.heatmap(results_df.iloc[:,3:].T, annot=True,square = True,
            cmap="Blues",
            )
plt.xticks(rotation=45)

plt.show()  