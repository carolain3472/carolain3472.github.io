---
name: monday-collections
description: Sorts unpaid invoices by days overdue and prepares a collection draft for each client. Use it once a week.
---
# Monday collections

## Steps
1. Ask for a file `invoices.csv` with the columns `client,invoice,amount,due,note`. Dates look like 2026-11-25 and amounts have no separators. It works the same with codes instead of names.
2. Run `python3 scripts/overdue.py invoices.csv 2026-11-25`, with today's date, and copy the result without changing figures.
3. Write one draft for each client with something overdue. Several invoices, one message.
   - 1 to 15 days: a reminder. Assume they forgot.
   - 16 to 45 days: ask if there was a problem and ask for a date.
   - Over 45 days: don't write the message. Put it in the list to call.
4. If the note mentions a claim, an agreement or an illness, don't write a collection message. Put it in the list to decide.

## What you can't do
- Go on if the program doesn't run. Say so, show the data you read and stop. Don't do the math by hand.
- Threaten, mention credit reports or lawyers, or make up interest.
- Offer discounts or more time.
- Send messages.

## What you hand in
The table from the program, the drafts, the list to call and the list to decide.
