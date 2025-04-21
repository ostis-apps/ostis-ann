import os
from ru_en_translator import translate_ru_to_en
from concept_extractor import extract_en_terms
def normalize_file_name(target_filename: str):
    no_random_words = target_filename.replace('IGOR10_', '').replace('IGOR19_', '').replace('IGOR7_', '').replace('IGOR12_', '')
    no_scs_classes = no_random_words.replace('nrel_', '').replace('rrel_', '').replace('concept_', '').lower()
    return no_scs_classes

def find_scs_file(kb_folder, target_term):
    target_term = target_term.replace(' ', '_')
    kb_folder = os.path.expanduser(kb_folder)  
    for root, dirs, files in os.walk(kb_folder):
        for file in files:
            if file.lower().endswith('.scs'):
                normalized_file = normalize_file_name(file)[:-4]
                if normalized_file == target_term.lower():
                    return os.path.join(root, file)
    return None

def get_scs_content(target_term, kb_path="~/ostis-ann/kb"):
    file_path = find_scs_file(kb_path, target_term)
    if not file_path:
        print(f"Файл '{target_term}' не найден в '{kb_path}'")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        return None

def extract_definition_block(scs_content: str):
    lines = scs_content.split('\n')
    definition_block = []
    in_definition = False
    brace_level = 0

    for line in lines:
        stripped = line.strip()
        
        if not in_definition and stripped.startswith('definition -> ...') :
            in_definition = True
            definition_block.append(line)
            continue
            
        if in_definition:
            definition_block.append(line)

            if '(*' in line:
                brace_level += (line.count('(*')+line.count('('))
            if '*)' in line:
                brace_level -= (line.count('*)')+line.count(')'))
                
                if brace_level <= 0:
                    break
    return '\n'.join(definition_block) if definition_block else None

def extract_definition_block_extra_case(scs_content: str):
    lines = scs_content.split('\n')
    definition_block = []
    in_definition = False
    brace_level = -1
    for line in lines:
        stripped = line.strip()
        if not in_definition and stripped.startswith('<- definition;;'):
            in_definition = True
            definition_block.append(line)
            continue
        if in_definition:
            definition_block.append(line)

            if '(*' in line:
                brace_level += (line.count('(*')+line.count('('))+line.count('{')
            if '*)' in line:
                brace_level -= (line.count('*)')+line.count(')'))+line.count('}')
                
                if brace_level == 0:
                    break
    return '\n'.join(definition_block) if definition_block else None

def extract_definition_and_constants(block: str):
    definition_text = None
    used_constants = []

    lines = block.split('\n')

    in_translation = False
    in_constants = False
    brace_level = 0
    
    for line in lines:
        stripped = line.strip()

        if not in_translation and 'nrel_sc_text_translation' in stripped:
            in_translation = True
            continue

        if not in_constants and 'nrel_using_constants' in stripped:
            in_constants = True
            continue
            
        if in_translation and not in_constants:
            if '->' in line and '[' in line:
                arrow_pos = line.find('->')
                open_bracket_pos = line.find('[', arrow_pos)
                
                if open_bracket_pos != -1:
                    close_bracket_pos = line.find(']', open_bracket_pos)
                    
                    if close_bracket_pos != -1:
                        definition_text = line[open_bracket_pos+1:close_bracket_pos].strip()
                        in_translation = False

        if in_constants:
            if '(*' in line:
                brace_level += line.count('(*')
            if '*)' in line:
                brace_level -= line.count('*)')

            if '->' in line and brace_level == 1:
                const = line.split('->')[1].split(';;')[0].strip()
                if const:
                    used_constants.append(const)

            if brace_level <= 0:
                in_constants = False
    
    return {
        'definition': definition_text,
        'constants': used_constants
    }

def extract_definition_and_constants_extra_case(block: str):
    definition_text = None
    used_constants = []

    lines = block.split('\n')

    in_translation = False
    in_constants = False
    brace_level = 0
    for line in lines:
        stripped = line.strip()

        if not in_translation and 'nrel_sc_text_translation' in stripped:
            in_translation = True
            continue

        if not in_constants and 'nrel_using_constants' in stripped:
            in_constants = True
            continue

        if in_translation and not in_constants:
            if '[' in line:
                open_bracket_pos = line.find('[')
                
                if open_bracket_pos != -1:
                    close_bracket_pos = line.find(']', open_bracket_pos)
                    
                    if close_bracket_pos != -1:
                        definition_text = line[open_bracket_pos+1:close_bracket_pos].strip()
                        in_translation = False

        if in_constants:
            if '{' in line:
                brace_level += line.count('{')
            if '}' in line:
                brace_level -= line.count('}')

            if brace_level == 1:
                const = line.split(';')[0].split('//')[0].strip()
                if const:
                    used_constants.append(const)
            if brace_level <= 0:
                in_constants = False

        for const in used_constants:
            if const == '{':
                used_constants.remove(const)
    return {
        'definition': definition_text,
        'constants': used_constants
    }
        

def process_constants(concepts_list):
    processed = []
    
    for item in concepts_list:
        item = item.strip().strip("'\"")

        parts = [part.strip() for part in item.split(';') if part.strip()]
        
        for part in parts:
            for prefix in ['nrel_', 'rrel_', 'concept_']:
                if part.startswith(prefix):
                    part = part[len(prefix):]

            if part:
                processed.append(part)

    for i in range(len(processed)):
        processed[i] = processed[i].replace('_', ' ')
    
    return processed

def make_context(question: str):
    context = f"{question}"
    en_question = translate_ru_to_en(question)
    terms = extract_en_terms(en_question)
    print(terms)
    for term in terms:
        target_term_file_content = get_scs_content(term)

        if target_term_file_content is None:
            print(f"Не найден файл для термина: {term}")
            continue
            
        definition_block = extract_definition_block(target_term_file_content)
        definition_block_extra_case = extract_definition_block_extra_case(target_term_file_content)
        
        if definition_block is None and definition_block_extra_case is None:
            print(f"Не найден блок определения для термина: {term}")
            continue
        
        definitions_and_constants = None
        
        if definition_block:
            definitions_and_constants = extract_definition_and_constants(definition_block)
        elif definition_block_extra_case:
            definitions_and_constants = extract_definition_and_constants_extra_case(definition_block_extra_case)
                
        if definitions_and_constants and (definitions_and_constants['definition'] or definitions_and_constants['constants']):
            if definitions_and_constants['constants']:
                definitions_and_constants['constants'] = process_constants(definitions_and_constants['constants'])
                context += f" {' '.join(definitions_and_constants['constants'])}"
                
            if definitions_and_constants['definition']:
                context += f" {definitions_and_constants['definition']}"
    
    return context