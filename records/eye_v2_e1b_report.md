# eye_v2 E1b report

Numerical verdict: **map wiring-consistent**. The full five-fold run scored 45,528 cells across 31 types and 1,581 hemisphere-qualified column keys.

Pooled bidirectional median d = 0; mean d = nonfinite; d<=2 = 45,034/45,528 (0.98915). Every cell is scored once. No network simulation or neuron drive occurred.

## Scope and interpretation

This is consistency, not independent validation. Publication assignments may themselves have been derived from wiring, so holding out coordinates during this prediction does not make the underlying assignment process independent. The result measures agreement between published hex coordinates and local anatomical connectivity; it does not establish optical geometry, visual physiology, or biological map accuracy. This closes E1's explicitly unperformed held-out anatomical prediction within this limited scope. Scope note (added after review): the hold-out is at cell level, not column level; on average about 54% of donor synapse weight comes from cells sharing the target's own (p,q) column, and a stricter column-level hold-out (excluding same-column donors) gives median distance 1 and a within-2-hex share of 92.6%, so the gate verdict stands while the headline numbers are carried largely by same-column neighbours.

The gate distinguishes the observed map from the five specified random controls. It does not logically exclude every possible sequential-ID map. The separate descriptive surrogate provides evidence about the particular rank construction defined in the preregistration.

## Data and denominators

The exact-ID join contains 45,528 matched assignment cells, 31 types and 1,581 columns. Assignment/graph type and side disagreements are zero. The graph has 138,639 cells; its 93,111 unassigned cells are unavailable donors and are outside the assigned-cell target denominator. Five fold sizes: 9106, 9106, 9106, 9105, 9105.

Counts are raw positive synapse counts, regardless of neurotransmitter sign. Incoming and outgoing edges are pooled for the sole gate. Each fold excludes every held-out cell from donors. Lower coordinate-wise weighted medians require no occupied-column projection. Reciprocal edges contribute both counts. Fractions include unpredictable targets as failures; their distance is positive infinity. Nonfinite summaries are null in JSON with explicit flags; finite-only summaries are also retained.

## Bidirectional type metrics and denominators

| Type | Held out | Predictable | Unpredictable | Median d | Mean d | Finite-only mean d | d<=1 fraction | d<=2 fraction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ALL | 45528 | 45435 | 93 | 0 | nonfinite | 0.226587 | 0.956181 | 0.98915 |
| C2 | 1426 | 1426 | 0 | 0 | 0.036466 | 0.036466 | 0.98878 | 0.997896 |
| C3 | 1509 | 1508 | 1 | 0 | nonfinite | 0.006631 | 0.998675 | 0.998675 |
| L1 | 1572 | 1571 | 1 | 0 | nonfinite | 0.003819 | 0.998728 | 0.999364 |
| L2 | 1557 | 1556 | 1 | 0 | nonfinite | 0.010283 | 0.996789 | 0.998073 |
| L3 | 1412 | 1410 | 2 | 0 | nonfinite | 0.022695 | 0.992918 | 0.997167 |
| L4 | 1332 | 1331 | 1 | 1 | nonfinite | 0.707739 | 0.866366 | 0.974474 |
| L5 | 1556 | 1556 | 0 | 0 | 0.007712 | 0.007712 | 0.998072 | 0.999357 |
| Mi1 | 1581 | 1581 | 0 | 0 | 0.008223 | 0.008223 | 0.999367 | 1 |
| Mi4 | 1529 | 1529 | 0 | 0 | 0.008502 | 0.008502 | 0.998038 | 0.999346 |
| Mi9 | 1541 | 1541 | 0 | 0 | 0.014276 | 0.014276 | 0.997404 | 1 |
| R7 | 1253 | 1183 | 70 | 0 | nonfinite | 0.016906 | 0.94174 | 0.943336 |
| R8 | 1276 | 1260 | 16 | 0 | nonfinite | 0.03254 | 0.977273 | 0.98511 |
| T1 | 1389 | 1388 | 1 | 0 | nonfinite | 0.020173 | 0.993521 | 0.99712 |
| T2 | 1450 | 1450 | 0 | 1 | 0.708966 | 0.708966 | 0.904138 | 0.975172 |
| T2a | 1530 | 1530 | 0 | 0 | 0.520915 | 0.520915 | 0.90915 | 0.980392 |
| T3 | 1474 | 1474 | 0 | 0 | 0.350746 | 0.350746 | 0.930801 | 0.984396 |
| T4a | 1441 | 1441 | 0 | 0 | 0.363636 | 0.363636 | 0.918112 | 0.990285 |
| T4b | 1493 | 1493 | 0 | 0 | 0.19357 | 0.19357 | 0.969859 | 0.991962 |
| T4c | 1553 | 1553 | 0 | 0 | 0.397939 | 0.397939 | 0.928525 | 0.987122 |
| T4d | 1498 | 1498 | 0 | 0 | 0.293057 | 0.293057 | 0.949266 | 0.990654 |
| T5a | 1465 | 1465 | 0 | 0 | 0.372014 | 0.372014 | 0.909898 | 0.984983 |
| T5b | 1484 | 1484 | 0 | 0 | 0.298518 | 0.298518 | 0.938005 | 0.986523 |
| T5c | 1472 | 1472 | 0 | 0 | 0.311821 | 0.311821 | 0.949049 | 0.982337 |
| T5d | 1416 | 1416 | 0 | 0 | 0.349576 | 0.349576 | 0.933616 | 0.980226 |
| Tm1 | 1549 | 1549 | 0 | 0 | 0.012912 | 0.012912 | 0.997418 | 0.998709 |
| Tm2 | 1542 | 1542 | 0 | 0 | 0.016213 | 0.016213 | 0.998054 | 0.999351 |
| Tm20 | 1484 | 1484 | 0 | 0 | 0.045148 | 0.045148 | 0.990566 | 0.996631 |
| Tm21 | 1276 | 1276 | 0 | 1 | 0.637147 | 0.637147 | 0.907524 | 0.984326 |
| Tm3 | 1499 | 1499 | 0 | 0 | 0.551034 | 0.551034 | 0.918612 | 0.984656 |
| Tm4 | 1454 | 1454 | 0 | 0 | 0.70564 | 0.70564 | 0.832187 | 0.971114 |
| Tm9 | 1515 | 1515 | 0 | 0 | 0.10363 | 0.10363 | 0.978878 | 0.991419 |

## Incoming-only metrics and denominators

| Type | Held out | Predictable | Unpredictable | Median d | Mean d | Finite-only mean d | d<=1 fraction | d<=2 fraction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ALL | 45528 | 44944 | 584 | 0 | nonfinite | 0.254628 | 0.936654 | 0.977684 |
| C2 | 1426 | 1423 | 3 | 0 | nonfinite | 0.133521 | 0.969846 | 0.991585 |
| C3 | 1509 | 1508 | 1 | 0 | nonfinite | 0.012599 | 0.997349 | 0.998675 |
| L1 | 1572 | 1570 | 2 | 0 | nonfinite | 0.012739 | 0.996183 | 0.998092 |
| L2 | 1557 | 1547 | 10 | 0 | nonfinite | 0.025856 | 0.988439 | 0.991651 |
| L3 | 1412 | 1346 | 66 | 0 | nonfinite | 0.141902 | 0.924221 | 0.9483 |
| L4 | 1332 | 1314 | 18 | 1 | nonfinite | 0.9414 | 0.713213 | 0.953453 |
| L5 | 1556 | 1556 | 0 | 0 | 0.008355 | 0.008355 | 0.998072 | 0.999357 |
| Mi1 | 1581 | 1581 | 0 | 0 | 0.006325 | 0.006325 | 0.998735 | 1 |
| Mi4 | 1529 | 1528 | 1 | 0 | nonfinite | 0.015707 | 0.996076 | 0.998692 |
| Mi9 | 1541 | 1541 | 0 | 0 | 0.015574 | 0.015574 | 0.996755 | 0.999351 |
| R7 | 1253 | 989 | 264 | 0 | nonfinite | 0.033367 | 0.784517 | 0.786911 |
| R8 | 1276 | 1065 | 211 | 0 | nonfinite | 0.051643 | 0.821317 | 0.829154 |
| T1 | 1389 | 1385 | 4 | 0 | nonfinite | 0.020217 | 0.991361 | 0.99496 |
| T2 | 1450 | 1450 | 0 | 1 | 0.707586 | 0.707586 | 0.904828 | 0.975862 |
| T2a | 1530 | 1530 | 0 | 0 | 0.537255 | 0.537255 | 0.905882 | 0.981046 |
| T3 | 1474 | 1474 | 0 | 0 | 0.372456 | 0.372456 | 0.922659 | 0.984396 |
| T4a | 1441 | 1441 | 0 | 0 | 0.401804 | 0.401804 | 0.901457 | 0.991672 |
| T4b | 1493 | 1493 | 0 | 0 | 0.205626 | 0.205626 | 0.96718 | 0.991293 |
| T4c | 1553 | 1553 | 0 | 0 | 0.39472 | 0.39472 | 0.929169 | 0.985834 |
| T4d | 1498 | 1498 | 0 | 0 | 0.293725 | 0.293725 | 0.943925 | 0.990654 |
| T5a | 1465 | 1465 | 0 | 0 | 0.400683 | 0.400683 | 0.908532 | 0.984983 |
| T5b | 1484 | 1484 | 0 | 0 | 0.306604 | 0.306604 | 0.940701 | 0.985849 |
| T5c | 1472 | 1472 | 0 | 0 | 0.325408 | 0.325408 | 0.949049 | 0.982337 |
| T5d | 1416 | 1416 | 0 | 0 | 0.39548 | 0.39548 | 0.923729 | 0.97952 |
| Tm1 | 1549 | 1549 | 0 | 0 | 0.014203 | 0.014203 | 0.996127 | 0.998709 |
| Tm2 | 1542 | 1542 | 0 | 0 | 0.038262 | 0.038262 | 0.992866 | 0.999351 |
| Tm20 | 1484 | 1484 | 0 | 0 | 0.041105 | 0.041105 | 0.991914 | 0.996631 |
| Tm21 | 1276 | 1276 | 0 | 1 | 0.631661 | 0.631661 | 0.904389 | 0.982759 |
| Tm3 | 1499 | 1499 | 0 | 0 | 0.617078 | 0.617078 | 0.894596 | 0.985991 |
| Tm4 | 1454 | 1454 | 0 | 1 | 0.763411 | 0.763411 | 0.821183 | 0.971802 |
| Tm9 | 1515 | 1511 | 4 | 0 | nonfinite | 0.10589 | 0.971617 | 0.988779 |

## Outgoing-only metrics and denominators

| Type | Held out | Predictable | Unpredictable | Median d | Mean d | Finite-only mean d | d<=1 fraction | d<=2 fraction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ALL | 45528 | 45211 | 317 | 0 | nonfinite | 0.401539 | 0.908298 | 0.975817 |
| C2 | 1426 | 1422 | 4 | 0 | nonfinite | 0.030942 | 0.988079 | 0.99439 |
| C3 | 1509 | 1508 | 1 | 0 | nonfinite | 0.007958 | 0.998675 | 0.998675 |
| L1 | 1572 | 1571 | 1 | 0 | nonfinite | 0.003183 | 0.999364 | 0.999364 |
| L2 | 1557 | 1555 | 2 | 0 | nonfinite | 0.017363 | 0.992935 | 0.996789 |
| L3 | 1412 | 1406 | 6 | 0 | nonfinite | 0.023471 | 0.990085 | 0.994334 |
| L4 | 1332 | 1330 | 2 | 1 | nonfinite | 0.709023 | 0.857357 | 0.972973 |
| L5 | 1556 | 1555 | 1 | 0 | nonfinite | 0.014791 | 0.996787 | 0.998715 |
| Mi1 | 1581 | 1581 | 0 | 0 | 0.019608 | 0.019608 | 0.996837 | 1 |
| Mi4 | 1529 | 1529 | 0 | 0 | 0.017659 | 0.017659 | 0.99673 | 0.999346 |
| Mi9 | 1541 | 1541 | 0 | 0 | 0.0305 | 0.0305 | 0.997404 | 0.999351 |
| R7 | 1253 | 1074 | 179 | 0 | nonfinite | 0.034451 | 0.850758 | 0.857143 |
| R8 | 1276 | 1239 | 37 | 0 | nonfinite | 0.03632 | 0.961599 | 0.968652 |
| T1 | 1389 | 1339 | 50 | 0 | nonfinite | 0.064974 | 0.948164 | 0.958963 |
| T2 | 1450 | 1449 | 1 | 1 | nonfinite | 0.929607 | 0.786207 | 0.96 |
| T2a | 1530 | 1524 | 6 | 0 | nonfinite | 0.715879 | 0.834641 | 0.963399 |
| T3 | 1474 | 1471 | 3 | 0 | nonfinite | 0.624065 | 0.850068 | 0.972185 |
| T4a | 1441 | 1441 | 0 | 0 | 0.547536 | 0.547536 | 0.883414 | 0.984733 |
| T4b | 1493 | 1492 | 1 | 0 | nonfinite | 0.488606 | 0.926993 | 0.982585 |
| T4c | 1553 | 1549 | 4 | 1 | nonfinite | 0.825048 | 0.831294 | 0.961365 |
| T4d | 1498 | 1494 | 4 | 1 | nonfinite | 1.01004 | 0.764352 | 0.955274 |
| T5a | 1465 | 1464 | 1 | 1 | nonfinite | 0.85929 | 0.817747 | 0.959727 |
| T5b | 1484 | 1483 | 1 | 1 | nonfinite | 0.7559 | 0.841644 | 0.963612 |
| T5c | 1472 | 1468 | 4 | 1 | nonfinite | 0.908719 | 0.809103 | 0.950408 |
| T5d | 1416 | 1412 | 4 | 1 | nonfinite | 0.896601 | 0.810028 | 0.951977 |
| Tm1 | 1549 | 1549 | 0 | 0 | 0.02776 | 0.02776 | 0.996772 | 0.998709 |
| Tm2 | 1542 | 1542 | 0 | 0 | 0.032425 | 0.032425 | 0.994163 | 0.998703 |
| Tm20 | 1484 | 1482 | 2 | 0 | nonfinite | 0.209852 | 0.965633 | 0.987197 |
| Tm21 | 1276 | 1273 | 3 | 1 | nonfinite | 1.069128 | 0.757837 | 0.945141 |
| Tm3 | 1499 | 1499 | 0 | 0 | 0.574383 | 0.574383 | 0.903936 | 0.984656 |
| Tm4 | 1454 | 1454 | 0 | 1 | 0.841816 | 0.841816 | 0.780605 | 0.969051 |
| Tm9 | 1515 | 1515 | 0 | 0 | 0.2 | 0.2 | 0.968317 | 0.989439 |

## Permutation distribution

Five paired-coordinate shuffles within hemisphere, seed 3802, fixed graph/types/folds. Both references and donor coordinates are shuffled. These five values are a descriptive null distribution, not a significance estimate.

| Replicate | Direction | Predictable | Unpredictable | Median d | Mean d | d<=1 | d<=2 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | both | 45435 | 93 | 13 | nonfinite | 0.008786 | 0.024512 |
| 1 | incoming | 44944 | 584 | 14 | nonfinite | 0.009379 | 0.023985 |
| 1 | outgoing | 45211 | 317 | 14 | nonfinite | 0.00962 | 0.025852 |
| 2 | both | 45435 | 93 | 14 | nonfinite | 0.009071 | 0.024117 |
| 2 | incoming | 44944 | 584 | 14 | nonfinite | 0.008061 | 0.020998 |
| 2 | outgoing | 45211 | 317 | 14 | nonfinite | 0.009049 | 0.024403 |
| 3 | both | 45435 | 93 | 13 | nonfinite | 0.007973 | 0.024578 |
| 3 | incoming | 44944 | 584 | 14 | nonfinite | 0.008237 | 0.024359 |
| 3 | outgoing | 45211 | 317 | 14 | nonfinite | 0.008764 | 0.024688 |
| 4 | both | 45435 | 93 | 14 | nonfinite | 0.009115 | 0.024952 |
| 4 | incoming | 44944 | 584 | 14 | nonfinite | 0.008698 | 0.023634 |
| 4 | outgoing | 45211 | 317 | 14 | nonfinite | 0.008742 | 0.024249 |
| 5 | both | 45435 | 93 | 14 | nonfinite | 0.009247 | 0.025215 |
| 5 | incoming | 44944 | 584 | 14 | nonfinite | 0.008412 | 0.024227 |
| 5 | outgoing | 45211 | 317 | 14 | nonfinite | 0.00894 | 0.025149 |

The sole gate evaluates 0 < 13 and 0.98915 >= 0.5: **map wiring-consistent**.

## Opposite-hemisphere accounting

Counts are assigned-neighbor directional edge incidences, not unique undirected neighbors. All means before fold exclusion; training means after it. Every count below is excluded from prediction. Per-type counts and per-cell arrays are retained in JSON and the raw archive.

| Direction | All incidences | All synapses | Training incidences | Training synapses |
| --- | ---: | ---: | ---: | ---: |
| both | 0 | 0 | 0 | 0 |
| incoming | 0 | 0 | 0 | 0 |
| outgoing | 0 | 0 | 0 | 0 |

## Sequential-ID descriptive surrogate

The legacy eye is not comparable directly: it emits azimuth rather than p,q. No legacy eye code was executed. The preregistered surrogate sorts exact IDs within type and hemisphere, spreads integer p across the hemisphere's published range, and fixes q=0. The table scores held-out prediction against those surrogate assignments. It is descriptive and does not enter the gate.

| Type | Held out | Predictable | Unpredictable | Median d | Mean d | Finite-only mean d | d<=1 fraction | d<=2 fraction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ALL | 45528 | 45435 | 93 | 9 | nonfinite | 10.231011 | 0.083619 | 0.137739 |
| C2 | 1426 | 1426 | 0 | 9 | 10.56101 | 10.56101 | 0.085554 | 0.131837 |
| C3 | 1509 | 1508 | 1 | 9 | nonfinite | 10.099469 | 0.092114 | 0.139165 |
| L1 | 1572 | 1571 | 1 | 10 | nonfinite | 10.994271 | 0.0757 | 0.127226 |
| L2 | 1557 | 1556 | 1 | 9 | nonfinite | 10.74036 | 0.085421 | 0.13359 |
| L3 | 1412 | 1410 | 2 | 10 | nonfinite | 11.087943 | 0.084986 | 0.140227 |
| L4 | 1332 | 1331 | 1 | 9 | nonfinite | 9.800902 | 0.093093 | 0.152402 |
| L5 | 1556 | 1556 | 0 | 9 | 10.354756 | 10.354756 | 0.079692 | 0.12982 |
| Mi1 | 1581 | 1581 | 0 | 9 | 9.867173 | 9.867173 | 0.075269 | 0.132827 |
| Mi4 | 1529 | 1529 | 0 | 9 | 10.52845 | 10.52845 | 0.085677 | 0.141269 |
| Mi9 | 1541 | 1541 | 0 | 9 | 10.227774 | 10.227774 | 0.073329 | 0.131084 |
| R7 | 1253 | 1183 | 70 | 11 | nonfinite | 11.519865 | 0.087789 | 0.144453 |
| R8 | 1276 | 1260 | 16 | 10 | nonfinite | 11.088095 | 0.101097 | 0.147335 |
| T1 | 1389 | 1388 | 1 | 11 | nonfinite | 11.959654 | 0.078474 | 0.136789 |
| T2 | 1450 | 1450 | 0 | 9 | 9.636552 | 9.636552 | 0.077931 | 0.135172 |
| T2a | 1530 | 1530 | 0 | 9 | 10.019608 | 10.019608 | 0.085621 | 0.136601 |
| T3 | 1474 | 1474 | 0 | 9 | 10.059701 | 10.059701 | 0.080054 | 0.126187 |
| T4a | 1441 | 1441 | 0 | 9 | 10.053435 | 10.053435 | 0.078418 | 0.129077 |
| T4b | 1493 | 1493 | 0 | 9 | 10.116544 | 10.116544 | 0.073677 | 0.123242 |
| T4c | 1553 | 1553 | 0 | 9 | 9.864778 | 9.864778 | 0.084997 | 0.146169 |
| T4d | 1498 | 1498 | 0 | 9 | 10.00534 | 10.00534 | 0.083445 | 0.144192 |
| T5a | 1465 | 1465 | 0 | 9 | 9.797952 | 9.797952 | 0.090102 | 0.139249 |
| T5b | 1484 | 1484 | 0 | 10 | 9.915768 | 9.915768 | 0.074798 | 0.137466 |
| T5c | 1472 | 1472 | 0 | 9 | 9.650815 | 9.650815 | 0.09375 | 0.155571 |
| T5d | 1416 | 1416 | 0 | 9 | 9.909605 | 9.909605 | 0.089689 | 0.144068 |
| Tm1 | 1549 | 1549 | 0 | 9 | 10.630084 | 10.630084 | 0.071014 | 0.131698 |
| Tm2 | 1542 | 1542 | 0 | 9 | 10.262646 | 10.262646 | 0.09144 | 0.152399 |
| Tm20 | 1484 | 1484 | 0 | 9 | 10.355121 | 10.355121 | 0.079515 | 0.128032 |
| Tm21 | 1276 | 1276 | 0 | 9 | 9.554075 | 9.554075 | 0.094828 | 0.144984 |
| Tm3 | 1499 | 1499 | 0 | 9 | 9.397598 | 9.397598 | 0.089393 | 0.151434 |
| Tm4 | 1454 | 1454 | 0 | 9 | 9.572215 | 9.572215 | 0.078404 | 0.131362 |
| Tm9 | 1515 | 1515 | 0 | 9 | 9.856106 | 9.856106 | 0.083828 | 0.130693 |

Direct surrogate-to-publication distance (without prediction): {"n": 45528, "predictable": 45528, "unpredictable": 0, "median_d": 15.0, "mean_d": 16.600882973115446, "median_nonfinite": false, "mean_nonfinite": false, "finite_median_d": 15.0, "finite_mean_d": 16.600882973115446, "le1_count": 340, "le2_count": 938, "le1_fraction": 0.007467931822175365, "le2_fraction": 0.02060270602706027}.

## Verification, reproduction and deviations

Targeted pytest: 15 passed in 0.39s, exit 0. Intentional harness probe: 1 failed in 0.49s, exit 1. Both count lines and exits were checked. The synthetic hex-grid/CSR tests cover distance, direction, reciprocal weights, median ties, fold and hemisphere leakage, missing predictions, paired controls and gate boundaries.

Independent raw checks recomputed cube distances and type summaries for all seven cases and three directions, compared every quick prediction with its full-run counterpart, and checked paired permutation inventories. A separate direct traversal of the original full CSR checked 1004 targets (including every directionally unpredictable target), all three directions and real/first-permutation/rank cases, using expanded synapse weights as an independent median oracle.

Quick mode scored 880 fold-zero L1/Mi1/T4a targets and issued no gate verdict. Full-run wall time: 22.628 seconds. Versions: {"python": "3.12.14", "numpy": "2.4.2", "scipy": "1.17.1"}.

The prescribed Windows CPython/dependency chain was used, with LC_ALL=C, LANG=C, bytecode and pytest plugin autoload disabled, and -p no:cacheprovider. No environment fallback was used. From the worktree root in that environment:

```text
<python> build/records-raw/eye_v2_e1b/run_evidence.py
<python> build/records-raw/eye_v2_e1b/finalize.py
```

Raw evidence includes full/quick per-cell coordinates, folds, predictions, distances and cross-side counts; summary JSON includes every type, fold, hemisphere, direction and control. Freeze contains preregistration and compressed input SHA-256 values; hashes were checked before both runs and at finalization. Audit records file hashes, git status, sizes and LF/BOM checks, excluding its own recursive hash.

Clean-room scope: only repository context, the supplied graph/assignment data, and authorized dependency imports were used. No external project or archive source was opened. No git writes, staging, commits, pushes, network activity or protected-module edits occurred. All new deliverables are English UTF-8 without BOM and LF.

- No changes to the frozen method, seeds, metric, or gate. No environment difference.
- Before real-data runs, the evidence wrapper expected 17 test passes but the module contained 15. The fail-closed wrapper stopped on this count mismatch; the expected count was corrected to 15 and the full chain rerun.
- The actual legacy azimuth output is not comparable in p,q. The preregistered rank-to-p surrogate is descriptive only.
- The first finalization attempt stopped before checks because a directly invoked raw script lacked the repository import path. The script now explicitly adds the invoking worktree; the prescribed interpreter and dependency directory are unchanged.

## Frozen preregistration (verbatim)

```text
# eye_v2 E1b preregistration

Decision owner: the operator. Budget: 40 minutes from first inspection.
This document is frozen with SHA-256 before implementation or data evaluation.
Text hashes use LF UTF-8 without BOM; compressed input hashes use exact bytes.
No network simulation, neuron drive, fitting, git writes, or changes to the
existing eye, retinotopy, or world modules are permitted.

## Question and data

Are published column assignments consistent with local graph wiring?
Use read_assignments and join_columns on the supplied FAFB v783 graph and
column_assignment.csv.gz. Expected join: 45,528 cells, 31 assignment types,
1,581 hemisphere-qualified column keys. Fail closed on a mismatch with these
counts or on graph/publication type or side disagreements. No other anatomical
data or external project code is used. The E1 coverage and report are context.
Only strictly positive raw count edges enter; signed data and sign never weight
the prediction. CSR rows are presynaptic and columns postsynaptic.

## Holdout and estimator

Order assigned cells by graph index. NumPy default_rng(3801) permutes this
population once; array_split into five groups defines disjoint folds of sizes
differing by at most one. Each cell is held out exactly once (about 20% per
fold). All cells in the target's fold are unavailable as coordinate donors,
including the target itself and any self-loop. Donors may be any of the 31
assigned types. No held-out coordinates enter the estimator.

For each held-out cell, use assigned, non-held-out, same-hemisphere neighbors.
Predict p and q separately by the count-weighted lower median: the smallest
coordinate whose cumulative weight is at least half the total. No rounding,
nearest-column projection, or fitting follows. The resulting integer pair
need not be an occupied column. Pool incoming and outgoing counts for the
primary prediction; reciprocal edges contribute both counts. Also evaluate
incoming-only and outgoing-only predictions independently.

Count opposite-hemisphere assigned neighbors and their synapses separately,
both before and after the fold exclusion; they never enter prediction.
Directional edge incidences are counted separately, including in pooled totals.
Cells without eligible positive weight are unpredictable and stay in all
fraction denominators. Their distance is positive infinity for the primary
median and mean; also report finite-only median and mean for interpretation.
JSON represents nonfinite summaries as null with an explicit nonfinite flag.

## Metrics and controls

Hex distance is (abs(delta_p)+abs(delta_q)+abs(delta_p+delta_q))/2.
Pool held-out cells across folds, without averaging fold medians. Report count,
predictable/unpredictable, median distance, mean distance, d<=1 and d<=2 counts
and fractions, overall and per assignment type, for all three directions.
Save per-cell folds, predictions, distances, and excluded cross-side counts.

Control: default_rng(3802), five successive independent permutations of paired
(p,q) among assigned cells within each hemisphere (left then right). Types,
IDs, graph, hemisphere, and fold membership remain fixed. In each replicate
both donor coordinates and target reference coordinates use that permuted
assignment; use precisely the same estimator and metric denominators.
Do not permute p and q independently or restrict permutations within type.

The sole numerical gate, on pooled bidirectional full-run values, is:
real median d < minimum of the five permutation median d values AND
real d<=2 fraction >= 0.5. If true report "map wiring-consistent"; otherwise
report "not shown". Undefined comparisons cannot pass. No per-type or
directional threshold is an additional gate; no p-value is inferred from five
permutations. This is consistency, not independent validation: the publication
assignments may themselves have been derived from wiring. Holding out cells
here does not remove possible dependence in how the original map was built.

## Sequential-ID descriptive comparison

The legacy eye produces azimuth, not (p,q), so its actual output is not
comparable in hex distance. Use a declared crude surrogate for all assigned
types: within each type and hemisphere, sort exact body IDs and map rank r
linearly to that hemisphere's published p minimum and maximum, rounding with
floor(x+0.5); q=0. For a singleton use the rounded midpoint. Apply the same
holdouts and estimator to these pseudo-assignments and score against those
pseudo-assignments. Also report direct surrogate-to-publication hex error.
This is not an execution or reproduction of the legacy eye. It has no gate.
The numerical gate alone cannot logically exclude every possible ID mapping.

## Quick mode and evidence

Quick mode scores only fold zero targets of L1, Mi1, T4a, retaining the full
31-type donor population and full fold-zero exclusion. Run all five controls
but never issue the full numerical verdict from quick mode. Full mode scores
five folds and all 31 types. Save quick outputs only in the authorized raw
directory; full results go to the four authorized summary records.

Use the prescribed Windows CPython 3.12 and supplied dependency chain, locale
C, bytecode disabled, pytest plugin autoload disabled and -p no:cacheprovider.
Synthetic hex-grid/CSR tests must detect wrong direction, weights, distance,
held-out leakage, cross-side leakage, ignored unpredictable denominators,
broken folds, broken paired permutation, and incorrect gate boundaries.
An intentional failing pytest probe must produce one failure and exit 1.
Record actual pass/fail counts and exits, source and file hashes, git status,
runtime, software versions, and deviations. Recheck frozen hashes after work.
No alternative environment is acceptance evidence. If the budget prevents
completion, report partial status. Summary records together must be <=5 MB.
Audit excludes its own recursive hash and states that exclusion explicitly.
All deliverables use English, LF and UTF-8 without BOM, with no machine paths.
```
