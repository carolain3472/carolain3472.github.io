---
name: invoice-against-order
description: Compares a supplier's invoice with the order and shows the differences in product, quantity and price. Use it before paying.
---
# Invoice against order

## Steps
1. Write the order as `order.csv` and the invoice as `invoice.csv`, with the columns `product,quantity,price`. The price is per unit, without thousands separators.
2. Use the same name in both files only when you are sure it is the same product. If the names don't match and you doubt, keep them different and write the doubt down.
3. Show both tables to the person, so they can check the reading.
4. Run `python3 scripts/compare.py order.csv invoice.csv` and copy the result. Don't compare from memory.
5. Write a short draft for the supplier that mentions only the differences from the program.

## What you can't do
- Go on if the program doesn't run. Say so, show the data you read and stop. Don't do the math by hand.
- Say "you can pay". Say what matches and what doesn't. A person decides about paying.
- Guess a figure that can't be read. Write "can't be read" and stop.
- Include taxes, freight or discounts that are not in both documents. List them apart.

## What you hand in
The two tables, the result of the program, the doubts and the draft.
