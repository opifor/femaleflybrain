# courtship_v1

Rates are Hz per neuron; distance is mm; RMS is waveform amplitude. Ignition is a window fraction.

## Quick (excluded from verdicts)

| Condition | pIP10 | rms | vpoDN | pC1 | P1 | distance | final_distance | male_ignition | female_ignition |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| virgin_live | 6.5 | 0.00335461 | 35.75 | 24.6 | 0.0217391 | 5.99033 | 5.99033 | 0 | 0 |
| mated_live | 6.25 | 0.00365429 | 0 | 0 | 0.0217391 | 5.98478 | 5.98478 | 0 | 0 |
| virgin_mute | 6.5 | 0 | 35.75 | 24.6 | 0.0326087 | 5.98478 | 5.98478 | 0 | 0 |
| mated_mute | 6.25 | 0 | 0 | 0 | 0.0217391 | 5.98478 | 5.98478 | 0 | 0 |

## Full

| Condition | pIP10 | rms | vpoDN | pC1 | P1 | distance | final_distance | male_ignition | female_ignition |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| virgin_live | 6.81667 | 0.00381922 | 35.5417 | 24.8133 | 0.0456522 | 5.99297 | 5.99377 | 0 | 0 |
| mated_live | 6.44444 | 0.0036123 | 0 | 0 | 0.0519324 | 5.99153 | 5.99224 | 0 | 0 |
| virgin_mute | 6.64722 | 0 | 35.5417 | 24.8133 | 0.0507246 | 5.99321 | 5.99425 | 0 | 0 |
| mated_mute | 6.65556 | 0 | 0 | 0 | 0.0472222 | 5.99026 | 5.99089 | 0 | 0 |

## Paired predictions

```json
{
  "C1": {
    "verdict": "supported",
    "pIP10_positive_seeds": {
      "virgin_live": 10,
      "mated_live": 10
    },
    "audible_seeds": {
      "virgin_live": 10,
      "mated_live": 10
    },
    "rms_contrast": {
      "mean": 0.0038192219882861545,
      "se": 5.3789703680284285e-05,
      "n": 10,
      "differences": [
        0.003627424275282397,
        0.004066296136639434,
        0.003755607874224503,
        0.0037323071270153516,
        0.0037790299021715624,
        0.003641110980798068,
        0.0040885138355941505,
        0.003797560376521657,
        0.003997902935283659,
        0.003706466439330764
      ]
    }
  },
  "C2": {
    "verdict": "supported",
    "contrast": {
      "mean": 35.541666666666664,
      "se": 0.2778780683150073,
      "n": 10,
      "differences": [
        35.05555555555556,
        34.833333333333336,
        35.47222222222222,
        33.833333333333336,
        36.111111111111114,
        36.638888888888886,
        35.111111111111114,
        36.69444444444444,
        36.02777777777778,
        35.638888888888886
      ]
    }
  },
  "C3": {
    "verdict": "descriptive",
    "contrast": {
      "mean": 0.0,
      "se": 0.0,
      "n": 10,
      "differences": [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
      ]
    }
  },
  "C4": {
    "verdict": "descriptive"
  },
  "C5": {
    "verdict": "descriptive"
  }
}
```

## Dictionary and limitations

```json
{
  "male": {
    "counts": {
      "JO-A": 26,
      "JO-B": 75,
      "ORN": 2635,
      "Or*": 0,
      "Or47b": 130,
      "Or67d": 204,
      "Gr32a": 0,
      "ppk23": 0,
      "ppk25": 0,
      "L1": 1776,
      "L2": 1779,
      "R1-R6": 1394,
      "LC10a": 275,
      "LC10b": 95,
      "LC10c": 255,
      "LC10d": 214,
      "AOTU019": 2,
      "AOTU025": 2,
      "P1": 46,
      "pC1a": 0,
      "pC1b": 0,
      "pC1c": 0,
      "pC1d": 0,
      "pC1e": 0,
      "pIP10": 2,
      "vPR6": 8,
      "vMS11": 14,
      "pMP2": 2,
      "dPR1": 2,
      "TN1A": 22,
      "vpoDN": 0,
      "vpoEN": 4,
      "vpoIN": 5,
      "SAG": 0,
      "oviDN": 0,
      "DNp13/pMN1": 2,
      "pCd": 0,
      "aIPg": 56,
      "mAL": 159,
      "vAB3": 0,
      "DNa01": 2,
      "DNa02": 2,
      "DNp09": 2,
      "MDN": 4,
      "DNg100": 2,
      "DNb08": 4,
      "wing_motor": 48,
      "ps1_MN": 2,
      "i1_MN": 2,
      "iii1_MN": 2,
      "b3_MN": 2,
      "PAM": 316,
      "PPL1": 16,
      "serotonin": 48,
      "octopamine": 101,
      "KC": 4064,
      "MBON": 87,
      "APL": 2,
      "ORN_D": 28,
      "ORN_DA1": 204,
      "ORN_DA2": 48,
      "ORN_DA3": 34,
      "ORN_DA4l": 33,
      "ORN_DA4m": 35,
      "ORN_DC1": 32,
      "ORN_DC2": 22,
      "ORN_DC3": 35,
      "ORN_DC4": 23,
      "ORN_DL1": 83,
      "ORN_DL2d": 15,
      "ORN_DL2v": 23,
      "ORN_DL3": 103,
      "ORN_DL4": 62,
      "ORN_DL5": 43,
      "ORN_DM1": 74,
      "ORN_DM2": 54,
      "ORN_DM3": 63,
      "ORN_DM4": 32,
      "ORN_DM5": 35,
      "ORN_DM6": 58,
      "ORN_DP1l": 33,
      "ORN_DP1m": 31,
      "ORN_V": 55,
      "ORN_VA1d": 132,
      "ORN_VA1v": 130,
      "ORN_VA2": 83,
      "ORN_VA3": 30,
      "ORN_VA4": 34,
      "ORN_VA5": 16,
      "ORN_VA6": 63,
      "ORN_VA7l": 29,
      "ORN_VA7m": 24,
      "ORN_VC1": 29,
      "ORN_VC2": 32,
      "ORN_VC3": 34,
      "ORN_VC4": 38,
      "ORN_VC5": 31,
      "ORN_VL1": 82,
      "ORN_VL2a": 98,
      "ORN_VL2p": 45,
      "ORN_VM1": 33,
      "ORN_VM2": 41,
      "ORN_VM3": 43,
      "ORN_VM4": 78,
      "ORN_VM5d": 84,
      "ORN_VM5v": 34,
      "ORN_VM6": 0,
      "ORN_VM6l": 14,
      "ORN_VM6m": 25,
      "ORN_VM6v": 34,
      "ORN_VM7d": 36,
      "ORN_VM7v": 25,
      "pC1": 0,
      "DNa02_L": 1,
      "DNa02_R": 1
    },
    "missing_groups": [
      "Or*",
      "Gr32a",
      "ppk23",
      "ppk25",
      "pC1a",
      "pC1b",
      "pC1c",
      "pC1d",
      "pC1e",
      "vpoDN",
      "SAG",
      "oviDN",
      "pCd",
      "vAB3",
      "ORN_VM6",
      "pC1"
    ]
  },
  "female": {
    "counts": {
      "JO-A": 94,
      "JO-B": 296,
      "ORN": 2278,
      "Or*": 0,
      "Or47b": 94,
      "Or67d": 127,
      "Gr32a": 0,
      "ppk23": 0,
      "ppk25": 0,
      "L1": 1775,
      "L2": 1728,
      "R1-R6": 7938,
      "LC10a": 237,
      "LC10b": 83,
      "LC10c": 203,
      "LC10d": 188,
      "AOTU019": 2,
      "AOTU025": 2,
      "P1": 0,
      "pC1a": 2,
      "pC1b": 2,
      "pC1c": 2,
      "pC1d": 2,
      "pC1e": 2,
      "pIP10": 0,
      "vPR6": 0,
      "vMS11": 0,
      "pMP2": 0,
      "dPR1": 0,
      "TN1A": 0,
      "vpoDN": 2,
      "vpoEN": 4,
      "vpoIN": 0,
      "SAG": 4,
      "oviDN": 6,
      "DNp13/pMN1": 2,
      "pCd": 0,
      "aIPg": 0,
      "mAL": 107,
      "vAB3": 0,
      "DNa01": 2,
      "DNa02": 2,
      "DNp09": 2,
      "MDN": 4,
      "DNg100": 2,
      "DNb08": 4,
      "wing_motor": 0,
      "ps1_MN": 0,
      "i1_MN": 0,
      "iii1_MN": 0,
      "b3_MN": 0,
      "PAM": 307,
      "PPL1": 16,
      "serotonin": 1021,
      "octopamine": 72,
      "KC": 5177,
      "MBON": 89,
      "APL": 2,
      "ORN_D": 31,
      "ORN_DA1": 127,
      "ORN_DA2": 39,
      "ORN_DA3": 30,
      "ORN_DA4l": 40,
      "ORN_DA4m": 40,
      "ORN_DC1": 39,
      "ORN_DC2": 20,
      "ORN_DC3": 33,
      "ORN_DC4": 22,
      "ORN_DL1": 69,
      "ORN_DL2d": 14,
      "ORN_DL2v": 18,
      "ORN_DL3": 79,
      "ORN_DL4": 52,
      "ORN_DL5": 42,
      "ORN_DM1": 68,
      "ORN_DM2": 54,
      "ORN_DM3": 61,
      "ORN_DM4": 40,
      "ORN_DM5": 42,
      "ORN_DM6": 52,
      "ORN_DP1l": 24,
      "ORN_DP1m": 32,
      "ORN_V": 67,
      "ORN_VA1d": 97,
      "ORN_VA1v": 94,
      "ORN_VA2": 67,
      "ORN_VA3": 29,
      "ORN_VA4": 31,
      "ORN_VA5": 12,
      "ORN_VA6": 60,
      "ORN_VA7l": 16,
      "ORN_VA7m": 22,
      "ORN_VC1": 26,
      "ORN_VC2": 29,
      "ORN_VC3": 31,
      "ORN_VC4": 23,
      "ORN_VC5": 25,
      "ORN_VL1": 80,
      "ORN_VL2a": 71,
      "ORN_VL2p": 27,
      "ORN_VM1": 25,
      "ORN_VM2": 37,
      "ORN_VM3": 37,
      "ORN_VM4": 75,
      "ORN_VM5d": 67,
      "ORN_VM5v": 23,
      "ORN_VM6": 0,
      "ORN_VM6l": 21,
      "ORN_VM6m": 33,
      "ORN_VM6v": 26,
      "ORN_VM7d": 33,
      "ORN_VM7v": 26,
      "pC1": 10,
      "DNa02_L": 1,
      "DNa02_R": 1
    },
    "missing_groups": [
      "Or*",
      "Gr32a",
      "ppk23",
      "ppk25",
      "P1",
      "pIP10",
      "vPR6",
      "vMS11",
      "pMP2",
      "dPR1",
      "TN1A",
      "vpoIN",
      "pCd",
      "aIPg",
      "vAB3",
      "wing_motor",
      "ps1_MN",
      "i1_MN",
      "iii1_MN",
      "b3_MN",
      "ORN_VM6"
    ]
  }
}
```

C4 and C5 are descriptive only. Per-seed correlations, final distances, network rates and totals are in the summary JSON. Null correlations mean a constant series.
The existing DNp09 stop gate is retained. Female SAG uses the prior protocol alias union. No kernel or world modules were modified.
The experiment-local adapter supplies distinct rates to seed columns; synthetic CPU tests cover its equivalence to independent runs. Scientific runs use CUDA fast_gpu/shiu.
No mating or acceptance outcome is inferred from neural activity or contact.
Elapsed seconds: quick 215.763; full 2132.287.
Clean room: only this repository was inspected; the supplied dependency import path was used without inspecting its project sources.

Summary evidence: courtship_v1_full.json SHA256 4933b039cfde48c35bfb151f77ca3d5988145df2addff220d7524fde25f7773d
Quick evidence: build/courtship_v1_quick.json SHA256 17393252d628b7812c8ddf5a0628e62a995810346f00261615ecb3ee92566e72

## Delivery verification and deviations

Male P1 and Or47b are the existing dictionary proxies; these labels do not establish genetic-driver identity. The four-cell female SAG alias union is the prior experiment mapping, not the default candidate SpsP dictionary proxy.
The male ppk23 dictionary group has zero cells. Contact Hz is computed and recorded, but no contact target receives that input; no substitute population was introduced.
Recorded contact windows: 0 of 16480. These trials therefore did not exercise a nonzero window-boundary contact input.
The two live conditions and two mute conditions each contain ten paired seeds and 400 windows. The first 40 windows are excluded. No seed or duration reduction was used.
Quick raw records reveal a numerical reproducibility limitation: for seed 0, the mated_live and mated_mute male brains have identical observed input histories through window 30, but recorded total spikes first differ there (47360 versus 47345). Both use the same male seed. The numerical cause has not been isolated; bitwise reproducibility is not claimed for this CUDA execution chain. Small between-condition neural differences should not be attributed solely to treatment.
The prescribed interpreter and dependency environment were used for CUDA scientific runs and native pytest execution. Synthetic wiring tests use CPU by design and are not substituted for real-graph acceptance evidence.
A first invocation of the auxiliary audit by file path could not import the repository package. Running it as a module from the repository root resolved import discovery using the same interpreter and dependency environment; scientific execution was unaffected.
An earlier quick run (217.1 s) and an interrupted full run (at least 314.4 s, last reported at 220 windows of the first condition) were excluded and retained under build only. An unused female-state flag had been passed to both brain runners. The corrected interface configures SAG only on the female reset; each runtime brain call now receives observations only, and male SAG configuration rejects nonzero input. The preregistration and all scientific parameters remained unchanged; quick and full runs were restarted with the corrected source. A transient directory lock during archiving cleared after the stopped process exited.
No graph, dictionary, simulator, world, ear, song or other experiment module was modified. No add, commit or push operation was performed.

Native pytest: {"passed": 45, "skipped": 3}; exit 0.
Intentional failure: {"failed": 1, "deselected": 6}; exit 1.
All 16480 raw windows passed hash, summary-recalculation, cell-mean, network-count, delayed-sound and condition-wiring checks.
Evidence details: build/courtship_v1_checks.json.
Reproducibility diagnostic: build/courtship_v1_reproducibility.json SHA256 c3ef0b6f7846f61f0fa5bc4edf6b249841da24a8074326fa6a9c116e365cbe0f

## Descriptive approach and steering

| Condition | Mean distance (mm) | Final distance (mm) | Mean defined Spearman | Undefined seeds |
| --- | ---: | ---: | ---: | ---: |
| virgin_live | 5.99297 | 5.99377 | undefined | 10 |
| mated_live | 5.99153 | 5.99224 | undefined | 10 |
| virgin_mute | 5.99321 | 5.99425 | -0.0732613 | 9 |
| mated_mute | 5.99026 | 5.99089 | undefined | 10 |
