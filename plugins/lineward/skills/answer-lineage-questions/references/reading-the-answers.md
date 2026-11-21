# Reading Lineward's answers

- `lineward lineage <model> <column>` prints one arrow path per route, `→` downstream and `←`
  upstream. A column computed from several columns branches into one path per column; a path that
  ends in `<source>.<table>.<column>` has reached the raw data. Without a column it prints one line
  per model reached, with that model's direct parents (or children) side by side.
- `lineward blast-radius <model> <column>` lists every downstream model with its file, and how it
  reads the column, however many models away. `amount`→`payment_amount`: it reads the column
  straight from the model you named and calls it `payment_amount`. `int_payments.amount`→`amount_bucket`:
  it reads what the column became in `int_payments`, a model between, and derives `amount_bucket`
  from it. `amount` in a WHERE and a GROUP BY: it reads it outside its select list, in the clauses
  named (a JOIN, a WHERE, a HAVING, a QUALIFY, a GROUP BY, an ORDER BY, a FLATTEN). Each of these models reads the
  column, and a drop breaks it. A column named only inside a Jinja expression the analysis leaves in place
  (`{{ some_macro('amount') }}`) is not seen. Without a column, `lineward blast-radius <model>` does the same for
  every column of your model.
- An exposure — a dashboard, a notebook or an application its YAML declares — is listed as
  `exposure:<name>` with its YAML file and line; it has no column, so its line reads `downstream`
  alone. The other commands take it by that name too (`lineward context exposure:<name>`).
- A model, seed or snapshot of an installed package (under `dbt_packages/`) is named
  `<package>/<name>` in every answer, the search's included; every command takes it by that name,
  or by its name alone when no other node bears it.
- `lineward search` matches names only, never descriptions: one word of a name, as a substring
  (`email` finds `customer_email`; `e-mail address` finds nothing). It ranks exact, then prefix,
  then substring matches, and lists only the columns a YAML file documents, besides a seed's, which
  its CSV header names.
