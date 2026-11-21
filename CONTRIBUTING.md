# Contributing

This repository is generated from Lineward's private source tree at every release: a change made here, by
an edit or a merged pull request, is overwritten by the next release. Lineward's source code is not here, and it is
not open to contribution.

Everyone taking part in the issues, the Discussions and the pull requests follows the
[code of conduct](CODE_OF_CONDUCT.md).

## Report a problem

Open an issue with one of the forms on <https://github.com/Lineward/lineward/issues/new/choose>,
and fill in what it asks: the version (the output of `lineward --version`), your editor or agent and the platform,
what you did, what you expected and what happened. A question or an idea goes to the repository's Discussions
([`SUPPORT.md`](SUPPORT.md)).

A reproduction is synthetic: a minimal model and its YAML, written for the report, that show the problem. Never paste
your own SQL, schema or data, even renamed.

## What never goes in an issue

Issues and Discussions are public, and they are for the product itself: a bug, a wrong or missing diagnostic, a skill
or a setup page that misleads an agent. Never post in them:

- a licence key, or the value of `LINEWARD_LICENSE_KEY`;
- a payment, an order or an invoice;
- personal data, yours or anyone else's, or a project you are not allowed to share.

A licence key or a payment: write to <sales@lineward.dev>. Your personal data: <privacy@lineward.dev>. A
vulnerability: [`SECURITY.md`](SECURITY.md).

## Pull requests

A pull request on this repository's files, the plugin, its skills, the setup pages and the container recipe, is
welcome as a proposal. It is never merged here: if it is accepted, its change is ported to the source and published
with the next release, and the notes of that release, in [`CHANGES.md`](CHANGES.md), credit its author by their GitHub
name.

A contribution to this repository's files is made under its licence, the Apache License 2.0, as its section 5 says
([`LICENSE`](LICENSE)).
