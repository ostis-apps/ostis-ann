import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import json
from evaluate import load
import requests
import uuid
import re
import time
start_time = time.time()

# Метрики
bleu = load("bleu", quiet=True)
rouge = load("rouge", quiet=True)
bertscore = load("bertscore", quiet=True)
meteor = load("meteor", quiet=True)
chrf = load("chrf", quiet=True)
ter = load("Vallp/ter", quiet=True)

def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # Удаляем пунктуацию
    text = re.sub(r"\s+", " ", text)     # Удаляем лишние пробелы
    return text.strip()


def get_api_response(question, session_id, model):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        "question": question,
        "model": model
    }
    if session_id:
        data["session_id"] = session_id

    try:
        response = requests.post("http://localhost:8000/chat", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[API ERROR] Status code: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        print(f"[EXCEPTION] {e}")
        return None

def evaluate_metrics(prediction: str, reference: str, question: str):
    start_incycle_time = time.time()

    # Нормализация
    pred_norm = normalize_text(prediction)
    ref_norm = normalize_text(reference)

    # Метрики
    bleu_result = bleu.compute(
        predictions=[pred_norm],
        references=[[ref_norm]]
    )
    bert_result = bertscore.compute(
        predictions=[prediction],
        references=[reference],
        lang="ru"
    )
    meteor_result = meteor.compute(
        predictions=[pred_norm],
        references=[ref_norm]
    )
    chrf_result = chrf.compute(
        predictions=[pred_norm],
        references=[ref_norm]
    )
    ter_result = ter.compute(
        predictions=[pred_norm],
        references=[ref_norm]
    )

    end_incycle_time = time.time()
    elapsed_incycle_time = end_incycle_time - start_incycle_time

    return {
        "BLEU": bleu_result["bleu"],
        "METEOR": meteor_result["meteor"],
        "BERTScore (F1)": bert_result["f1"][0],
        "ChrF": chrf_result["score"]/100,
        "TER": ter_result["score"]/100,
        "Execution Time (s)": elapsed_incycle_time
    }


# Загрузка бенчмарка
with open("benchmark/test.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

results = []
for i, item in enumerate(questions, 1):
    start_cycle_time = time.time()

    SESSION_ID = f"benchmark-{uuid.uuid4()}"
    question = item["question"]
    reference = item["reference"]

    prediction_data = get_api_response(question, session_id=SESSION_ID, model="gemma3")
    if prediction_data and 'answer' in prediction_data:
        prediction = prediction_data['answer']
    else:
        prediction = f"Error: No response (Session ID: {SESSION_ID})"

    print(f"[{i}] Вопрос: {question}")
    print(f"→ Ответ: {prediction[:100]}...")
    if prediction:
        classic_scores = evaluate_metrics(prediction, reference, question)
    else:
        classic_scores = {
            "BLEU": 0.0,
            "METEOR": 0.0,
            "BERTScore (F1)": 0.0,
            "ChrF": 0.0,
            "TER": 0.0
        }

    result = {
        "question": question,
        "prediction": prediction,
        "reference": reference,
        **classic_scores
    }

    end_cycle_time = time.time()
    elapsed_cycle_time = end_cycle_time - start_cycle_time
    print(f"\n⏱ Время выполнения вопроса: {elapsed_cycle_time:.2f} секунд")
    results.append(result)

# Сохранение
with open("benchmark/triad_extended_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n✅ Оценка завершена. Результаты сохранены в 'triad_extended_results.json'")

end_time = time.time()
elapsed_time = end_time - start_time
print(f"\n⏱ Время выполнения: {elapsed_time:.2f} секунд")