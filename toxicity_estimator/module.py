from googleapiclient import discovery
import argparse
import json
import os

API_KEY = os.environ['PERSPECTIVE_API_KEY']

class PerspectiveAPI:
    def __init__(self):
        self.client = discovery.build(
                        "commentanalyzer",
                        "v1alpha1",
                        developerKey=API_KEY,
                        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
                        static_discovery=False,
                    )
    @staticmethod
    def _get_request(text):
        return {
            'comment': {'text': text},
            'requestedAttributes': {'TOXICITY': {}}
        }
    
    def _infer(self, text):
        request = self._get_request(text)
        response = self.client.comments().analyze(body=request).execute()
        return response
    
    def infer(self, text):
        return self._infer(text)
        
    def get_score(self, text, label='TOXICITY'):
        response = self._infer(text)
        return response['attributeScores'][label]['spanScores'][0]['score']['value']
    

def parse_args():
    parser = argparse.ArgumentParser(
        description='Perspective API Test.')
    parser.add_argument('-i', '--input-text', type=str, required=True)
    args = parser.parse_args()
    return args    


if __name__ == '__main__':
    args = parse_args()
    
    perspective_api = PerspectiveAPI()
    score = perspective_api.get_score(args.input_text)

    print(score)
