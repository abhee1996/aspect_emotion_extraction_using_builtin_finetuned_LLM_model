from transformers import AutoTokenizer, AutoModelForTokenClassification,AutoModelForSequenceClassification, pipeline
import torch

device = "cpu"  # Heroku dynos are CPU-based

# Aspect Extraction Model
model_id_ate = "gauneg/roberta-base-absa-ate-sentiment"
tokenizer_ate = AutoTokenizer.from_pretrained(model_id_ate)
model_ate = AutoModelForTokenClassification.from_pretrained(model_id_ate)#.to(device)
senti_pipeline = pipeline(task='ner', model=model_ate, tokenizer=tokenizer_ate, device=device, aggregation_strategy='simple')

device = "mps" if torch.backends.mps.is_available() else 0 if torch.cuda.is_available() else -1
# Emotion Detection Model
emotion_model = "j-hartmann/emotion-english-distilroberta-base"
emo_tokenizer = AutoTokenizer.from_pretrained(emotion_model)
emo_model = AutoModelForSequenceClassification.from_pretrained(emotion_model)
classifier = pipeline("text-classification", model=emo_model,tokenizer=emo_tokenizer, top_k=None, device=device)


