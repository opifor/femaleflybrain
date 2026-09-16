# Hash basis note

As of 2026-09-17, `.gitattributes` requires LF text. Earlier `core.autocrlf=true` checkouts and appended LF text allowed CRLF and mixed working-tree hashes to differ from committed LF bytes.
At base `ac0fb19`, all 145 tracked text blobs were LF and their checkout bytes were CRLF; renormalization changed zero blobs. Working-tree text was converted to LF without other byte changes.
Historical hashes remain unchanged. This audit compares SHA-256 after CRLF-to-LF replacement and after LF-to-CRLF expansion, without reformatting content.
E1 = `records/ear_v2_e1_audit.json` (round-1 freeze values; no separate freeze file); E1r2/E1r3 = `records/ear_v2_e1r2_freeze.json` / `records/ear_v2_e1r3_freeze.json`.
E2 = `records/ear_v2_e2_freeze.json`; DP = `records/direction_probe_v1_results.json` (freeze provenance; no separate freeze file); TF = `records/two_female_v1_freeze.json`.
Scope: freeze input/provenance fields, including repeated TF population graph hashes; later result-array hashes and duplicate copies in fit/audit records are excluded.

| Record | Hash field(s) | Reproduced basis |
| --- | --- | --- |
| E1 | `preregistration_sha256`, `ledger_sha256` | LF |
| E1r2 | `preregistration_v1_sha256`, `amendment_sha256`, `preregistration_combined_sha256`, `ledger_v1.0_sha256` | LF |
| E1r3 | `round1_sha256`, `round2_sha256`, `historical_round12_sha256`, `round3_sha256`, `ledger_v11_sha256` | LF |
| E1r3 | `round12_sha256`, `ledger_current_sha256`, `original_ear2_sha256`, `original_tests_sha256` | CRLF |
| E1r3 | `combined_sha256` | mixed (pre-commit working tree) |
| E2 | `original_ledger_sha256` | CRLF |
| E2 | `ledger_sha256` | none |
| E2 | `preregistration_sha256` | LF |
| TF | `sha256.experiments/two_female_v1.md`, `sha256.records/female_no_v1_experiment.json` | CRLF |
| TF | `sha256.experiments/female_no_v1.md`, `sha256.flybench/experiment/two_female.py`, `sha256.flybench/experiment/runner.py`, `sha256.flybench/experiment/protocol.py`, `sha256.flybench/experiment/record.py`, `sha256.flybench/experiment/report.py`, `sha256.flybench/song.py`, `sha256.flybench/ear.py`, `sha256.flybench/sim/fast_gpu.py`, `sha256.flybench/sim/params.py`, `sha256.flybench/dictionary/entries.py` | LF |
| TF | `sha256.build/graph_female.npz`, `sha256.build/graph_banc.npz`, `sha256.build/dictionary_female.json`, `sha256.build/dictionary_banc.json`, `populations.female.sha256`, `populations.banc.sha256` | none |
| DP | `protocol_sha256`, `dictionary_sha256.flybench/dictionary/__init__.py`, `dictionary_sha256.flybench/dictionary/api.py`, `dictionary_sha256.flybench/dictionary/build.py`, `dictionary_sha256.flybench/dictionary/entries.py`, `dictionary_sha256.flybench/graph/select.py`, `source_sha256.flybench/experiment/direction_probe.py`, `source_sha256.flybench/sim/release.py`, `source_sha256.flybench/sim/fast_gpu.py`, `source_sha256.flybench/sim/lif.py`, `source_sha256.flybench/sim/params.py` | LF |
| DP | `graph_sha256` | none |
| DP | `resolved_identities_sha256` | CRLF |

Counts are field occurrences, not unique digests: LF = 34, CRLF = 8, mixed (pre-commit working tree) = 1, none = 8.
E1 LF byte ranges are round 1 `[0:8708]`, round 2 `[8708:14200]`, round 3 `[14200:17637]`. The E1r3 combined match requires CRLF expansion of `[0:14200]` followed by the LF round-3 suffix.
Historical text was recovered from full-context `git diff` old sides against `ac0fb19`: ledger v1.0 at `ac0fb19~8`, v1.1 at `ac0fb19~6`, and pre-round-3 code/tests at `ac0fb19~3`. All 27 available first-parent ancestors were checked for these three paths.
E1r3 `ledger_current_sha256` matches CRLF current ledger v1.2; `ledger_v11_sha256` matches LF historical v1.1. E2 `original_ledger_sha256` matches CRLF v1.1.
E2 `ledger_sha256` (`1904fc03...7d64e5e`) matches neither LF nor CRLF for any available committed ledger version; its original byte stream is not recoverable here.
DP `resolved_identities_sha256` was checked by serializing embedded `identities` exactly as the recorded source does: `json.dumps(..., indent=2, allow_nan=False)` plus a trailing newline, then comparing LF and CRLF.
`none` means no reproducible match in available bytes, not proof of corruption. Seven occurrences refer to absent build artifacts (including repeated graph hashes); these could not be rehashed. Binary graph bytes must never undergo newline replacement.

Future text hashes MUST use UTF-8 bytes without BOM, with CRLF and lone CR normalized to LF before SHA-256, and freeze records MUST declare `hash_basis: "lf"`. No JSON reserialization, whitespace stripping, or implicit final-newline addition is part of normalization.
Binary artifacts retain exact-byte hashing and must be identified as binary in the freeze record; the `lf` basis applies to text inputs only. Historical freeze records and reports are retained without hash corrections.
See this note when interpreting older reference-ledger hashes; a historical digest is evidence of its original bytes, not a promise that the current checkout reproduces them.
