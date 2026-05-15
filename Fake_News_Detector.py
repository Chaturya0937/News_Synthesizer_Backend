# ============================================
# FAKE NEWS DETECTION USING DISTILBERT
# ============================================

# INSTALL REQUIRED LIBRARIES:
# pip install transformers datasets torch scikit-learn pandas

# ============================================
# STEP 1 — IMPORT LIBRARIES
# ============================================

import pandas as pd
import torch

from sklearn.model_selection import train_test_split

from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    TrainingArguments,
    Trainer,
    pipeline
)

# ============================================
# STEP 2 — LOAD DATASET
# ============================================

# Dataset CSV format:
#
# title,text,label
#
# label:
# 0 = FAKE
# 1 = REAL

df = pd.read_csv(
    "combined_news_dataset.csv",
    encoding='latin1'
)

print(df.head())

# ============================================
# STEP 3 — TRAIN TEST SPLIT
# ============================================

train_texts, val_texts, train_labels, val_labels = train_test_split(
    df['text'].tolist(),
    df['label'].tolist(),
    test_size=0.2,
    random_state=42
)

# ============================================
# STEP 4 — LOAD TOKENIZER
# ============================================

tokenizer = DistilBertTokenizerFast.from_pretrained(
    'distilbert-base-uncased'
)

# ============================================
# STEP 5 — TOKENIZE TEXT
# ============================================

train_encodings = tokenizer(
    train_texts,
    truncation=True,
    padding=True,
    max_length=512
)

val_encodings = tokenizer(
    val_texts,
    truncation=True,
    padding=True,
    max_length=512
)

# ============================================
# STEP 6 — CREATE PYTORCH DATASET
# ============================================

class NewsDataset(torch.utils.data.Dataset):

    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):

        item = {
            key: torch.tensor(val[idx])
            for key, val in self.encodings.items()
        }

        item['labels'] = torch.tensor(self.labels[idx])

        return item

    def __len__(self):
        return len(self.labels)

# ============================================
# STEP 7 — PREPARE DATASETS
# ============================================

train_dataset = NewsDataset(
    train_encodings,
    train_labels
)

val_dataset = NewsDataset(
    val_encodings,
    val_labels
)

# ============================================
# STEP 8 — LOAD MODEL
# ============================================

model = DistilBertForSequenceClassification.from_pretrained(
    'distilbert-base-uncased',
    num_labels=2
)

# ============================================
# STEP 9 — TRAINING CONFIGURATION
# ============================================

training_args = TrainingArguments(
    output_dir='./results',

    num_train_epochs=3,

    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,

    warmup_steps=500,

    weight_decay=0.01,

    logging_dir='./logs',

    logging_steps=10,

    evaluation_strategy="epoch",

    save_strategy="epoch"
)

# ============================================
# STEP 10 — TRAINER
# ============================================

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

# ============================================
# STEP 11 — TRAIN MODEL
# ============================================

trainer.train()

# ============================================
# STEP 12 — SAVE MODEL
# ============================================

model.save_pretrained("./fake_news_model")

tokenizer.save_pretrained("./fake_news_model")

print("\nMODEL SAVED SUCCESSFULLY")

# ============================================
# STEP 13 — LOAD TRAINED MODEL
# ============================================

classifier = pipeline(
    "text-classification",
    model="./fake_news_model",
    tokenizer="./fake_news_model"
)

# ============================================
# STEP 14 — TEST ON NEW ARTICLE
# ============================================

article = """
Scientists claim aliens built the pyramids
using advanced technology hidden by governments.
"""

result = classifier(article)

# ============================================
# STEP 15 — DISPLAY RESULT
# ============================================

label = result[0]['label']
score = result[0]['score']

if label == "LABEL_0":
    prediction = "FAKE NEWS"
else:
    prediction = "REAL NEWS"

print("\n===================================")
print("PREDICTION :", prediction)
print("CONFIDENCE :", round(score * 100, 2), "%")
print("===================================")