# Оценка работы API RAG-приложения
## Главные библиотеки и подходы в оценке
- ### **sklearn (cosine_similarity)**
- ### **requests**

## Методы оценки

- ### **cosine_similarity**
Функция, находящая косинусное расстояние между полученным результатом и итоговый результатом. 
```python
def calculate_cos_query(response,reference):
    resp = embedding_function.embed_query(response)
    refr = embedding_function.embed_query(reference)
    resp = np.array(resp).reshape(1, -1) 
    refr = np.array(refr).reshape(1, -1)
    result = cosine_similarity(resp,refr)
    return result[0][0]
```
- ### **requests**
***Библиотека, которую будем использовать для обращения к нашему приложению по url-адрессу.***

## Алгоритм оценки rag-приложения

### 1.Инициализируем свой набор данных
### 2.Загружаем файл через requests
### 3.Обрабатываем вопросы из набора данных
### 4.Оценка ответов
### 5.Построение таблицы для анализа полученных результатов

## 1.Инициализация своего набора данных
``` python
dataset = [
    {
        "question": "Как изменения в информационной революции повлияли на восприятие новостей?",
        "answer": "Информационная революция привела к тому, что всё больше людей начинают зависеть от онлайн-новостей для получения информации, использующих такие термины как «цифровые аборигены»" 
        ...
    }
    ...
]
```
## 2.Загрузка файла 
``` python

 with open(filename, "rb") as f:
        files = {'file': (f.name,f,'pdf')}
        response = requests.post("http://localhost:8000/upload-doc", files=files)
        assert response.status_code == 200

```
## 3.Обработка вопросов
```python
for example in dataset:
    data = {
        "question":example['question'],
        "model":"llama3.2"
    }
    
    response = requests.post("http://localhost:8000/chat",headers=headers, json=data)
    assert response.status_code == 200
    res = response.json()
    ...

```
## 4.Оценка ответов
```python
 cosine_answer = calculate_cos_query(res['answer'],example['answer'])
    
    cosine_distance.append({
        "cosine_answer":cosine_answer,
    })   
```
## 5.Таблица результатов

![](imgs/table_of_API.png)



------------------------

# ***Оценка работы retriever от всей системы***
## Главные библиотеки и подходы в оценке
- ### **ragas (NonLLMContextPrecisionWithReference)**
- ### **ragas (NonLLMContextRecall)**
- ### **sklearn (cosine_similarity)**

## Методы оценки

- ### **cosine_similarity**
Функция, находящая косинусное расстояние между полученным результатом и итоговый результатом. 
```python
def calculate_cos_query(response,reference):
    resp = embedding_function.embed_query(response)
    refr = embedding_function.embed_query(reference)
    resp = np.array(resp).reshape(1, -1) 
    refr = np.array(refr).reshape(1, -1)
    result = cosine_similarity(resp,refr)
    return result[0][0]
```
- ### NonLLMContextPrecisionWithReference
    [Ссылка на официальную документацию по этому классу](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_precision/#non-llm-based-context-precision)
- ### NonLLMContextRecall
    [Ссылка на официальную документацию по этому классу](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_recall/#non-llm-based-context-recall)
## Алгоритм оценки

### 1.Загрузка набора данных
### 2.Добавление контекстов из набора данных в временное хранилище
### 3.Обработка вопросов из набора данных с помощью rag-приложения и создание нового набора на основе ответов.  
### 4.Оценка получившегося набор данных с помощью метрик
### 5.Построение таблицы для анализа полученных результатов

#

### В рабочем пространстве должна быть создана папка benchmark

## 1.Этап загрузки данных
``` python
dataset = load_dataset(
    "explodinggradients/amnesty_qa",
    "english_v3",
    trust_remote_code=True
)

eval_dataset = dataset["eval"].select(range(10))
```

## 2.Этап добавления контекстов
``` python
documents = [Document(page_content="".join(example['retrieved_contexts'])) for example in eval_dataset]

split_documents = text_splitter.split_documents(documents)

temp_vectorstore = Chroma(persist_directory=temp_dir.name, embedding_function=embedding_function)

temp_vectorstore.add_documents(split_documents)
```

## 3.Этап создания нового набора данных
``` python
system_answers = []
cos_distance = []
for example in eval_dataset:  
    
    question = example["user_input"]  
    reference = example["reference"] 
    reference_contexts = example['retrieved_contexts']
    
    response = process_question_with_rag(question)
    
    retrieved_contexts = [i.page_content for i in response['context']]
    
    cossim = calculate_cos(response['answer'],reference)
    cos_distance.append(cossim)
    
    system_answers.append({"user_input": question,
                           "reference":reference,
                           "response": response['answer'],
                           "retrieved_contexts":retrieved_contexts,
                           "reference_contexts": reference_contexts})
```
## 4.Этап оценки нового набора данных
``` python
answers_df = pd.DataFrame(system_answers)
answers_df.to_csv("./benchmark/system_answers.csv", index=False)
eval_dataset_for_metrics = EvaluationDataset.from_pandas(answers_df)
metrics = [
    NonLLMContextPrecisionWithReference(),
    NonLLMContextRecall()
]

results = evaluate(dataset=eval_dataset_for_metrics, metrics=metrics)

results_df = results.to_pandas()
results_df['cosine_similarity'] = cos_distance
```
## 5.Этап построения таблицы
``` python
sns.heatmap(results_df.iloc[:,5:].T, annot=True,linewidths= 2,square = True,
            cmap="Blues",
            )
plt.xticks(rotation=45)

plt.show
```
### В нашем случае таблица выглядит следующим образом:
![Таблица](imgs/table_of_results.png)
