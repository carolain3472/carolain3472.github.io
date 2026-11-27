# A hidden order in an invoice

20 invented invoices checked against their purchase orders by three models, in three versions
(clean, hidden direct order, hidden "commercial agreement") and with two prompts. 360 reviews.

- `experiment.py MODEL` — builds the invoices and runs the reviews → `results_MODEL.json` (full answers)
- `analyze.py` — table and `summary.json`
- `figure.py` — the figure of the note

The hardware store, the suppliers and the invoices are invented. Calls go through `../llm.py`.
