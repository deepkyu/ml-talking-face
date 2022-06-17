from .v3 import GoogleAuthTranslation
from pathlib import Path
import yaml


class Translator:
    def __init__(self, yaml_path='./lang.yaml'):
        self.google_translation = GoogleAuthTranslation(project_id="cvpr-2022-demonstration")
        with open(yaml_path) as f:
            self.supporting_languages = yaml.load(f, Loader=yaml.FullLoader)
            
    def _get_text_with_lang(self, text, lang):
        lang_detected = self.google_translation.detect(text)
        print(lang_detected, lang)
        if lang is None:
            lang = lang_detected
            
        if lang != lang_detected:
            target_text = self.google_translation.translate(text, lang=lang)
        else:
            target_text = text
            
        return target_text, lang
    
    def _convert_lang_from_index(self, lang):
        try:
            lang_finder = [name for name in self.supporting_languages
                            if self.supporting_languages[name]['language'] == lang]
        except Exception as e:
            raise RuntimeError(e)
        
        if len(lang_finder) == 1:
            lang = lang_finder[0]
        else:
            raise AssertionError("Given language index can't be understood!"
                                 f"Only one of ['Korean', 'English', 'Japanese', 'Chinese'] can be supported. | lang: {lang}")
        
        return lang

    def get_translation(self, text, lang, use_translation=True):
        lang_ = self._convert_lang_from_index(lang)
        
        if use_translation:
            target_text, _ = self._get_text_with_lang(text, lang_)
        else:
            target_text = text

        return target_text, lang 