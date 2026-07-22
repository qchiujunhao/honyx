# Multi-analysis demo — several analyses, one repo, one website

A session that answered more than one question becomes a repo of **independent,
self-contained analysis packages** plus one landing page. Each analysis under
`analyses/<slug>/` reproduces on its own; CI verifies each in a matrix job; the
showcase aggregates every analysis's site into one repo website.

```text
multi-analysis-demo/
├── analyses/
│   ├── group-means/     # "What is the mean value in each group?" (dropped in unchanged)
│   └── pass-rates/      # "What fraction pass (score >= 60) per method?"
├── build_index.py       # builds site/: runs each analysis's build_site.py + a landing page
└── reproduce.yml        # -> .github/workflows/reproduce.yml (matrix over the analyses)
```

Each `analyses/<slug>/` is a complete package (`honyx.json`, `steps/`, `run.sh`,
`results/`, `check.py`, `build_site.py`) — exactly the single-analysis shape,
composed. `group-means` is the standalone `pipeline-demo` copied in with no
changes, showing that an existing package drops into this layout as-is.

## Reproduce every analysis the CI way

```bash
for a in analyses/*/; do
  ( cd "$a" && mv results reference-outputs && bash run.sh \
    && python3 check.py results reference-outputs )
done
```

## Build the combined website

```bash
python3 build_index.py     # -> site/index.html (landing) + site/<slug>/index.html
```

## When to use this vs one package

- **Separate questions** → separate packages here (one per `analyses/<slug>/`).
- **Alternative paths for the same question** → a single package with a comparison
  step, not multiple packages.

CI shows one pass/fail per analysis, so a break is localized to the analysis that
broke, and the landing page only surfaces analyses that are actually present.
