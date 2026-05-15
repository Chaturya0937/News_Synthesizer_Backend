import pandas as pd

# ============================================
# LOAD DATASETS
# ============================================

true_df = pd.read_csv("True.csv")
fake_df = pd.read_csv("Fake.csv")

# ============================================
# CREATE LABEL COLUMN
# ============================================

# REAL NEWS
true_df['label'] = 1

# FAKE NEWS
fake_df['label'] = 0

# ============================================
# KEEP REQUIRED COLUMNS
# ============================================

true_df = true_df[['title', 'text', 'label']]
fake_df = fake_df[['title', 'text', 'label']]

# ============================================
# COMBINE DATASETS
# ============================================

df = pd.concat([true_df, fake_df], ignore_index=True)

# ============================================
# REMOVE EMPTY VALUES
# ============================================

df.dropna(inplace=True)

# ============================================
# COMBINE TITLE + TEXT
# ============================================

df['content'] = df['title'] + " " + df['text']

# ============================================
# SHUFFLE DATASET
# ============================================

df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# ============================================
# SAVE FINAL DATASET
# ============================================

df.to_csv("combined_news_dataset.csv", index=False)

# ============================================
# DISPLAY RESULTS
# ============================================

print(df.head())

print("\nTOTAL DATA:")
print(df.shape)

print("\nLABEL COUNTS:")
print(df['label'].value_counts())

print("\nDATASET SAVED SUCCESSFULLY")