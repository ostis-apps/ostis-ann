from sc_kpm import ScModule
from .AgentTranslationLanguage import LanguageTranslator


class LanguageTranslatorModule(ScModule):
    def __init__(self):
        super().__init__(LanguageTranslator())