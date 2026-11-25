---
name: quote-by-rule
description: Prepares a quote with the price list and the discount rule of the business. Use it when an order arrives and a total has to be calculated.
---
# Quote by rule

Prices and rules are in `rules.json`. Change them for the ones of your business before you use this skill.

## Steps
1. Read the order. Write down each product and its quantity as they appear.
2. Look for each product in `rules.json`. If the name is not clear, a quantity is missing or the product is not there, stop and ask. Don't replace it with a similar one.
3. Calculate with the program. Don't do the math yourself.
   `echo '{"items": [["River Coffee 500 g", 12]]}' | python3 scripts/quote.py`
   Run the command from the folder of this skill.
4. Copy the lines the program returns, without changing any figure.
5. Write a short message for the client with those figures.

## What you can't do
- Go on if the program doesn't run. Say so, show the data you read and stop. Don't do the math by hand.
- Give a discount that doesn't come from the program. If the client asks for it, or someone says they always get it, write: "That is decided by" and the person in `who_approves_exceptions`.
- Promise a delivery date. It is not in the rules.
- Send the message. It is a draft.

## What you hand in
The lines of the calculation, the draft, and a list of what a person has to decide. If there is nothing to decide, say so.
