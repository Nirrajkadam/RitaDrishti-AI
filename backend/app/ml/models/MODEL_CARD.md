# Model Card: RitaDrishti Fake Review Classifier

## Model Overview
- **Model Architecture**: Scikit-Learn Pipeline (`ColumnTransformer` combining TF-IDF N-gram vectorizer + StandardScaler for 6 text style features -> `LogisticRegression`).
- **Artifact File**: `fake_review_model.joblib`
- **SHA-256 Checksum**: `8bf3a042511c3d883d11ded7d146b00ae2deafa77a83dd69d61dd97f74976651`
- **Release Version**: 1.0.0

## Intended Use
Determines probability $[0.0, 1.0]$ of deceptive or fraudulent online customer review text based on lexical diversity entropy, character case ratios, exclamation frequency, and generic spam phrase matching.

## Evaluation Metrics (Evaluated on Test Split, `random_state=42`)
- **Test Sample Size**: 7 samples
- **Accuracy**: 1.0
- **Precision**: 1.0
- **Recall**: 1.0
- **F1 Score**: 1.0
- **PR-AUC**: 1.0
- **Confusion Matrix**: `[[4, 0], [0, 3]]`

## Ethical Considerations & Limitations
- Model is trained on English text review data.
- Intended for automated risk scoring assistance, not sole decision-making for user bans.
