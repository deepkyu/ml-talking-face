from .v3 import GoogleAuthTranslation
from pathlib import Path
import yaml
import os

MAX_ENG_TEXT_LENGTH = int(os.getenv('MAX_ENG_TEXT_LENGTH', 200))
MAX_CJK_TEXT_LENGTH = int(os.getenv('MAX_CJK_TEXT_LENGTH', 100))

class Translator:
    def __init__(self, yaml_path='./lang.yaml'):
        self.google_translation = GoogleAuthTranslation(project_id="cvpr-2022-demonstration")
        with open(yaml_path) as f:
            self.supporting_languages = yaml.load(f, Loader=yaml.FullLoader)
    
    @staticmethod 
    def length_check(lang, text):
        if lang in ['en']:
            if len(text) > MAX_ENG_TEXT_LENGTH:
                raise AssertionError(f"Input text is too long. For English, the text length should be less than {MAX_ENG_TEXT_LENGTH}. | Length: {len(text)}")
        elif lang in ['ko', 'ja', 'zh-CN', 'zh']:
            if len(text) > MAX_CJK_TEXT_LENGTH:
                raise AssertionError(f"Input text is too long. For CJK, the text length should be less than {MAX_CJK_TEXT_LENGTH}. | Length: {len(text)}")
        else:
            raise AssertionError(f"Not in ['ko', 'ja', 'zh-CN', 'zh', 'en'] ! | Language: {lang}")
        
        return
        
    def _get_text_with_lang(self, text, lang):
        lang_detected = self.google_translation.detect(text)
        print(f"Detected as: {lang_detected} | Destination: {lang}")
        
        if lang is None:
            lang = lang_detected
            
        if lang != lang_detected:
            target_text = self.google_translation.translate(text, lang=lang)
        else:
            target_text = text
                
        return target_text, lang
    
    def _convert_lang_from_index(self, lang):
        try:
            lang = [name for name in self.supporting_languages
                    if self.supporting_languages[name]['language'] == lang][0]
        except Exception as e:
            raise RuntimeError(e)
        
        return lang

    def get_translation(self, text, lang, use_translation=True):
        lang_ = self._convert_lang_from_index(lang)
        
        if use_translation:
            target_text, _ = self._get_text_with_lang(text, lang_)
        else:
            target_text = text

        return target_text, lang_ 