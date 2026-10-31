# Experiment Results

Comparative evaluation of Semgrep (SAST) and OWASP ZAP (DAST) on OWASP crAPI.

- **Target:** OWASP crAPI, commit `b5fc307f3e5f875809b095b771108ef342a33724`
- **Tools:** `semgrep/semgrep:1.141.0`, `zaproxy/zap-stable:2.17.0` (pinned digests)
- **Date:** 2026-10-31
- **Host:** Windows 11, Docker Desktop 4.91.0
- **Timing:** median of 3 clean runs (`reset-crapi` before each)

## Conditions

- **S0** — Semgrep, standard per-language rules
- **S1** — S0 plus the project rule `crapi-controller-path-object-without-request-context`
- **D0** — authenticated OWASP ZAP API scan from the pinned OpenAPI document
- **D1** — D0 plus the two-account BOLA harness

## Detection, precision and false positives

| Condition | Coverage | Precision | True pos. | False pos. | Unverified | Scenarios detected |
|-----------|----------|-----------|-----------|------------|------------|--------------------|
| S0 | 0 / 4 | n/a | 0 | 0 | 96 | — |
| S1 | 1 / 4 | 0.50 | 1 | 1 | 96 | CRAPI-BOLA-VEHICLE-LOCATION |
| D0 | 1 / 8 | 1.00 | 1 | 0 | ~12 | CRAPI-SSRF-CONTACT-MECHANIC |
| D1 | 2 / 8 | 1.00 | 2 | 0 | 0 | CRAPI-BOLA-VEHICLE-LOCATION, CRAPI-BOLA-MECHANIC-REPORT |

- **S1 precision 0.50:** the custom rule produced two findings. `VehicleController.getLocationBOLA`
  is a true positive (confirmed BOLA); `ProfileController.getProfileVideo` is a false positive —
  dynamic testing showed non-owned video IDs return 404, so `ProfileService` scopes by user.
- **D0 false positives:** several ZAP SQL Injection (40018) alerts used arithmetic payloads and are
  left unverified pending per-URL review; they are not counted as confirmed false positives here.

## Combined coverage (RQ4)

| | Scenarios |
|---|---|
| Detected by at least one condition | 3 |
| Detected by both SAST and DAST | CRAPI-BOLA-VEHICLE-LOCATION |
| SAST only | — |
| Dynamic only | CRAPI-SSRF-CONTACT-MECHANIC, CRAPI-BOLA-MECHANIC-REPORT |
| Jaccard overlap (S1 vs dynamic) | 0.33 |

SAST and DAST are complementary: the custom SAST rule and the dynamic tests agree on the
vehicle-location BOLA, while SSRF and the mechanic-report BOLA are found only dynamically.

## Execution time (median of 3 runs)

| Condition | Median (s) | Min (s) | Max (s) |
|-----------|-----------|---------|---------|
| S0 | 142.3 | 141.7 | 164.9 |
| S1 | 149.5 | 138.5 | 155.8 |
| D0 | 425.5 | 408.4 | 438.1 |
| D1 | 14.1 | 13.8 | 14.2 |
| **Total** | **719.8** | 714.4 | 772.7 |

SAST (S0/S1) runs in ~2.5 min per condition; the dynamic API scan (D0) dominates runtime at
~7 min, while the targeted two-account BOLA test (D1) is by far the fastest at ~14 s.

## Key findings

1. **Standard SAST misses BOLA (RQ2).** S0 detects none of the authorization scenarios.
2. **The project-specific SAST rule detects the vehicle-location BOLA (RQ2)** that S0 misses, at the
   cost of one false positive (precision 0.50).
3. **Generic DAST does not detect BOLA either**, but the authenticated scan finds SSRF
   (`contact_mechanic`) that SAST does not.
4. **Only the targeted two-account test (D1) reliably confirms BOLA**, including the mechanic-report
   case, in the shortest time.
5. **SAST and DAST are complementary (RQ4):** together they cover 3 scenarios; neither covers all.

## Reproducibility notes

- The authenticated active scan (D0) mutates the attacker account (e.g. password-reset endpoints),
  so `test@example.com` login can break after a scan. Always `reset-crapi` before an official run,
  and run the BOLA harness before ZAP.
- `CRAPI_VICTIM_REPORT_ID` must be set in `.env` for the Challenge 2 (mechanic report) case.
- Drafts scenarios in `ground_truth/scenarios.json` marked `draft_needs_team_validation` are not yet
  confirmed and should be validated before being used as final denominators.