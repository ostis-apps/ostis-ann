import re


class BaseCleaner:
    def __init__(self):
        self._chapter_letter_spacings = r"Г\sл\sа\sв\sа"
        self._section_letter_spacings = r"Р\sа\sз\sд\sе\sл"

        self._word_wrap_regex = r"(?<=[A-Za-zА-Яа-я])-\n(?=[a-zа-я]+)"
        self._multi_spase_regex = r"\s\s+"
        self._space_before_punctuation_regex = r"\s+([.,!?:;])"
        self._newline_space_regex = r"\n\s"
        self._multi_newline_regex = r"\n(\n\s*)*"
        self._image_regex = r"\((Рис|Рисунок|рис|рисунок)\.?\s*\d+(\.\d+)?(\.)?\s*(.+)\)"
        self._unicode_private_use_area_regex = r"[\uf000-\uffff]"
        self._em_space_regex = r"\u2003"
        self._biblio_regex = r"\s\[\d+.*\]\."

    def clean(self, text: str):
        text = re.sub(self._chapter_letter_spacings, self._chapter_letter_spacings.replace(r"\s", ""), text)
        text = re.sub(self._section_letter_spacings, self._section_letter_spacings.replace(r"\s", ""), text)
        text = re.sub(self._multi_spase_regex, " ", text)
        text = re.sub(self._word_wrap_regex, "", text)
        text = re.sub(self._multi_newline_regex, "\n", text)
        text = re.sub(self._unicode_private_use_area_regex, "", text)
        text = re.sub(self._em_space_regex, " ", text)
        text = re.sub(self._image_regex, "", text)
        text = re.sub(self._biblio_regex, "", text)
        text = re.sub(self._space_before_punctuation_regex, r"\1", text)
        text = re.sub(self._newline_space_regex, "\n", text)
        text = text.replace("\t", "")
        return text
