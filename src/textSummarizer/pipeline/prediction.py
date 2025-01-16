from src.textSummarizer.config.configuration import ConfigurationManager
from transformers import AutoTokenizer
from transformers import pipeline

class PredictionPipeline:
    def __init__(self):
        self.config = ConfigurationManager().get_model_evaluation_config()

    def predict(self,text):
        tokenizer = AutoTokenizer.from_pretrained("artifacts/model_trainer/tokenizer")
        #gen_kwargs = {"length_penalty": 0.8, "num_beams":8, "max_length":128}
        gen_kwargs = {"max_length": 128,  "min_length": 30,   "length_penalty": 1.0,  "no_repeat_ngram_size": 3,"early_stopping": True}
        

        pipe = pipeline("summarization", model = "artifacts/model_trainer/pegasus-samsum-model", tokenizer= tokenizer)

        print("dialogue:")
        print(text)

        output = pipe(text, **gen_kwargs)[0]["summary_text"]
        print("\nModel Summary:")
        print(output)

        return output