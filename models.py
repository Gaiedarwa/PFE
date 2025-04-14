import torch
from transformers import BertTokenizer, BertModel
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import re


# Modèle BERT pré-entraîné
class BERTModel(nn.Module):
    def __init__(self):
        super(BERTModel, self).__init__()
        self.bert = BertModel.from_pretrained('bert-base-uncased')
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(self.bert.config.hidden_size, 1)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        pooled_output = self.dropout(pooled_output)
        outputs = self.classifier(pooled_output)
        return outputs

class SimilarityDataset(Dataset):
    def __init__(self, texts1, texts2, labels, tokenizer):
        self.texts1 = texts1
        self.texts2 = texts2
        self.labels = labels
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts1)

    def __getitem__(self, idx):
        encoding1 = self.tokenizer(self.texts1[idx], return_tensors='pt', max_length=512, padding='max_length', truncation=True)
        encoding2 = self.tokenizer(self.texts2[idx], return_tensors='pt', max_length=512, padding='max_length', truncation=True)
        label = torch.tensor(self.labels[idx], dtype=torch.float)
        return {
            'input_ids1': encoding1['input_ids'].flatten(),
            'attention_mask1': encoding1['attention_mask'].flatten(),
            'input_ids2': encoding2['input_ids'].flatten(),
            'attention_mask2': encoding2['attention_mask'].flatten(),
            'label': label
        }

def calculate_similarity(text1, text2):
    # Fine-tuning du modèle BERT
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Création du dataset et du dataloader
    dataset = SimilarityDataset([text1], [text2], [1], tokenizer)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False)

    # Chargement du modèle
    model = BERTModel()
    model.to(device)

    # Fine-tuning (ajoutez ici votre logique de fine-tuning si nécessaire)

    # Calcul de la similarité après fine-tuning (ou directement si fine-tuning n'est pas nécessaire)
    
    with torch.no_grad():
        encoding1 = tokenizer(text1, return_tensors='pt', padding=True).to(device)
        encoding2 = tokenizer(text2, return_tensors='pt', padding=True).to(device)

        outputs1 = model(**encoding1).logits.squeeze()
        outputs2 = model(**encoding2).logits.squeeze()

        similarity_score = torch.cosine_similarity(outputs1.unsqueeze(0), outputs2.unsqueeze(0)).item()

    return similarity_score * 100  # Retourne le score en pourcentage

def extract_entities(text):
    patterns = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
        'téléphone': r'\+?\d{1,4}[-.\s]?(?:\(\d+\)[-.\s]?)?\d{3}[-.\s]?\d{4}',
        'nom': r'(?i)\b(?:[A-ZÀ-ÂÇÉÈÊËÎÏÔÙÛÜ][a-zà-âçéèêëîïôùûü]+\b[\s-]*){2,}'
    }
    
    entities = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            entities[key] = match.group().strip()
    
    return entities


def validate_personal_info(info):
     if not info.get('email'):
         raise ValueError("L'email est requis")
