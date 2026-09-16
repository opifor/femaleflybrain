# male_decides_v1

Rates are Hz per neuron. Ignition is a measured-window fraction. Network totals are retained in JSON.

## Calibration

| Condition | P1 | LC10a | pIP10 | Network | Ignition |
| --- | ---: | ---: | ---: | ---: | ---: |
| zero | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| A30 | 0.0706522 +/- 0.00924 | 0 +/- 0 | 4.625 +/- 0.283 | 5.36114 +/- 0.00334 | 0 +/- 0 |
| A60 | 0.0625 +/- 0.0058 | 0 +/- 0 | 5.6875 +/- 0.411 | 5.37909 +/- 0.00567 | 0 +/- 0 |
| A120 | 0.0461957 +/- 0.0115 | 0 +/- 0 | 6.4375 +/- 0.427 | 5.50929 +/- 0.00631 | 0 +/- 0 |
| A240 | 0.0951087 +/- 0.0101 | 0 +/- 0 | 7.875 +/- 0.477 | 5.69111 +/- 0.00412 | 0 +/- 0 |
| A480 | 0.236413 +/- 0.0091 | 0 +/- 0 | 9.875 +/- 0.306 | 5.96841 +/- 0.00365 | 0 +/- 0 |
| A960 | 0.372283 +/- 0.0128 | 0 +/- 0 | 9.9375 +/- 0.315 | 6.40248 +/- 0.00264 | 0 +/- 0 |
| B30 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0.435511 +/- 0.000836 | 0 +/- 0 |
| B60 | 0.0434783 +/- 0.0158 | 0 +/- 0 | 4.5 +/- 0.617 | 5.72118 +/- 0.477 | 0 +/- 0 |
| B120 | 0.0543478 +/- 0.014 | 0 +/- 0 | 4.375 +/- 1.02 | 5.94502 +/- 0.747 | 0 +/- 0 |
| B240 | 0.0516304 +/- 0.0131 | 0 +/- 0 | 5.625 +/- 1.25 | 8.30747 +/- 0.745 | 0 +/- 0 |
| C0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| C30 | 30 +/- 0.287 | 0 +/- 0 | 10.5 +/- 0.5 | 0.412774 +/- 0.0239 | 0 +/- 0 |
| C60 | 60.212 +/- 0.259 | 0 +/- 0 | 17 +/- 0.888 | 0.571905 +/- 0.0178 | 0 +/- 0 |
| C120 | 121.549 +/- 0.575 | 0 +/- 0 | 26.5 +/- 0.96 | 0.705586 +/- 0.0125 | 0 +/- 0 |

Elapsed: 144.362 seconds.

## Test

| Condition | P1 | LC10a | pIP10 | Network | Ignition |
| --- | ---: | ---: | ---: | ---: | ---: |
| zero | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| A | 0.0652174 +/- 0.00694 | 0 +/- 0 | 5.25 +/- 0.254 | 5.36199 +/- 0.00331 | 0 +/- 0 |
| C | 30.4253 +/- 0.193 | 0 +/- 0 | 9.84375 +/- 0.665 | 0.846817 +/- 0.289 | 0 +/- 0 |

Elapsed: 39.470 seconds.

```json
{
  "verdicts": {
    "M1": {
      "mean": 0.06521739130434782,
      "se": 0.006942025800635925,
      "n": 20,
      "verdict": "supported"
    },
    "M2": {
      "verdict": "unassessed"
    },
    "M3": {
      "mean": 9.84375,
      "se": 0.664654824840842,
      "n": 20,
      "verdict": "supported"
    }
  },
  "M4": {
    "verdict": "descriptive",
    "smell_ignition_threshold": null,
    "ignition": {
      "zero": {
        "mean": 0.0,
        "se": 0.0,
        "n": 20
      },
      "A": {
        "mean": 0.0,
        "se": 0.0,
        "n": 20
      },
      "C": {
        "mean": 0.0,
        "se": 0.0,
        "n": 20
      }
    },
    "combined_P1_contrast": null
  }
}
```

## Frozen choices

```json
{
  "created_utc": "2026-09-16T14:12:12.690654+00:00",
  "protocol_sha256": "0a636f0494f36a46b96dc568ad176735f3fbf88407f6eaf11f1aae69e10d8c73",
  "calibration_sha256": "1c5baac168009b73b7a8542014400f85bca99f5e2edb115ae320c2de5000b9b4",
  "choices": {
    "A": {
      "dose": 30,
      "fallback": false,
      "metric": "P1"
    },
    "B": {
      "dose": null,
      "fallback": false,
      "metric": "LC10a",
      "reason": "No qualifying calibration dose"
    },
    "C": {
      "dose": 30,
      "fallback": false,
      "metric": "pIP10"
    }
  },
  "smell_ignition_threshold": null
}
```

SE uses independent seeds, with windows averaged within seed. Calibration is separate from held-out inference.
Right-side L1/L2 drive is CHOSEN. Or47b is a glomerular proxy. Direct-target type summaries are in JSON; fewer than 20 types may exist.
Clean room: only this repository was inspected. The supplied dependency import path was used without inspecting adjacent project sources.
No world, behavior, mating outcome or biological ignition threshold is inferred. GPU numerical reproducibility is not claimed bitwise.

## Execution checks and limitations

Quick completed in 38.5 seconds after correcting an initial Result-field interface error; no kernel or protocol change was made.
Native-chain pytest: 6 passed, 1 skipped, exit 0. Deliberate failure probe: 1 failed, 6 deselected, exit 1.
Vision had no qualifying calibration dose. M2, held-out vision direction, and combined selected-dose M4 are unassessed; no fallback vision dose was invented.
Preexisting records occupied 13,027,298 bytes before this experiment. The 10 MB limit is applied to newly added experiment summaries; existing records are preserved.
Network total_spikes in each seed summary is the mean count per 50 ms measured window; multiply by 16 for the measured-period total.
The backend resets refractoriness for its fixed Poisson target union, including zero-rate targets. All conditions share this input convention.

### Calibration vision direction

| Dose | DNa02 R minus L (Hz/neuron, mean +/- SE) |
| --- | ---: |
| 30 | 0 +/- 0 |
| 60 | -1.375 +/- 1.02825 |
| 120 | -2.25 +/- 1.67498 |
| 240 | -0.625 +/- 0.426956 |

### Direct-target type firing

Only one type exists in each specified direct target population: ORN_VA1v, L1 and L2. These are not postsynaptic-partner rankings.

| Stage / condition | ORN_VA1v | Right L1 | Right L2 |
| --- | ---: | ---: | ---: |
| calibration / zero | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| calibration / A30 | 29.6769 +/- 0.154 | 0 +/- 0 | 0 +/- 0 |
| calibration / A60 | 59.4019 +/- 0.212 | 0 +/- 0 | 0 +/- 0 |
| calibration / A120 | 120.347 +/- 0.295 | 0 +/- 0 | 0 +/- 0 |
| calibration / A240 | 248.333 +/- 0.444 | 0 +/- 0 | 0 +/- 0 |
| calibration / A480 | 492.181 +/- 0.706 | 0 +/- 0 | 0 +/- 0 |
| calibration / A960 | 967.862 +/- 0.935 | 0 +/- 0 | 0 +/- 0 |
| calibration / B30 | 0 +/- 0 | 29.9431 +/- 0.0705 | 30.0823 +/- 0.0805 |
| calibration / B60 | 0 +/- 0 | 59.9304 +/- 0.103 | 60.1432 +/- 0.0945 |
| calibration / B120 | 0 +/- 0 | 120.004 +/- 0.153 | 120.119 +/- 0.136 |
| calibration / B240 | 0 +/- 0 | 239.784 +/- 0.178 | 240.246 +/- 0.165 |
| calibration / C0 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| calibration / C30 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| calibration / C60 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| calibration / C120 | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| test / zero | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
| test / A | 30.0471 +/- 0.0965 | 0 +/- 0 | 0 +/- 0 |
| test / C | 0 +/- 0 | 0 +/- 0 | 0 +/- 0 |
