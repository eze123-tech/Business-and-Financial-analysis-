# Financial Statements Analyzer

A Streamlit app (blue and gold theme) that collects income statement and balance
sheet inputs, displays both statements, checks that the balance sheet balances,
and calculates liquidity, profitability, leverage and efficiency ratios.

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit interface |
| `finance.py` | Statement models and ratio calculations |
| `requirements.txt` | Python dependencies |
| `.streamlit/config.toml` | Blue and gold theme |

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open http://localhost:8501.

## Deploy free on Streamlit Community Cloud

1. Create a GitHub repository and push this folder to it (keep `app.py` in the repo root):
   ```bash
   git init
   git add .
   git commit -m "Financial statements app"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **Create app**, pick your repository and branch, and set the main file path to `app.py`.
4. Click **Deploy**. Your app will be live at a public `*.streamlit.app` URL in a minute or two.

Any later `git push` redeploys the app automatically.
