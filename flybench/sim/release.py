"""Externally computed graded release; no voltage law or random sampling."""
from dataclasses import dataclass, field

import numpy as np
from scipy.sparse import csr_matrix


def zero_source_rows(weights, source_rows):
    """Return an isolated CSR copy and the original outgoing rows."""
    matrix = csr_matrix(weights, dtype=np.float64, copy=True)
    original = matrix[source_rows].copy()
    keep = np.ones(matrix.nnz, dtype=bool)
    for row in source_rows:
        lo, hi = matrix.indptr[row:row + 2]
        matrix.data[lo:hi] = 0
        keep[lo:hi] = False
    prefix = np.concatenate(([0], np.cumsum(keep)))
    zeroed = csr_matrix((matrix.data[keep], matrix.indices[keep],
                         prefix[matrix.indptr]), shape=matrix.shape)
    return zeroed, original


@dataclass
class GradedRelease:
    source_rows: object
    flux: object
    original_rows: object = field(default=None, init=False)
    counts: object = field(default=None, init=False)
    scaled_source_counts: object = field(default=None, init=False)

    def __post_init__(self):
        rows = np.asarray(self.source_rows)
        if rows.ndim != 1 or (rows.size and rows.dtype.kind not in "iu"):
            raise ValueError("source_rows must be integer indices")
        self.source_rows = rows.astype(np.int64, copy=True)
        if np.any(self.source_rows < 0) or len(np.unique(rows)) != len(rows):
            raise ValueError("Invalid or duplicate source rows")
        self.flux = np.array(self.flux, dtype=np.float64, copy=True)
        if (self.flux.ndim != 2 or self.flux.shape[1] != len(rows)
                or not np.isfinite(self.flux).all() or np.any(self.flux < 0)):
            raise ValueError("flux must be finite, nonnegative, and shaped [steps, sources]")

    def bind(self, weights):
        if np.any(self.source_rows >= weights.shape[0]):
            raise ValueError("Source row outside graph")
        bound = GradedRelease(self.source_rows, self.flux)
        matrix, bound.original_rows = zero_source_rows(weights, self.source_rows)
        bound.counts = np.diff(matrix.indptr).copy()
        if np.any(bound.counts[self.source_rows] != 0):
            raise ValueError("Source outgoing rows must be empty")
        return matrix, bound

    def verify_scaled(self, source_indices, values):
        """Check the actual final delivery entries, after synaptic scaling."""
        self.scaled_source_counts = np.array([
            np.count_nonzero(values[source_indices == row]) for row in self.source_rows
        ], dtype=np.int64)
        if np.any(self.scaled_source_counts):
            raise ValueError("Scaled source outgoing entries must be zero")

    def validate_run(self, state, steps):
        if state.step < 0 or state.step + steps > len(self.flux):
            raise ValueError("flux does not cover absolute state.step interval")

    def enqueue(self, state, active, destination, dt, w_syn):
        """Track absolute released mass separately to avoid signed cancellation."""
        if state.release_pending is None:
            state.release_pending = np.zeros((len(state.delay_buffer), active.shape[0]))
            state.dropped_flux = np.zeros(active.shape)
        amount = self.flux[state.step] * dt
        events = np.zeros(active.shape[0])
        mass = np.zeros_like(events)
        for index, value in enumerate(amount):
            lo, hi = self.original_rows.indptr[index:index + 2]
            cols = self.original_rows.indices[lo:hi]
            counts = self.original_rows.data[lo:hi]
            events[cols] += counts * w_syn * value
            mass[cols] += np.abs(counts) * value
        state.release_pending[destination] += mass
        arriving = state.release_pending[state.cursor]
        if active.ndim == 2:
            arriving = arriving[:, None]
        state.dropped_flux += np.where(active, 0.0, arriving)
        state.release_pending[state.cursor] = 0
        return events
