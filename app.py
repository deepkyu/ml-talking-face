import os
import subprocess

REST_IP = os.environ['REST_IP']
SERVICE_PORT = int(os.environ['SERVICE_PORT'])
TRANSLATION_APIKEY_URL = os.environ['TRANSLATION_APIKEY_URL']
GOOGLE_APPLICATION_CREDENTIALS = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
subprocess.call(f"wget --no-check-certificate -O {GOOGLE_APPLICATION_CREDENTIALS} {TRANSLATION_APIKEY_URL}", shell=True)

import gradio as gr
from client_rest import RestAPIApplication
from pathlib import Path
import argparse
import threading
from translator import GoogleAuthTranslation
import yaml

TITLE = Path("docs/title.txt").read_text()
DESCRIPTION = Path("docs/description.txt").read_text()

class Translator:
    def __init__(self, yaml_path='lang.yaml'):
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
        lang_finder = [name for name in self.supporting_languages
                        if self.supporting_languages[name]['language'] == lang]
        if len(lang_finder) == 1:
            lang = lang_finder[0]
        else:
            raise AssertionError(f"Given language index can't be understood! | lang: {lang}")
        
        return lang

    def get_translation(self, text, lang, use_translation=True):
        lang_ = self._convert_lang_from_index(lang)
        
        if use_translation:
            target_text, _ = self._get_text_with_lang(text, lang_)
        else:
            target_text = text

        return target_text, lang 
    
    
class GradioApplication:
    def __init__(self, rest_ip, rest_port, max_seed):
        self.lang_list = {
            'Korean': 'ko_KR',
            'English': 'en_US',
            'Japanese': 'ja_JP',
            'Chinese': 'zh_CN'
        }
        self.background_list = [None,
                                "background_image/cvpr.png",
                                "background_image/black.png",
                                "background_image/river.mp4",
                                "background_image/sky.mp4"]
        
        self.translator = Translator()
        self.rest_application = RestAPIApplication(rest_ip, rest_port)
        self.output_dir = Path("output_file")

        inputs = prepare_input()
        outputs = prepare_output()

        self.iface = gr.Interface(fn=self.infer,
                                  title=TITLE,
                                  description=DESCRIPTION,
                                  inputs=inputs,
                                  outputs=outputs,
                                  allow_flagging='never',
                                  article=Path("docs/article.md").read_text())

        self.max_seed = max_seed
        self._file_seed = 0
        self.lock = threading.Lock()
        
    
    def _get_file_seed(self):
        return f"{self._file_seed % self.max_seed:02d}"

    def _reset_file_seed(self):
        self._file_seed = 0

    def _counter_file_seed(self):
        with self.lock:
            self._file_seed += 1

    def get_lang_code(self, lang):
        return self.lang_list[lang]

    def get_background_data(self, background_index):
        # get background filename and its extension
        data_path = self.background_list[background_index]

        if data_path is not None:
            with open(data_path, 'rb') as rf:
                background_data = rf.read()
            is_video_background = str(data_path).endswith(".mp4")
        else:
            background_data = None
            is_video_background = False

        return background_data, is_video_background

    def infer(self, text, lang, duration_rate, pad_begin, pad_end, action, background_index):
        self._counter_file_seed()
        print(f"File Seed: {self._file_seed}")
        target_text, lang_dest = self.translator.get_translation(text, lang)
        lang_rpc_code = self.get_lang_code(lang_dest)

        background_data, is_video_background = self.get_background_data(background_index)
        
        video_data = self.rest_application.get_video(target_text, lang_rpc_code, duration_rate, pad_begin, pad_end, action.lower(),
                                                     background_data, is_video_background)
        print(len(video_data))

        video_filename = self.output_dir / f"{self._file_seed:02d}.mkv"
        with open(video_filename, "wb") as video_file:
            video_file.write(video_data)
        
        return f"Language: {lang_dest}\nText: \n{target_text}", str(video_filename)        

    def run(self, server_port=7860, share=False):
        try:
            self.iface.launch(height=900,
                              share=share, server_port=server_port,
                              enable_queue=True)
        
        except KeyboardInterrupt:
            gr.close_all()


def prepare_input():
    text_input = gr.Textbox(lines=2,
                            placeholder="Type your text with English, Chinese, Korean, and Japanese.",
                            value="Hello, this is demonstration for talking face generation "
                            "with multilingual text-to-speech.",
                            label="Text")
    lang_input = gr.Radio(['Korean', 'English', 'Japanese', 'Chinese'],
                          type='value',
                          value=None,
                          label="Language")
    duration_rate_input = gr.Slider(minimum=0.8,
                                    maximum=1.2,
                                    step=0.01,
                                    value=1.0,
                                    label="Duration (The bigger the value, the slower it pronounces)")
    start_padding_input = gr.Slider(minimum=0.0,
                                    maximum=2.0,
                                    step=0.1,
                                    value=0.0,
                                    label="Start padding (s)")
    end_padding_input = gr.Slider(minimum=0.0,
                                  maximum=2.0,
                                  step=0.1,
                                  value=0.0,
                                  label="End padding (s)")
    action_input = gr.Radio(['Default', 'Hand', 'BothHand', 'HandDown', 'Sorry'],
                            type='value',
                            value='Default',
                            label="Select an action ...")
    background_input = gr.Radio(['None', 'CVPR', 'Black', 'River', 'Sky'],
                                type='index',
                                value='None',
                                label="Select a background image/video ...")

    return [text_input, lang_input,
            duration_rate_input, start_padding_input, end_padding_input,
            action_input, background_input]


def prepare_output():
    translation_result_otuput = gr.Textbox(type="str",
                                                   label="Translation Result")

    video_output = gr.Video(format='mp4')
    return [translation_result_otuput, video_output]


def parse_args():
    parser = argparse.ArgumentParser(
        description='GRADIO DEMO for talking face generation submitted to CVPR2022')
    parser.add_argument('-p', '--port', dest='gradio_port', type=int, default=7860, help="Port for gradio")
    parser.add_argument('--rest_ip', type=str, default=REST_IP, help="IP for REST API")
    parser.add_argument('--rest_port', type=int, default=SERVICE_PORT, help="Port for REST API")
    parser.add_argument('--max_seed', type=int, default=20, help="Max seed for saving video")
    parser.add_argument('--share', action='store_true', help='get publicly sharable link')
    args = parser.parse_args()
    return args    


if __name__ == '__main__':
    args = parse_args()
    
    gradio_application = GradioApplication(args.rest_ip, args.rest_port, args.max_seed)
    gradio_application.run(server_port=args.gradio_port, share=args.share)
    
