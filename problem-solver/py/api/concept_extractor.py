import spacy
import re
from ru_en_translator import translate_ru_to_en

nlp_en = spacy.load("en_core_web_sm")

def extract_en_terms(text):
    doc = nlp_en(text)
    terms = []
    words_in_chunks = set()
    articles = {"a", "an", "the"}
    question_words = {"what", "which", "who", "whom", "whose", "where", "when", 
                     "why", "how", "whether", "if", "do", "does", "did", "is", 
                     "are", "was", "were", "will", "would", "can", "could", 
                     "shall", "should", "may", "might", "must"}
    nn_patterns = [
        ("artificial neural network", "ann"),
        ("neural network", "ann")
    ]
    for chunk in doc.noun_chunks:
        filtered_chunk = [token for token in chunk 
                          if token.text.lower() not in articles 
                          and token.text.lower() not in question_words]
        if not filtered_chunk:
            continue

        chunk_text = " ".join(token.lemma_ for token in filtered_chunk).lower()
        
        is_standalone_nn = chunk_text in ["artificial neural network", "neural network"]
        
        if len(chunk_text.split()) > 1:
            if not is_standalone_nn:
                for pattern, replacement in nn_patterns:
                    chunk_text = chunk_text.replace(pattern, replacement)
            
            terms.append(chunk_text)
            words_in_chunks.update([token.lemma_.lower() for token in filtered_chunk])
        elif is_standalone_nn:
            terms.append("ann")
            words_in_chunks.update(["ann"])
    
    for token in doc:
        token_text = token.text.lower()
        token_lemma = token.lemma_.lower()
        
        if token_text in articles or token_text in question_words or token.is_stop:
            continue
            
        is_noun_adj = token.pos_ in ["NOUN", "PROPN", "ADJ"]  
        is_ing_verb = (token.pos_ == "VERB") and token_text.endswith("ing")
        
        if (is_noun_adj or is_ing_verb) and len(token_text) > 2:
            if token_lemma not in words_in_chunks:
                terms.append(token_text if is_ing_verb else token_lemma)
    
    return list(set(terms))
    

def make_context_for_db(question):
    en_question = translate_ru_to_en(question)
    print(f"Перевод вопроса: {en_question}") 
    en_terms = extract_en_terms(en_question)
    print(f"Ключевые термины (en): {en_terms}")
    return f"{question} {' '.join(en_terms)}"