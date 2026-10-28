# Methodology

## Target and unit of analysis

The target is OWASP crAPI at the commit recorded in `.env.example`. A **scenario** is a documented, manually reproducible vulnerability with a security oracle. A **finding** is one normalized alert emitted by a tool or targeted harness.

The upstream crAPI deployment currently references moving image tags. Bootstrap therefore records the exact local Docker image identifiers under `results/raw/`. Preserve those records with each experiment. For the final evaluation, all teammates must use the same recorded image set and must not pull again between repeated runs.

## Detection rule

A finding detects a scenario only when it identifies the affected endpoint or source location and the same underlying security mechanism. Duplicate alerts for one root cause are collapsed during manual classification.

## Labels

- `true_positive`: validated against a ground-truth scenario
- `false_positive`: validated not to represent the claimed vulnerability
- `unverified`: insufficient evidence; excluded from precision
- `informational`: useful observation that does not claim a vulnerability

Human classification is stored in `ground_truth/mappings.json`; generated code never silently turns an unmatched alert into a false positive.

## Metrics

- Scenario coverage: detected eligible scenarios / eligible ground-truth scenarios
- Finding precision: TP / (TP + FP), excluding unverified findings
- False negatives: eligible ground-truth scenarios without a mapped TP
- Union coverage: scenarios detected by at least one condition
- Unique contribution: scenarios detected by only one condition
- Runtime: wall-clock duration recorded by each runner

Counts and denominators accompany every percentage. Timed scans should be repeated at least three times after a warm-up; use the median and range for the final evaluation.

## Variables held fixed

- crAPI commit and database initialization
- Semgrep and ZAP image versions
- selected rule/configuration files
- OpenAPI input
- seeded accounts and BOLA object identifiers
- scan timeout and host hardware for each repeated comparison

## Pilot

The first pilot validates the vehicle-location BOLA case and end-to-end result processing. The main experiment should begin only after all included ground-truth cases are independently reproduced and reviewed.

