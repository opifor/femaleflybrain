"""Synthetic coordinate and CSR oracles for the anatomical holdout."""
import os

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from flybench.experiment.retinotopy_holdout import (
    gate, hex_distance, make_folds, metrics, permute_coordinates,
    predict, prepare_neighbors, rank_surrogate, weighted_median,
)


def test_hex_grid_cube_oracle():
    grid = np.array([(p, q) for p in range(-3, 4) for q in range(-3, 4)
                     if max(abs(p), abs(q), abs(p + q)) <= 3])
    for point in grid:
        delta = grid - point
        expected = np.max(np.abs(np.column_stack((delta, -delta.sum(axis=1)))), axis=1)
        np.testing.assert_array_equal(hex_distance(grid, point), expected)
    assert hex_distance([2, -2], [0, 0]) == 2
    assert hex_distance([2, 2], [0, 0]) == 4


def test_weight_and_lower_tie():
    assert weighted_median([9, 1, 5], [1, 8, 1]) == 1
    assert weighted_median([9, 1], [1, 1]) == 1
    assert weighted_median([9, 1], [3, 2]) == 9
    assert weighted_median([9, 1], [2**32, 2**32 + 1]) == 1


@pytest.mark.parametrize("values,weights", [([], []), ([1], [0]), ([1], [-1]), ([1, 2], [1])])
def test_invalid_weights(values, weights):
    with pytest.raises(ValueError):
        weighted_median(values, weights)


def test_direction_exclusions_weights_and_cross_counts():
    # Cell 0: outgoing donor 1, incoming donor 2, held-out 3, cross-side 4.
    rows = [0, 2, 0, 0, 0, 0, 1, 5]
    cols = [1, 0, 3, 4, 0, 5, 0, 0]
    weights = [3, 9, 1000, 2000, 3000, 0, 1, -4]
    matrix = csr_matrix((weights, (rows, cols)), shape=(6, 6))
    coords = np.array([[99, 99], [1, -1], [4, 2], [80, 80], [70, 70], [60, 60]])
    hemis = np.array(["left"] * 4 + ["right", "left"])
    folds = np.array([0, 1, 2, 0, 1, 1])
    eligible, cross = prepare_neighbors(matrix, hemis, folds)
    np.testing.assert_array_equal(predict(eligible["outgoing"], coords, [0]), [[1, -1]])
    np.testing.assert_array_equal(predict(eligible["incoming"], coords, [0]), [[4, 2]])
    np.testing.assert_array_equal(predict(eligible["both"], coords, [0]), [[4, 2]])
    assert eligible["both"][0, 1] == 4  # Reciprocal weights summed.
    assert cross["outgoing"]["all_edge_incidences"][0] == 1
    assert cross["both"]["training_synapses"][0] == 2000
    changed = coords.copy()
    changed[[0, 3, 4]] = [-800, 700]
    np.testing.assert_array_equal(predict(eligible["both"], changed, [0]), [[4, 2]])
    assert np.isnan(predict(eligible["both"], coords, [5])).all()


def test_cross_side_same_fold_not_training():
    matrices, counts = prepare_neighbors(csr_matrix([[0, 7], [2, 0]]),
                                        np.array(["left", "right"]), np.array([0, 0]))
    assert matrices["both"].nnz == 0
    assert counts["both"]["all_edge_incidences"].tolist() == [2, 2]
    assert counts["both"]["all_synapses"].tolist() == [9, 9]
    assert counts["both"]["training_synapses"].tolist() == [0, 0]


def test_unpredictable_denominator_and_extended_summaries():
    m = metrics([0, 1, 3, np.inf])
    assert (m["n"], m["predictable"], m["unpredictable"]) == (4, 3, 1)
    assert m["le2_fraction"] == .5
    assert m["median_d"] == 2
    assert m["mean_d"] is None and m["mean_nonfinite"]
    assert m["finite_mean_d"] == 4 / 3
    assert metrics([np.inf])["median_d"] is None
    assert metrics([])["le2_fraction"] is None
    with pytest.raises(ValueError):
        metrics([np.nan])


def test_folds_exact_partition_seed_and_balance():
    actual = make_folds(103)
    expected = np.empty(103, dtype=int)
    for k, chunk in enumerate(np.array_split(np.random.default_rng(3801).permutation(103), 5)):
        expected[chunk] = k
    np.testing.assert_array_equal(actual, expected)
    assert np.bincount(actual).tolist() == [21, 21, 21, 20, 20]
    assert not np.array_equal(actual, make_folds(103, 3802))


def test_paired_hemisphere_permutation():
    coords = np.array([(k, 100 + k) for k in range(30)])
    sides = np.array(["left"] * 15 + ["right"] * 15)
    rng = np.random.default_rng(3802)
    first = permute_coordinates(coords, sides, rng)
    second = permute_coordinates(coords, sides, rng)
    for side in set(sides):
        assert set(map(tuple, first[sides == side])) == set(map(tuple, coords[sides == side]))
    assert not np.array_equal(first, coords)
    assert not np.array_equal(first, second)
    np.testing.assert_array_equal(first, permute_coordinates(coords, sides, np.random.default_rng(3802)))


def test_local_hex_graph_recovers_heldout_and_rejects_scramble():
    grid = np.array([(p, q) for p in range(-2, 3) for q in range(-2, 3)
                     if max(abs(p), abs(q), abs(p + q)) <= 2])
    # Five cells per hex, one per fold; all neighbors in the same column.
    coordinates = np.repeat(grid, 5, axis=0)
    column = np.repeat(np.arange(len(grid)), 5)
    matrix = csr_matrix((column[:, None] == column[None, :]).astype(int))
    folds = np.tile(np.arange(5), len(grid))
    sides = np.full(len(coordinates), "left")
    eligible, _ = prepare_neighbors(matrix, sides, folds)
    targets = np.arange(len(coordinates))
    pred = predict(eligible["both"], coordinates, targets)
    np.testing.assert_array_equal(pred, coordinates)
    scrambled = permute_coordinates(coordinates, sides, np.random.default_rng(3802))
    bad = predict(eligible["both"], scrambled, targets)
    assert np.median(hex_distance(bad, scrambled)) > 0


def test_gate_exact_boundaries_and_quick():
    real = metrics([0, 2, 3, 3])
    controls = [metrics([4, 4])] * 5
    assert gate(real, controls) == "map wiring-consistent"
    assert gate(real, controls, quick=True) == "quick only; not evaluated"
    assert gate(real, [real] * 5) == "not shown"
    assert gate(metrics([0, 3, 3]), controls) == "not shown"
    assert gate(metrics([np.inf]), controls) == "not shown"
    assert gate(real, controls[:4]) == "not shown"
    assert gate(real, [metrics([np.inf])] * 5) == "not shown"


def test_rank_surrogate_exact_ids_and_groups():
    ids = np.array([2**60 + 3, 2**60 + 1, 2**60 + 2, 2**60 + 4], dtype=np.int64)
    rank = rank_surrogate(ids, np.array(["L1", "L1", "L1", "Mi1"]),
                          np.array(["left"] * 4), np.array([[-3, 1], [3, 1], [0, 2], [0, 0]]))
    np.testing.assert_array_equal(rank, [[3, 0], [-3, 0], [0, 0], [0, 0]])


def test_harness_failure_probe():
    requested = os.environ.get("RETINOTOPY_HOLDOUT_FAIL_PROBE")
    assert requested != "1", "intentional harness failure"
