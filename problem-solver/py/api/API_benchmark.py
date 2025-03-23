from sklearn.metrics.pairwise import cosine_similarity
from chroma_utils import embedding_function
import seaborn as sns
import matplotlib.pyplot as plt

import requests
import pandas as pd
import numpy as np

def calculate_cos_query(response,reference):
    resp = embedding_function.embed_query(response)
    refr = embedding_function.embed_query(reference)
    resp = np.array(resp).reshape(1, -1) 
    refr = np.array(refr).reshape(1, -1)
    result = cosine_similarity(resp,refr)
    return result[0][0]

file_names = ["news.pdf"]

dataset = [
    {
        "question": "Как изменения в информационной революции повлияли на восприятие новостей?",
        "answer": "Информационная революция привела к тому, что всё больше людей начинают зависеть от онлайн-новостей для получения информации, использующих такие термины как «цифровые аборигены», «интернет-пользователи» и так далее.",
        "context": "Thanks to the information revolution, more and more people rely on online news to stay informed. Expressions such as “digital natives,” “netizens,” “webworms,” “Internet geeks” are used to describe people who depend on Internet access for updating their knowledge and information."
    },
    {
        "question": "Какие форматы новостей существуют в интернете?",
        "answer": "В интернете новости могут быть представлены через видео, флеши, звуки, изображения, галереи картинок, а также веб-страницы с гиперссылками.",
        "context": "Online news refers to a variety of formats to disseminate information using Internet portals and digital presentation. These formats include news delivered through online videos, flashes, sounds, images, and picture galleries, as well as Web pages with hyperlinks."
    },
    {
        "question": "Как отличаются традиционные и онлайн-новости по процессу производства?",
        "answer": "В традиционных новостях роли разделены между владельцами, издателями и редакторами. В онлайн-новостях авторы могут выполнять все эти роли, создавая новости и публикуя их самостоятельно.",
        "context": "Online news does not have the same clear-cut division of labor in the production and conveyance of news as traditional news. The author of online news articles may have to perform many tasks, which range from news-searching, editing, and designing to promotion."
    },
    {
        "question": "Что характеризует онлайн-новости в плане скорости публикации?",
        "answer": "Онлайн-новости характеризуются непрерывным циклом публикации, в отличие от традиционных новостей с фиксированными сроками выхода.",
        "context": "In contrast to the traditional print news cycle, which has predictable and recurring time windows for publishing, online news is characterized by a continuous publishing cycle."
    },
    {
        "question": "Как мультимедийные возможности изменили представление новостей в интернете?",
        "answer": "Онлайн-новости предлагают разнообразные формы представления, включая текст, видео, звук, анимацию и гиперссылки, в отличие от ограничений традиционной печатной прессы.",
        "context": "Compared with the restricted presentation options of traditional news, online news has a rich variety of presentation choices. Hyperlinks are possible, users can make comments, news stories may be moved up and down the front page, and multimedia components such as Web TV may be added."
    },
    {
        "question": "Что такое 'YouTubization' в контексте онлайн-новостей?",
        "answer": "'YouTubization' означает использование видео для передачи новостей, что стало важной частью современного онлайн-репортажей.",
        "context": "Second, there has been an increase in users’ ability to participate interactively in sites. Third comes what Lee calls “YouTubization”: YouTubization is the reliance on video excerpts to tell a story."
    },
    {
        "question": "Как онлайн-новости изменили участие аудитории?",
        "answer": "В онлайн-новостях аудитория может активно участвовать, комментируя и делая репосты, что отличается от традиционного способа взаимодействия с новостями, когда нужно было отправлять письма или звонить.",
        "context": "Online news media remove most of the regulation. Lee (2012) describes six significant changes. The first is the inclusion of user-generated content, which allows users to upload the information they see as newsworthy."
    },
    {
        "question": "Как работает индивидуализация новостей в интернете?",
        "answer": "Онлайн-новости позволяют пользователям выбирать интересующие их статьи и получать только те, которые соответствуют их предпочтениям.",
        "context": "Online news provides a solution to this troublesome turning and tossing and reading for a particular piece of information. With online news readers may select those sections of the newspaper they are interested in, and only receive those parts."
    },
    {
        "question": "Каковы особенности заголовков онлайн-новостей?",
        "answer": "Заголовки онлайн-новостей короткие, активные и в настоящем времени, с целью привлечь внимание и быть легко понятными.",
        "context": "Headlines typically consist of no more than 10 relatively nontechnical words that seek to represent the whole idea of a story. Headlines are designed for easy understanding and to facilitate enjoyment."
    }
]


for filename in file_names:
    with open(filename, "rb") as f:
        files = {'file': (f.name,f,'pdf')}
        response = requests.post("http://localhost:8000/upload-doc", files=files)
        assert response.status_code == 200

system_answers = []
cosine_distance = []

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
    
    cosine_answer = calculate_cos_query(res['answer'],example['answer'])
    
    cosine_distance.append({
        "cosine_answer":cosine_answer,
    })   
    
    system_answers.append({
        "user_input":example['question'],
        "system_answer":res['answer'],
        "reference_answer":example['answer'],
    })
    
answers_df = pd.DataFrame(system_answers)
cosine_df = pd.DataFrame(cosine_distance)
results_df = pd.concat([answers_df,cosine_df],axis=1)
results_df.to_csv("./benchmark/API_results.csv",index=False)