import json
import os
import re

import django
from langchain_community.embeddings import OpenAIEmbeddings

# Setzen Sie das Django-Einstellungsmodul
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pvs_backend')

# Initialisieren Sie Django
django.setup()

from pinecone import Pinecone

from gpt_model_manger import GPTModelManager


pc = Pinecone(api_key="49434cc5-3257-4091-bceb-958989eab291")
index = pc.Index("pvs-index")

namespace = "analog-catalog"
#
# # Alle Einträge im angegebenen Namespace löschen
# index.delete(delete_all=True, namespace=namespace)


EMBEDDINGS_GPT = OpenAIEmbeddings(deployment="TEXT-EMBEDDING-ADA-UK-SOUTH",
                                  openai_api_key="7c53126a3d674474a76176d04ad0cfe8",
                                  openai_api_base="https://ai-platform-resource-uk-south.openai.azure.com/",
                                  openai_api_type="azure",
                                  openai_api_version="2023-05-15"
                                  )

# JSON-Datei laden
with open("AnalogKatalogJson.json", "r", encoding="utf-8") as f:
    data = json.load(f)


# Funktion, um IDs zu normalisieren
def normalize_id(section, index):
    return re.sub(r'[^a-zA-Z0-9]', '_', f"{section}_{index}")

# Embeddings erstellen und in Pinecone hochladen
vectors = []
# for section_index, (section, sentences) in enumerate(data.items(), start=1):
#     for sentence_index, sentence in enumerate(sentences, start=1):
#         embedding = EMBEDDINGS_GPT.embed_query(sentence)
#         vec_id = normalize_id(section_index, sentence_index)
#         vectors.append({
#             "id": vec_id,
#             "values": embedding,
#             "metadata": {"section": section, "sentence": sentence}
#         })
#
# print("baaam")
#
# # Daten in Pinecone-Index hochladen
# index.upsert(vectors=vectors, namespace=namespace)


print("baaam")


# Schritt 1: Erstellen Sie das Query-Embedding
query_text = "20300 ET Hier Anwendung von Kariesdetektor je Zahn; gemäß § 6 Abs.1 GOZ"  # Beispiel-Suchtext
query_embedding = EMBEDDINGS_GPT.embed_query(query_text)

# Sicherstellen, dass der Vektor eine Python-Liste ist
query_embedding = list(query_embedding)

# Schritt 2: Ähnlichkeitssuche in Pinecone durchführen
top_k = 5  # Anzahl der gewünschten Top-Ergebnisse
response = index.query(vector=query_embedding, top_k=top_k, namespace=namespace, include_metadata=True)

# Schritt 3: Ergebnisse anzeigen
for match in response['matches']:
    print(f"ID: {match['id']}, Score: {match['score']}, Metadata: {match['metadata']}")



# # Liste von Beispieltexten
# texts = [
#     "Zahnmedizinische Dienstleistung A",
#     "Zahnmedizinische Dienstleistung B",
#     "Zahnmedizinische Dienstleistung C"
# ]
#
# # Erstellung der Embeddings für alle Texte
# embeddings = EMBEDDINGS_GPT.embed_documents(texts)
#
# # Ausgabe der Embeddings
# for text, embedding in zip(texts, embeddings):
#     print(f"Text: {text}\nEmbedding: {embedding}\n")

# # Strukturieren Sie die Daten mit IDs
# data_to_insert = [(str(i), embeddings[i]) for i in range(len(embeddings))]
#
# # Daten in Pinecone einfügen
# index.upsert(vectors=data_to_insert)
