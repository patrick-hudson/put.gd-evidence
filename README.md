# put.gd evidence

Test receipts, screenshots and raw logs behind put.gd releases. The app lives in
[put.gd-desktop](https://github.com/patrick-hudson/put.gd-desktop).

Each record certifies the source identities and workloads written inside it, not
every later commit.

## Layout

- `records/<name>/`: one record. Older imported records may be a single file or
  have an undated name.
- `records/README.md`: the index of all records, by month. A workflow adds a row
  for each new record after it is pushed.
- `tools/check.py`: the record and push rules. `tools/index.py`: the index.
  `tests/`: their unit tests.

## Rules

- Records are add-only. New files may be added to a record; changing, deleting or
  renaming an existing file needs an `Evidence-Amend: <reason>` trailer on every
  commit that does it.
- New record names are `YYYY-MM-DD-slug`: lowercase letters, digits, dots and
  hyphens.
- A new record is a directory with a `README.md` that has a `# ` title and states
  what was tested, on which host and session, and the exact source or build
  identity.
- Never commit credentials, protected login values or private payloads. Forbidden
  file names, symlinks, Python bytecode and files over 50 MiB are refused, and every
  push is scanned with gitleaks.

`python3 tools/check.py record <dir>` checks a candidate directory. CI checks each
push with `tools/check.py push`. A failed check does not revert anything: the push
stays on `main`, the job fails and GitHub notifies the owner.

## Publish

From a put.gd-desktop checkout:

```
python3 tools/maintenance/evidence.py publish <dir>
```

The command validates the record, pushes it to `main` and prints commit-pinned
links.

## Link

Always pin links to a commit, because `main` keeps moving:

```
https://github.com/patrick-hudson/put.gd-evidence/blob/<sha>/records/<name>/...
https://raw.githubusercontent.com/patrick-hudson/put.gd-evidence/<sha>/records/<name>/<file>
```

Use the `raw.githubusercontent.com` form for images.

## Provenance

The first commit imports `docs/evidence` from put.gd-desktop at
`6677938767e732247f9097e0ae5f063cb63140ef`, byte for byte:
`docs/evidence/<name>` there is `records/<name>` here.
