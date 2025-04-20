import tempfile

from ragas import EvaluationDataset, evaluate
from ragas.metrics import NonLLMContextPrecisionWithReference, NonLLMContextRecall

from langchain.schema import Document
from langchain_utils import get_rag_chain
from langchain_chroma import Chroma

from datasets import load_dataset
from chroma_utils import embedding_function,text_splitter
from sklearn.metrics.pairwise import cosine_similarity

import seaborn as sns
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

#функция для подсчёта косинусного расстояния
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
    return precision,recall,f1

temp_dir = tempfile.TemporaryDirectory()

dataset = load_dataset(
    "explodinggradients/amnesty_qa",
    "english_v3",
    trust_remote_code=True
)

eval_dataset = dataset["eval"].select(range(10))

#Cоздание временной Chroma

documents = [Document(page_content="".join(example['retrieved_contexts'])) for example in eval_dataset]

split_documents = text_splitter.split_documents(documents)

temp_vectorstore = Chroma(persist_directory=temp_dir.name, embedding_function=embedding_function)

temp_vectorstore.add_documents(split_documents)

retriever = temp_vectorstore.as_retriever(search_kwargs = {"k":2})

rag_chain = get_rag_chain(model="llama3.2",retriever=retriever) 

#Создаём собственный датасет, который будет оцениваться с помощью метрик

def process_question_with_rag(question: str, chat_history: list = []):
    response = rag_chain.invoke({"input": question, "chat_history": chat_history})
    return response

system_answers = []
results_of_our_metrics = []
for example in eval_dataset:  
    
    question = example["user_input"]  
    reference = example["reference"] 
    reference_contexts = example['retrieved_contexts']
    
    response = process_question_with_rag(question)
    
    retrieved_contexts = [i.page_content for i in response['context']]

    precision,recall,f1_score = calculate_f1_score("".join(retrieved_contexts),"".join(reference_contexts))
    cos_context = calculate_cos_query("".join(retrieved_contexts),"".join(reference_contexts))
    results_of_our_metrics.append({"cosine_context":cos_context,
                                   "precision":precision,
                                   "recall":recall,
                                   "f1_score":f1_score})
    
    system_answers.append({"user_input": question,
                           "reference":reference,
                           "response": response['answer'],
                           "retrieved_contexts":retrieved_contexts,
                           "reference_contexts": reference_contexts})

    
answers_df = pd.DataFrame(system_answers)
answers_df.to_csv("./benchmark/system_answers.csv", index=False)
eval_dataset_for_metrics = EvaluationDataset.from_pandas(answers_df)
metrics = [
    NonLLMContextPrecisionWithReference(),
    NonLLMContextRecall()
]

results_of_ragas_metrics = evaluate(dataset=eval_dataset_for_metrics, metrics=metrics)

results_of_our_metrics_df = pd.DataFrame(results_of_our_metrics)

#Конвертируем в DataFrame

results_of_ragas_metrics_df = results_of_ragas_metrics.to_pandas()

results_df = pd.concat([results_of_ragas_metrics_df,results_of_our_metrics_df],axis=1)
#Сохрнаяем результаты в файл
results_df.to_csv("./benchmark/rag_system_metrics.csv", index=False)


sns.heatmap(results_df.iloc[:,5:].T, annot=True,square = True,
            cmap="Blues",
            )
plt.xticks(rotation=45)

plt.show()