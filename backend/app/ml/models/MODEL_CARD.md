# Model Card: RitaDrishti Prototype Fake Review Classifier

## Model Overview
- **Model Architecture**: Scikit-Learn Pipeline (`ColumnTransformer` combining TF-IDF N-gram vectorizer + `StandardScaler` for 6 text style features -> `LogisticRegression`).
- **Artifact File**: `fake_review_model.joblib`
- **SHA-256 Checksum**: `9c7acf6cb562185255253c0498e61bfe8129fa207e9149ee0510f38690779617`
- **Release Version**: 1.0.0

## Dataset & Training Scope
- **Training Set Note**: Trained on a curated benchmark seed dataset of 22 representative reviews (12 legitimate, 10 deceptive) designed for pipeline verification and deterministic end-to-end testing.
- **Evaluation Split**: 7 samples evaluated on test split (`random_state=42`, stratified).
- **Accuracy**: 1.0 | **F1 Score**: 1.0
- **Production Recommendation**: For production enterprise deployment, replace `train_fake_review_model.py` dataset input with full public fake-review callsets (e.g. Amazon Deceptive Reviews / Yelp Spam Dataset).

## Intended Use
Calculates probability $[0.0, 1.0]$ of deceptive or fraudulent online customer review text based on lexical diversity entropy, character case ratios, exclamation frequency, and generic spam phrase matching.
