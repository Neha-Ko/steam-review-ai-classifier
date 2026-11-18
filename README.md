# Do Players Notice the AI, or Just the Quality?

**Authors:** Neha Kollikara and Tomas Aguilar  
**Course:** INFO 4340 – Analytics and AI, University of Denver  
**Term:** Fall 2026

## Overview

Among buyers who leave negative reviews of AI-disclosed Steam games, how often is generative AI the stated reason, compared with game quality? This matters because criticism of a game that uses generative AI does not necessarily mean the AI itself caused the dissatisfaction. We use Anthropic's Claude Sonnet 4.6 to classify reviews by the reasons reviewers state, validate the AI labels against human judgments and a keyword baseline, and compare complaint rates between AI-disclosed and control games.

## Key findings

- **Quality dominates:** Among negative reviews of AI-disclosed games, an average of **88.0 per 100** mention quality and **11.4 per 100** mention generative AI (AI rate 95% bootstrap CI: **4.8–19.2**). Categories can overlap when a review mentions both.
- **AI complaints are concentrated:** Three games account for **83 of 127** AI complaints in the disclosed group. The disclosed-versus-control difference is **10.2 AI complaints per 100** (95% CI **3.5–18.1**), but is below the project's pre-established minimum detectable difference of **11.5**, so the study does not claim a group-wide difference under its decision rule.
- **Claude outperforms keywords:** On the hand-labeled test set, Claude's precision for identifying AI complaints is **0.934**, versus **0.593** for the keyword baseline. On a fresh, 100-review holdout, Claude's precision is **0.975** (39/40 flags).
- **Human labeling is still necessary:** Recall is less certain because relatively few randomly selected unflagged reviews were hand-checked. The workflow therefore includes review of AI flags and a random audit.
- **Cost:** Classifying **2,638 reviews** with Claude cost approximately **$4.87**, or **$1.84 per 1,000 reviews**, excluding human review. The estimated governed workflow costs **$70.98 per 1,000** when required human checks are included.

## Data

- **Source:** Public Steam user reviews collected through the project's Steam review scraper; games were selected and grouped using the project's game-selection data and AI-disclosure status.
- **Review window:** January 1, 2024–December 31, 2025; scraped November 4, 2026. A separate 2026 holdout was used only for classifier validation.
- **Size:** **6,612** original raw reviews, plus **100** reviews from replacement games, cleaned and sampled to **2,638 negative English-language reviews** from **30 games** (**15 AI-disclosed**, **15 controls**; **1,197** disclosed-group reviews and **1,441** control reviews).
- **Unit of observation:** One negative Steam user review. Main analyses summarize review-level complaint labels into game-level rates.
- **Access:** The notebook expects files under `data/`, including `data/games_final.csv`, `data/reviews/reviews_clean.csv`, pilot files, human labels, and saved Claude outputs. If these files are not included in the repository, obtain them from the project authors; the original scraping workflow uses `steam_reviews_scraper.py`.

## Workflow

1. **Pilot:** Examine 312 negative reviews, hand-check keyword matches, and define labeling distinctions such as generative AI versus enemy/NPC AI.
2. **Cleaning:** Validate review dates and language, remove pilot reviews and excluded games, and sample up to 100 negative reviews per game using random seed **42**.
3. **Keyword baseline:** Apply a fixed regex keyword pattern to flag possible AI complaints.
4. **Human labeling:** Assign and reconcile labels using the project labeling guide; assess inter-rater agreement.
5. **AI classification:** Run **`claude-sonnet-4-6`** using an XML-structured prompt containing labeling guide **v4**, requesting JSON with reason, confidence, evidence, and language fields. Categories are `GENAI`, `QUALITY`, `BOTH`, `OTHER`, and `SKIP`. The notebook does **not** explicitly set temperature. Prompt caching and parallel requests were used.
6. **Evaluation:** Compare Claude with hand labels and keywords using precision, recall, F1, confusion matrices, agreement, a fresh holdout, back-tests, and API cost analysis.
7. **Analysis and recommendation:** Compare AI and quality complaint rates per 100 negative reviews using game-level bootstrap confidence intervals and sensitivity checks. Interpret findings conservatively, retain human review for AI flags, and revalidate the model before reuse.

## Repo contents

The notebook references the following project files and folders. **Verify which ones are actually committed to your GitHub repository before publishing this list.**

```text
README.md                         Project overview and reproduction guide
steam_review_ai_classifier.ipynb  Main analysis notebook (rename uploaded notebook if desired)
steam_reviews_scraper.py           Steam review collection script
data/games_final.csv               Final list of 30 games and groups
 data/pilot/                      Pilot reviews and hand checks
 data/reviews/                    Raw and cleaned reviews; keyword flags
 data/labels/                     Human labels and agreement files
 data/claude/                     Saved Claude prompt and predictions
 data/game_selection/             Game selection documentation
LABELING_GUIDE.md                  Classification rules used by humans and Claude
```

Other scripts, outputs, and figures should be listed here if they are committed.

## How to run it

1. Clone or download the repository and open its root folder in VS Code.
2. Install Python dependencies:

   ```bash
   python -m pip install pandas numpy anthropic matplotlib scipy scikit-learn python-dotenv openpyxl jupyter
   ```

3. Ensure the referenced `data/` files and `LABELING_GUIDE.md` exist in the expected relative paths. Open `steam_review_ai_classifier.ipynb` and run cells in order from the repository root.
4. **Default / no API key:** The notebook is designed to read saved classifications from `data/claude/` when `ANTHROPIC_API_KEY` is not configured. The saved output files must be present.
5. **Optional API rerun:** Create a local `.env` file containing `ANTHROPIC_API_KEY=your_key_here` to enable Anthropic API access. **Never commit `.env` or API credentials.** The notebook's API execution cells should be reviewed before enabling a new run, since calls may incur charges and change results.
6. Inspect notebook tables, charts, evaluation metrics, and conclusions. Re-running the scraper is not necessary for the saved-data analysis; the original pilot scraping command is commented out.

## Limitations

- **Not causal or representative of all buyers:** Only people who posted negative reviews are observed. AI-disclosure status is self-reported, and the groups may differ in other ways.
- **Small game sample:** Only 15 games per group; a few games drive most AI complaints. The observed group difference is below the study's minimum detectable difference.
- **Labeling uncertainty:** Parts of the labeling guide were refined during test labeling, and most test labels came from one person. A fresh holdout provides a separate precision check, but recall remains uncertain.
- **Language and sampling:** Non-English reviews were excluded, and some games were subject to scraping caps or sampling restrictions.
- **Model reproducibility:** Results reflect Claude Sonnet 4.6 in November 2026. Temperature was not set explicitly, and later model runs may differ. Human oversight and revalidation are required before applying this workflow to new data.

## AI use

We used Claude Sonnet 4.6 as the review-classification step in the research workflow, with a labeling guide, structured outputs, and human validation. AI assistance was also used in developing see both of our AI use log.
