# Virtual Typing Pro — Render deployment troubleshooting

This repository contains a Flask app (`app.py`) and a `Procfile`. If you see the error during Render deployment:

  ==> Service Root Directory "/opt/render/project/src/app.py" is missing.
  builder.sh: line 51: cd: /opt/render/project/src/app.py: Not a directory

that means Render's **Root Directory** setting was pointed at a file (`src/app.py`) instead of a directory. The deploy script runs `cd $SERVICE_ROOT` which must be a directory.

Quick fixes (choose one):

1) Fix the Root Directory on Render (recommended)

   - Open your service in the Render dashboard.
   - Go to Settings -> Advanced -> Root Directory (or simply the service's "Root Directory" field).
   - If you previously entered `src/app.py` (or `app.py`), clear it or set it to the folder that contains `app.py`.
     - If `app.py` is in the repository root, set Root Directory to blank (empty) or `.`
     - If you want the service root to be a subfolder (for example `src/`) set it to `src` (not to a file path).
   - Save and trigger a new deploy.

2) Alternative: keep Render Root = `src` — move the file into a `src/` package and update the Procfile

   If you prefer to set the Root Directory to `src`, then make `src` a directory and place the Flask app module there. Example changes (do in your repo):

   - Move `app.py` into `src/app.py` and create `src/__init__.py` (can be empty).
   - Update `Procfile` to reference the module path, for example:

     web: gunicorn src.app:app

   - In Render settings, set Root Directory = `src` (no file name, only the directory). Deploy.

3) Verify Procfile and requirements

   - `Procfile` (at repo root) should contain one line like:

     web: gunicorn app:app

     or, if you move to `src/`:

     web: gunicorn src.app:app

   - `requirements.txt` must list dependencies (Flask, gunicorn, requests). Your repo already contains them.

Local testing (PowerShell on Windows)

  # create and activate a venv (PowerShell)
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt

  # run the app locally
  $env:PORT=5000; python app.py

Or run with gunicorn (if you have it installed):

  gunicorn app:app --bind 0.0.0.0:5000

If you moved the module into `src/`, change the commands to use `src.app:app`.

Extra notes

- The error you saw is not caused by Flask code — it's a deployment configuration issue.
- If you can't edit Render settings, you can add a small `render.yaml` or change repo layout (option #2 above). The simplest and safest fix is to set the Root Directory to the folder (or blank) in the Render dashboard.

If you'd like, I can:

- Update the repo to include `src/__init__.py` and move `app.py` into `src/` and update the `Procfile` for you (I can make that commit here). This is useful if you intend to set Root Directory to `src` on Render.
- Or provide step-by-step screenshots/text for changing the Render setting.

Tell me which option you want me to apply and I'll make the repo edits (or guide you through updating Render settings).
