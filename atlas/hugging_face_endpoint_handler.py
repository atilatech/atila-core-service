from typing import Dict

from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import whisper
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import pytube
import time


class EndpointHandler():
    # load the model
    WHISPER_MODEL_NAME = "tiny.en"
    SENTENCE_TRANSFORMER_MODEL_NAME = "multi-qa-mpnet-base-dot-v1"
    QUESTION_ANSWER_MODEL_NAME = "vblagoje/bart_lfqa"
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def __init__(self, path=""):

        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f'whisper and question_answer_model will use: {device}')

        t0 = time.time()
        self.whisper_model = whisper.load_model(self.WHISPER_MODEL_NAME).to(device)
        t1 = time.time()

        total = t1 - t0
        print(f'Finished loading whisper_model in {total} seconds')

        t0 = time.time()
        self.sentence_transformer_model = SentenceTransformer(self.SENTENCE_TRANSFORMER_MODEL_NAME)
        t1 = time.time()

        total = t1 - t0
        print(f'Finished loading sentence_transformer_model in {total} seconds')
        
        self.question_answer_tokenizer = AutoTokenizer.from_pretrained(self.QUESTION_ANSWER_MODEL_NAME)
        t0 = time.time()
        self.question_answer_model = AutoModelForSeq2SeqLM.from_pretrained(self.QUESTION_ANSWER_MODEL_NAME).to(device)
        t1 = time.time()
        total = t1 - t0
        print(f'Finished loading question_answer_model in {total} seconds')

    def __call__(self, data: Dict[str, str]) -> Dict:
        """
        Args:
            data (:obj:):
                includes the URL to video for transcription
        Return:
            A :obj:`dict`:. transcribed dict
        """
        # process input
        print('data', data)

        if "inputs" not in data:
            raise Exception(f"data is missing 'inputs' key which  EndpointHandler expects. Received: {data}"
                            f" See: https://huggingface.co/docs/inference-endpoints/guides/custom_handler#2-create-endpointhandler-cp")
        video_url = data.pop("video_url", None)
        query = data.pop("query", None)
        long_form_answer = data.pop("long_form_answer", None)
        encoded_segments = {}
        if video_url:
            video_with_transcript = self.transcribe_video(video_url)
            video_with_transcript['transcript']['transcription_source'] = f"whisper_{self.WHISPER_MODEL_NAME}"
            encode_transcript = data.pop("encode_transcript", True)
            if encode_transcript:
                encoded_segments = self.combine_transcripts(video_with_transcript)
                encoded_segments = {
                    "encoded_segments": self.encode_sentences(encoded_segments)
                }
            return {
                **video_with_transcript,
                **encoded_segments
            }
        elif query:
            if long_form_answer:
                context = data.pop("context", None)
                answer = self.generate_answer(query, context)
                response = {
                    "answer": answer
                }

                return response
            else:
                query = [{"text": query, "id": ""}] if isinstance(query, str) else query
                encoded_segments = self.encode_sentences(query)

                response = {
                    "encoded_segments": encoded_segments
                }

                return response

        else:
            return {
                "error": "'video_url' or 'query' must be provided"
            }

    def transcribe_video(self, video_url):
        decode_options = {
            # Set language to None to support multilingual,
            # but it will take longer to process while it detects the language.
            # Realized this by running in verbose mode and seeing how much time
            # was spent on the decoding language step
            "language": "en",
            "verbose": True
        }
        yt = pytube.YouTube(video_url)
        video_info = {
            'id': yt.video_id,
            'thumbnail': yt.thumbnail_url,
            'title': yt.title,
            'views': yt.views,
            'length': yt.length,
            # Althhough, this might seem redundant since we already have id
            # but it allows the link to the video be accessed in 1-click in the API response
            'url': f"https://www.youtube.com/watch?v={yt.video_id}"
        }
        stream = yt.streams.filter(only_audio=True)[0]
        path_to_audio = f"{yt.video_id}.mp3"
        stream.download(filename=path_to_audio)
        t0 = time.time()
        transcript = self.whisper_model.transcribe(path_to_audio, **decode_options)
        t1 = time.time()
        for segment in transcript['segments']:
            # Remove the tokens array, it makes the response too verbose
            segment.pop('tokens', None)

        total = t1 - t0
        print(f'Finished transcription in {total} seconds')

        # postprocess the prediction
        return {"transcript": transcript, 'video': video_info}

    def encode_sentences(self, transcripts, batch_size=64):
        """
        Encoding all of our segments at once or storing them locally would require too much compute or memory.
        So we do it in batches of 64
        :param transcripts:
        :param batch_size:
        :return:
        """
        # loop through in batches of 64
        all_batches = []
        for i in tqdm(range(0, len(transcripts), batch_size)):
            # find end position of batch (for when we hit end of data)
            i_end = min(len(transcripts), i + batch_size)
            # extract the metadata like text, start/end positions, etc
            batch_meta = [{
                **row
            } for row in transcripts[i:i_end]]
            # extract only text to be encoded by embedding model
            batch_text = [
                row['text'] for row in batch_meta
            ]
            # create the embedding vectors
            batch_vectors = self.sentence_transformer_model.encode(batch_text).tolist()

            batch_details = [
                {
                    **batch_meta[x],
                    'vectors': batch_vectors[x]
                } for x in range(0, len(batch_meta))
            ]
            all_batches.extend(batch_details)

        return all_batches

    def generate_answer(self, query, documents):

        # concatenate question and support documents into BART input
        conditioned_doc = "<P> " + " <P> ".join([d for d in documents])
        query_and_docs = "question: {} context: {}".format(query, conditioned_doc)

        model_input = self.question_answer_tokenizer(query_and_docs, truncation=False, padding=True, return_tensors="pt")

        generated_answers_encoded = self.question_answer_model.generate(input_ids=model_input["input_ids"].to(self.device),
                                                attention_mask=model_input["attention_mask"].to(self.device),
                                                min_length=64,
                                                max_length=256,
                                                do_sample=False, 
                                                early_stopping=True,
                                                num_beams=8,
                                                temperature=1.0,
                                                top_k=None,
                                                top_p=None,
                                                eos_token_id=self.question_answer_tokenizer.eos_token_id,
                                                no_repeat_ngram_size=3,
                                                num_return_sequences=1)
        answer = self.question_answer_tokenizer.batch_decode(generated_answers_encoded, skip_special_tokens=True,clean_up_tokenization_spaces=True)
        return answer

    @staticmethod
    def combine_transcripts(video, window=6, stride=3):
        """

        :param video:
        :param window: number of sentences to combine
        :param stride: number of sentences to 'stride' over, used to create overlap
        :return:
        """
        new_transcript_segments = []

        video_info = video['video']
        transcript_segments = video['transcript']['segments']
        for i in tqdm(range(0, len(transcript_segments), stride)):
            i_end = min(len(transcript_segments), i + window)
            text = ' '.join(transcript['text']
                            for transcript in
                            transcript_segments[i:i_end])
            # TODO: Should int (float to seconds) conversion happen at the API level?
            start = int(transcript_segments[i]['start'])
            end = int(transcript_segments[i]['end'])
            new_transcript_segments.append({
                **video_info,
                **{
                    'start': start,
                    'end': end,
                    'title': video_info['title'],
                    'text': text,
                    'id': f"{video_info['id']}-t{start}",
                    'url': f"https://youtu.be/{video_info['id']}?t={start}",
                    'video_id': video_info['id'],
                }
            })
        return new_transcript_segments
