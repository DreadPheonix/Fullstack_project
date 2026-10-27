# SMS Shield

SMS Shield serves a spam-detection dashboard backed by a TF-IDF text classifier.

## Run

From the repository root, install the runtime dependencies and start FastAPI:

```powershell
python -m pip install -r requirement.txt
python app.py
```

Open `http://127.0.0.1:8000/`. The dashboard and `POST /predict` endpoint are served by the same application.

Routine OTP and package-shipment messages are treated as ham unless they contain links or common scam language. Run the regression tests with:

```powershell
python -m unittest discover -s tests
```
