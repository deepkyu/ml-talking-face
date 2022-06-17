This system generates a talking face video based on the input text.
You can provide the input text in one of the four languages: Chinese (Mandarin), English, Japanese, and Korean.
You may also select the target language, the language of the output speech.
If the input text language and the target language are different, the input text will be translated to the target language using Google Translate API. 

### Updates

(2022.06.17.) We were originally planning to support any input text. However, when checking the logs recently, we found that there were a lot of inappropriate input texts. So, we decided to filter the inputs based on toxicity using [Perspective API @Google](https://developers.perspectiveapi.com/s/). Now, if you enter a possibily toxic text, the video generation will fail. We hope you understand.

(2022.06.05.) Due to the latency from HuggingFace Spaces and video rendering, it takes 15 ~ 30 seconds to get a video result.