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


## Round 2 ledger extension

The original snapshot description above is historical. Version 1.1 adds
16 REPORTED records R6_001--R6_016 from section 2 of the supplied JO
subtype report. Existing entries and policies are unchanged. The original
had schema_version 1.0 and no ledger_version field; the new field is 1.1.
R6 is an ID namespace; these auditory entries belong to rung 3.
Unknown modality, preparation details, sample sizes, figures and unique
earlier-work DOI assignments remain null or explicitly unextracted.
No primary source was reverified. Functional preferences are calcium
classes, not uniquely identified anatomical subtypes or individual rates.
The round-2 amendment authorizes conditional target placement despite
the preserved fit_allowed=false snapshot policy. See round-2 freeze
and fit records for original/current hashes and limitations.

## E2 ledger 1.2 extension

Version 1.2 appends R3_009--R3_012: WT residual 0.80 +/- 0.06,
shakB2 residual 0.22 +/- 0.04 under nicotinic antagonists, no observed
B1 spikes in 17 cell-attached recordings, and latency/jitter with n=24.
Evidence class is VERIFIED_OPERATOR_FULLTEXT: read by the operator in the
PMC full text, 2026-09-16. Supplied quotations are verbatim; their uncertainty
kind is not independently established. No SD/SEM conversion is made.
Existing entries, including unresolved R3_003 and C18 R3_006--R3_008,
remain unchanged. The original snapshot paragraphs above are historical.
The E2 preregistration authorizes the conditional fit; source-wide metadata
and historical fit policies are preserved. See experiments/ear_v2_e2.md and
records/ear_v2_e2_freeze.json for scope and hashes.
See [Hash basis note](../records/hash_basis_note.md) for historical LF/CRLF hash provenance.
Future text hashes use LF-normalized bytes and freeze records declare `hash_basis: "lf"`.
