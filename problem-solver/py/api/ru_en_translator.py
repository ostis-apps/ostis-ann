import json
from deep_translator import GoogleTranslator

with open("../translation_dict.json", "r", encoding="utf-8") as f:
    translation_dicts = json.load(f)
    ru_en_dict = translation_dicts["ru_en_dict"]
    proper_names = translation_dicts["proper_names"]

def preprocess_ru(text: str):
    text = text.lower()
    for ru, en in ru_en_dict.items():
        text = text.replace(ru, en)
    return text

def translate_ru_to_en(text):
    try:
        processed = preprocess_ru(text)
        translation = GoogleTranslator(source='ru', target='en').translate(processed)
        for mistake, correct in proper_names.items():
            translation = translation.replace(mistake, correct)
        return translation.lower()
    except Exception as e:
        print(f"Translation error: {e}")
        return text