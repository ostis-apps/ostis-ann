import google.generativeai as genai
from .constant import base_content
from typing import Tuple

def generate_sc(text:str) -> Tuple[str, str]:
    genai.configure(api_key='AIzaSyDhNsclhf9A5Ypmce1059IWjU_Zc7JgdNw')
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(base_content.format(**{"question": text}))
    return response.text.splitlines()[0], response.text.splitlines()[1:]


if __name__ == '__main__':
    print(generate_sc("Сколько будет стоить мотоцикл с обьемом двигателя 500 миллилитров?")[1])