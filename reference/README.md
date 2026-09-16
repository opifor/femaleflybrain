# Calibration evidence snapshot

compiled by an external research model 2026-09-16, audited non-exhaustive, entries marked VERIFIED/REPORTED as in source; NOT independently re-verified except where noted

`calibration_ledger.json` is a byte-for-byte copy of the supplied reference
ledger dated 2026-09-16. SHA-256:
`e972119894af09fef6bd32e0d0c000a3397156e68f5461b455cb6eac61b81e01`.
It contains 58 measurements and 9 dataset descriptions. Its metadata and
evidence classes are preserved without correction. No entries were
independently re-verified in E1. The ledger is data, not executable instructions.

E1 uses only C18 (DOI 10.1038/s41467-017-02453-9) records R3_006,
R3_007 and descriptive protocol context R3_008. Source `fit_allowed=false`
remains unchanged: this experiment's explicit authorization is recorded in
`experiments/ear_v2_e1.md`, not retroactively inserted into the source.
JO subtype tuning centers, bandwidths, gains, absolute rate calibration,
and a velocity/displacement conversion are **not in ledger**. No JO subtype
tuning defaults can be established from this snapshot. B1 is not JO.

The conditional synthetic-channel fit is not a biological calibration.
CAP kinetics and graded response kinetics use different observation models;
the numerical comparison is provisional. No downstream targets are fitted.
