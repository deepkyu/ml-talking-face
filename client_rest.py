import requests
import json
import base64
import argparse

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
SPEAKER_ID = 0

class RestAPIApplication:
    def __init__(self, ip, port):
        
        if port < 0:
            self.post_request_addr = f"http://{ip}/register/"
            self.post_headers = {"Content-Type": "application/json"}
            self.generate_addr = (lambda id_: f'http://{ip}/generate/{id_}')
        else:
            self.post_request_addr = f"http://{ip}:{port}/register/"
            self.post_headers = {"Content-Type": "application/json"}
            self.generate_addr = (lambda id_: f'http://{ip}:{port}/generate/{id_}')

    @staticmethod
    def _get_json_request(text, lang, duration_rate, pad_begin, pad_end, action, background_data=None, is_video_background=False):
        request_form = dict()

        request_form['text'] = text
        request_form['speaker'] = SPEAKER_ID
        request_form['width'] = VIDEO_WIDTH
        request_form['height'] = VIDEO_HEIGHT

        request_form['action'] = action
        
        if background_data is not None:
            background_base64 = base64.b64encode(background_data).decode("UTF-8")
        else:
            background_base64 = ""
        
        request_form['background'] = background_base64
        request_form['durationRate'] = duration_rate
        request_form['isVideoBackground'] = is_video_background
        request_form['lang'] = lang

        request_as_json = json.dumps(request_form)
        return request_as_json

    @staticmethod
    def _get_video_id(results):
        return json.loads(bytes.decode(results.content))['id']

    def get_video(self, text, lang, duration_rate, pad_begin, pad_end, action, background_data=None, is_video_background=False):
        request_json = self._get_json_request(text, lang, duration_rate, pad_begin, pad_end, action, background_data, is_video_background)
        
        # POST request with jsonified request
        results = requests.post(self.post_request_addr, headers=self.post_headers, data=request_json)
        
        # GET video with the given id
        video_id = self._get_video_id(results)
        video_results = requests.get(self.generate_addr(video_id))
        
        return video_results.content


def parse_args():
    parser = argparse.ArgumentParser(
        description='REST API interface for talking face generation submitted to CVPR2022')
    parser.add_argument('-i', '--ip', dest='rest_ip', type=str, default="127.0.0.1", help="IP for REST API")
    parser.add_argument('-p', '--port', dest='rest_port', type=int, default=8080, help="Port for REST API")
    args = parser.parse_args()
    return args    


if __name__ == '__main__':
    args = parse_args()
    rest_api_application = RestAPIApplication(args.rest_ip, args.rest_port)    
