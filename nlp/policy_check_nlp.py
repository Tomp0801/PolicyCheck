import torch
from transformers import BertTokenizer, BertModel
from scipy.spatial.distance import cosine

# Laden Sie das vortrainierte BERT-Modell und den Tokenizer.
# model_name = "bert-semantic-similarity"
model_name = "bert-base-multilingual-cased"

tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)


# Beispiele von Texten, die Sie vergleichen möchten.
text1 = "Das ist der erste Text."
text2 = "Das ist ein ähnlicher Text."
text3 = "Mein Affe ist ein Hund"

# Tokenisieren und codieren Sie die Texte für das Modell.
inputs1 = tokenizer(text1, return_tensors="pt", padding=True, truncation=True)
inputs2 = tokenizer(text2, return_tensors="pt", padding=True, truncation=True)
inputs3 = tokenizer(text3, return_tensors="pt", padding=True, truncation=True)

# Berechnen Sie die BERT-Einbettungen (Embeddings) für die Texte.
with torch.no_grad():
    embeddings1 = model(**inputs1).last_hidden_state.mean(dim=1)
    embeddings2 = model(**inputs2).last_hidden_state.mean(dim=1)
    embeddings3 = model(**inputs3).last_hidden_state.mean(dim=1)


# Berechnen Sie die Kosinus-Ähnlichkeit zwischen den Einbettungen.
similarity = 1 -  cosine(embeddings1.squeeze(), embeddings2.squeeze())

# Ausgabe der Ähnlichkeit.
print(f"Ähnlichkeit zwischen den Texten: {similarity:.2f}")

similarity = 1 -  cosine(embeddings1.squeeze(), embeddings3.squeeze())
print(f"Ähnlichkeit zwischen den Texten: {similarity:.2f}")