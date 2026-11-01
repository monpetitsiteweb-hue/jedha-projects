# AT&T Spam Detector (Jedha, Bloc 4)

This project builds a spam detector for SMS, based only on the content of the message. The notebook compares a TF-IDF baseline with three deep learning models, selects a model on the validation set, then evaluates it on the test set.

## Result

The selected model uses frozen pre-trained word vectors and a Bidirectional GRU. On the test set (765 SMS, 90 spams): accuracy 97.91%, precision 94.05%, recall 87.78%, F1 90.80%, ROC AUC 0.9897.

## Install

The versions in `requirements.txt` are the exact versions of the run, on Windows with Python 3.13.9. From `08_att_spam/`:

```bash
python -m venv .venv
```

```bash
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

`requirements.txt` also installs the `en_core_web_md` 3.8.0 vectors from the spaCy GitHub release.

**Antivirus:** with Avast inspecting HTTPS traffic, `python -m spacy download en_core_web_md` fails with `CERTIFICATE_VERIFY_FAILED` on `raw.githubusercontent.com`. Installing through pip avoids this command, and `pip` still verifies the certificate.

## Run

```bash
.venv/Scripts/python.exe -m nbconvert --to notebook --execute --inplace att_spam_detector.ipynb
```

This takes about one minute on a CPU, and replaces the notebook outputs, `spam_detector.keras`, `results_validation.csv` and `result_test.csv`. With the fixed seed, a new run on this environment gives the same results. A different system or set of versions may give different numbers.

## Files

- `att_spam_detector.ipynb`: the notebook, and `att_spam_detector.html` for reading without Jupyter.
- `spam.csv`: the dataset of the brief, read by the notebook.
- `spam_detector.keras`: the selected model.
- `results_validation.csv`: scores of all models on the validation set.
- `result_test.csv`: scores of the selected model on the test set.

## Note on DistilBERT

DistilBERT is present in the notebook but was not executed (`RUN_DISTILBERT = False`), because it needs a GPU or a lot of patience. It has no score. The transfer learning of the selected model uses pre-trained word vectors, not a complete pre-trained deep network.
