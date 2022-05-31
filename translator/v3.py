from google.cloud import translate
import yaml


class GoogleAuthTranslation:
    def __init__(self, project_id, yaml_path='lang.yaml'):
        self.translator = translate.TranslationServiceClient()
        self.location = "global"
        self.parent = f"projects/{project_id}/locations/{self.location}"
        
        with open(yaml_path) as f:
            self.supporting_languages = yaml.load(f, Loader=yaml.FullLoader)

    def _detect(self, query):
        response = self.translator.detect_language(
            request={
                "parent": self.parent,
                "content": query,
                "mime_type": "text/plain",  # mime types: text/plain, text/html
            }
        )

        for language in response.languages:
            # First language is the most confident one
            return language.language_code

    def _get_dest_from_lang(self, lang):
        try:
            return self.supporting_languages[lang]['google_dest']

        except KeyError as e:
            raise e
        
    def _get_lang_from_dest(self, dest):
        for key in self.supporting_languages:
            if self.supporting_languages[key]['google_dest'] == dest:
                return key
        
        raise RuntimeError(f"Detected langauge {dest} is not supported for TTS.")

    def translate(self, query, lang):

        dest = self._get_dest_from_lang(lang)

        response = self.translator.translate_text(
            request={
                "parent": self.parent,
                "contents": [query],
                "mime_type": "text/plain",  # mime types: text/plain, text/html
                "target_language_code": dest,
            }
        )

        return " ".join([translation.translated_text for translation in response.translations])

    def detect(self, query):
        dest = self._detect(query)
        return self._get_lang_from_dest(dest)
