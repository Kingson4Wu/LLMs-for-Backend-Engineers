# Reviewer-owned tutoring holdouts

Put private holdout case JSON files in this directory only in a reviewer-owned
working copy or protected evaluation store. `*.json` files here are ignored on
purpose and are never loaded by public CI.

Holdouts use the same schema as `../development/`, but their prompts, goldens,
and adjudications must not be published or used as an automatic score. Record
the complete artifact's format, filename, and SHA-256 in each private execution
report so a reviewer can reproduce what the tutor actually read.
