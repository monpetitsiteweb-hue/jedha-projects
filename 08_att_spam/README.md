# AT&T Spam Detector (Jedha, Bloc 4)

This project builds a spam detector for SMS, based only on the content of the message. The notebook compares a TF-IDF baseline with four deep learning models, selects a model on the validation set, then evaluates it on the test set.

## Result

The selected model is DistilBERT, a pre-trained language model fine-tuned on the SMS. On the test set (765 SMS, 90 spams): accuracy 98.95%, precision 95.56%, recall 95.56%, F1 95.56%, ROC AUC 0.9947.

The lighter model, frozen pre-trained word vectors with a Bidirectional GRU, reaches an F1 of 95.40% on the validation set against 96.09% for DistilBERT. It is the model saved in `spam_detector.keras`.

## Install

The versions in `requirements.txt` are the exact versions of the run, on Windows with Python 3.13. From `08_att_spam/`:

```bash
python -m venv .venv
```

```bash
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

`requirements.txt` also installs the `en_core_web_md` 3.8.0 vectors from the spaCy GitHub release, and `torch` and `transformers` for DistilBERT.

**Antivirus:** with Avast inspecting HTTPS traffic, `python -m spacy download en_core_web_md` fails with `CERTIFICATE_VERIFY_FAILED` on `raw.githubusercontent.com`. Installing through pip avoids this command, and `pip` still verifies the certificate.

## Run

```bash
.venv/Scripts/python.exe -m nbconvert --to notebook --execute --inplace att_spam_detector.ipynb
```

The first run downloads DistilBERT from Hugging Face (about 268 MB). The whole notebook takes a few minutes on a CPU, and replaces the notebook outputs, `spam_detector.keras`, `results_validation.csv` and `result_test.csv`. With the fixed seed, a new run on this environment gives the same results. A different system or set of versions may give different numbers. Setting `RUN_DISTILBERT = False` in the notebook skips the DistilBERT cell.

## Files

- `att_spam_detector.ipynb`: the notebook, and `att_spam_detector.html` for reading without Jupyter.
- `spam.csv`: the dataset of the brief, read by the notebook.
- `spam_detector.keras`: the best Keras model (pre-trained word vectors + Bidirectional GRU). DistilBERT is not saved by the notebook.
- `results_validation.csv`: scores of all models on the validation set.
- `result_test.csv`: scores of the selected model on the test set.

## Note on DistilBERT

DistilBERT (66 million parameters) is fine-tuned for 2 passes on the 3,567 training SMS, with the same class weights as the other models. It gives the best validation F1 and is the selected model. The notebook keeps a lighter alternative, the pre-trained word vectors with a Bidirectional GRU, 64,193 trained parameters, which is cheaper to run and close in score.
