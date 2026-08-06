# Presentation notes

Talking points for the live demo, matched to the current 11-page app
(`app/Home.py` and `app/pages/*.py`). Every member should be able to
deliver this flow, not just the page they own.

## Flow (~8–10 minutes)

1. **Home** — open with the policy framing: Kenya's own national survey
   already tells us where children are worst off; this project turns that
   into a ranked, actionable list. State the three headline metrics
   (stunting 21.7%, full immunisation 50.3%, skilled birth attendance
   88.8%) before clicking anywhere.
2. **Problem Statement** — one line on the two objectives (regional/wealth
   indicators, then intervention targeting) and the SDG mapping, then move
   on — this page is reference material, not the demo's centerpiece.
3. **Regional Analysis** — show the funnel chart (sample → estimate) first
   to establish the survey-weighting methodology is real, not a raw count.
   Then the county map and the interactive bar chart. Name the highest and
   lowest county out loud — concrete numbers land better than "it varies
   by region."
4. **Wealth Analysis** — the forest plot of concentration indices is the
   single strongest chart in the app: skilled birth attendance's +0.66 is
   the largest wealth gap found, larger than stunting's or immunisation's,
   and it runs the opposite direction from stunting. Say that contrast out
   loud.
5. **Spatial & Bayesian Analysis** — the small-area-estimation stretch
   goal, fully delivered: observed prevalence, model diagnostics, and
   predicted-probability surfaces for all three indicators. Good page to
   mention MBG/INLA by name if a technical judge is in the room, otherwise
   skip the model equations and go straight to the predicted maps.
6. **Intervention Prioritization** — this is the page that answers "so
   what." Show the threshold rule in one sentence, then the flagged county
   list (v1, stunting-based). Point out the confidence-interval column
   before anyone asks about estimate reliability, then show the v2
   multi-indicator ranking as corroboration.
7. **Policy Recommendations** — close on the recommendation bullets. End
   here, not on a chart — the last thing judges see should be the
   argument, not another visualization.

Skip in a time-constrained demo (mention they exist, don't click through):
**Data**, **Methodology**, **Downloads**, **About** — reference/appendix
pages for anyone who wants to dig into provenance or reproduce the pipeline
after the fact.

## Anticipated judge questions

- **"Why national + 1 SD as the threshold, not top-N or top-quartile?"** —
  it's threshold-based on actual variation rather than an arbitrary count,
  and the app says so directly; `quarto/intervention_analysis.qmd` shows
  how the flagged list would change under alternatives.
- **"Is this causal?"** — no, and the app says so directly on the Policy
  Recommendations page. This is a prioritization signal from prevalence
  data, not a study of why stunting is higher in a given county.
- **"How does wealth inequality compare across the three indicators?"** —
  point straight to the Wealth Analysis forest plot: stunting concentrates
  among the poor, immunisation and SBA both concentrate among the wealthy,
  with SBA's gap by far the largest.
- **"What's the county-level confidence like?"** — the CI-width column on
  Intervention Prioritization exists exactly for this; a county with a
  wide interval rests on fewer sampled clusters and shouldn't be read with
  the same confidence as a narrow one, even at the same point estimate.

## What not to do

- Don't over-explain the survey design math live — one sentence
  ("survey-weighted, accounts for KDHS's cluster sampling") is enough; the
  full explanation lives in the Methodology page for anyone who wants it.
- Don't read out every caption on a slide — the charts are built to be
  self-explanatory; narrate the finding, not the chart mechanics.
