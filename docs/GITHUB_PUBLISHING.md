# Publishing to GitHub

This project is **not yet a Git repository**. These are the exact steps to publish it. Nothing here pushes automatically; you run every command yourself.

## 1. Create the GitHub repository (website)

1. Sign in at github.com → **+** (top right) → **New repository**.
2. **Repository name:** `regional-sales-performance-analysis` (matches the folder name).
3. **Description:** paste the short description from [GITHUB_PROFILE_TEXT.md](GITHUB_PROFILE_TEXT.md).
4. **Public**: yes. Recruiters must be able to see it, and the data is synthetic, so nothing is confidential.
5. **Do NOT** tick "Add a README", ".gitignore" or "license". The project already has them, and ticking these creates a conflicting first commit.
6. Click **Create repository** and copy the URL shown (e.g. `https://github.com/<your-username>/regional-sales-performance-analysis.git`).

## 2. Check before the first push

Run from the project folder:

```bash
cd ~/regional-sales-performance-analysis
source .venv/bin/activate
python src/pipeline.py --regenerate      # must finish without errors
python tests/test_pipeline.py            # must print: 10 tests passed
```

Then check:
- [ ] README *Author* section has your name and (optionally) your LinkedIn/GitHub links
- [ ] No `.venv/`, `__pycache__/` or `.ipynb_checkpoints/` will be committed (they're in `.gitignore`; confirm in step 3)
- [ ] No passwords, tokens or personal files in the folder
- [ ] `PROJECT_CHECKLIST.md` honestly reflects what is done (Power BI items unticked until built)

## 3. First commit and push

```bash
git init
git status
```
`git status` lists the files Git sees. **Confirm** that `.venv/` and `__pycache__/` are **not** listed. If they are, `.gitignore` is missing or misnamed.

```bash
git add .
git status
```
Everything to be committed is now listed in green. Expect 77 files (code, notebooks, CSVs, charts, mockups, docs).

```bash
git commit -m "Initial release: regional sales performance analysis"
git branch -M main
git remote add origin <YOUR_REPOSITORY_URL>
git push -u origin main
```
Replace `<YOUR_REPOSITORY_URL>` with the URL from step 1.6. When asked for a password, GitHub requires a **personal access token** (Settings → Developer settings → Personal access tokens) or sign-in through the GitHub CLI (`gh auth login`), not your account password.

*If Git asks who you are:* `git config --global user.name "Your Name"` and `git config --global user.email "<the email on your GitHub account>"`.

## 4. Verify the upload

Open the repository page and check:
- [ ] The README renders, including the Mermaid architecture diagram and the chart images
- [ ] `notebooks/03_eda.ipynb` opens on GitHub and shows its charts and outputs
- [ ] Links in the README work (click 3–4 of them)
- [ ] File count and folder structure match the README tree
- [ ] Optional: on another machine, `git clone` the repo, follow *How to run* in the README, and confirm `10 tests passed`

**Repository polish (Settings / main page):**
- *About* (gear icon) → add the topics listed in [GITHUB_PROFILE_TEXT.md](GITHUB_PROFILE_TEXT.md)
- Pin the repository on your GitHub profile

## 5. Add the Power BI file and screenshots later

After building the dashboard (see [POWER_BI_MASTER_GUIDE.md](../powerbi/POWER_BI_MASTER_GUIDE.md) and [FINAL_VALIDATION.md](../powerbi/FINAL_VALIDATION.md)):

```bash
git add powerbi/Regional_Sales_Dashboard.pbix screenshots/*.png README.md PROJECT_CHECKLIST.md
git status
git commit -m "Add Power BI dashboard and screenshots"
git push
```

Before committing, update the README: add `![Executive Overview](screenshots/01_executive_overview.png)` under *Screenshots*, and change the dashboard status from "specification" to "built". Tick the Power BI items in `PROJECT_CHECKLIST.md`.

## Line endings (Windows users)

`.gitattributes` forces CSV, SQL, Python and Markdown files to use LF line endings. That keeps the CSVs byte-identical on every OS, which matters because MySQL's `LOAD DATA … LINES TERMINATED BY '\n'` would otherwise read a stray `\r` into the last column. No action is needed; just don't delete `.gitattributes`.
