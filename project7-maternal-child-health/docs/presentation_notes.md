# Presentation notes

Talking points for the live demo, matched to `app/Home.py` and its four
pages. Every member should be able to deliver this flow, not just the page
they own.

## Flow (~6–8 minutes)

1. **Home** — open with the policy framing: Kenya's own national survey
   already tells us where children are worst off; this project turns that
   into a ranked, actionable list. State the four headline metrics on
   screen before clicking anywhere.
2. **Regional Analysis** — show the funnel chart (sample → estimate) first
   to establish the survey-weighting methodology is real, not a raw count.
   Then the county map/bar chart. Name the highest and lowest county
   out loud — concrete numbers land better than "it varies by region."
3. **Wealth Analysis** — if data has landed by presentation day, this is
   the second half of the "region and wealth quintile" story — show the
   poorest-vs-richest gap explicitly. If not yet landed, say so plainly
   ("this axis is still in progress — here's the code that's ready to run
   once the data does") rather than skipping the page.
4. **Intervention Prioritization** — this is the page that answers "so
   what." Show the threshold rule in one sentence, then the flagged county
   list. Point out the confidence-interval column before anyone asks about
   estimate reliability.
5. **Policy Recommendations** — close on the three recommendation bullets.
   End here, not on a chart — the last thing judges see should be the
   argument, not another visualization.

## Anticipated judge questions

- **"Why national + 1 SD as the threshold, not top-N or top-quartile?"** —
  it's threshold-based on actual variation rather than an arbitrary count,
  and it's transparent about being a v1 choice; `quarto/intervention_analysis.qmd`
  shows how the flagged list would change under alternatives.
- **"Is this causal?"** — no, and the app says so directly on the Policy
  Recommendations page. This is a prioritization signal from prevalence
  data, not a study of why stunting is higher in a given county.
- **"What's still missing?"** — say it before they ask: wealth-quintile,
  immunisation, and skilled-birth-attendance data. The code is written and
  gated only on restricted-data access, not designed from scratch after the
  fact — that's a stronger answer than pretending the gap doesn't exist.

## What not to do

- Don't apologize for the pending wealth-quintile page — treat it as "here's
  exactly what's left and why," which reads as in-control, not incomplete.
- Don't over-explain the survey design math live — one sentence
  ("survey-weighted, accounts for KDHS's cluster sampling") is enough; the
  full explanation lives in `docs/methodology.md` for anyone who wants it.
