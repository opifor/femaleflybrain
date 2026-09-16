"""Independent small-graph oracles for the anatomical path map."""
import itertools
import os

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from flybench.experiment.vpoen_inputs import Map, m4, m5, overlap, B1, sha, PROTOCOL, PROTOCOL_HASH


@pytest.fixture
def graph():
    # Two sources, same-type relay cells with different signs, an unnamed
    # relay, two target cells, an isolated cell; cycles and self-edges included.
    edges = [(0,2,8), (1,2,5), (0,3,8), (1,4,3), (2,3,6),
             (2,5,7), (3,5,7), (4,5,9), (3,6,4), (5,2,10),
             (2,2,99), (5,5,13), (0,5,2), (6,5,1), (2,0,4)]
    a = csr_matrix(([w for _,_,w in edges], ([u for u,_,_ in edges], [v for _,v,_ in edges])), shape=(8,8), dtype=np.int32)
    signs = np.array([1,0,-1,1,-1,1,1,0], dtype=np.int8)
    return dict(indptr=a.indptr, indices=a.indices, count=a.data,
                data=np.repeat(signs, np.diff(a.indptr))*a.data, sign=signs,
                body_id=np.arange(100,108,dtype=np.int64),
                type=np.array(['JO-A','JO-B','relay','relay','','vpoEN','vpoEN','isolated']),
                nt=np.array(['acetylcholine','unknown','gaba','acetylcholine','gaba','acetylcholine','acetylcholine','']))


def oracle(g, sources, targets, depth):
    # Brute-force vertex permutations deliberately avoid reverse CSR traversal.
    a = csr_matrix((g['count'], g['indices'], g['indptr']), shape=(8,8)).toarray()
    found = []
    for p in itertools.permutations(range(8), depth+1):
        if p[0] in sources and p[-1] in targets:
            weights = [int(a[u,v]) for u,v in zip(p,p[1:])]
            if all(weights):
                found.append((p, min(weights)))
    return found


def test_protocol_seal():
    assert sha(PROTOCOL) == PROTOCOL_HASH


def test_direct_orientation_unique_cells_signs_and_self(graph):
    result, cells, edges = Map(graph).direct([5,6])
    assert result['total_synapses'] == 43
    assert result['self_synapses'] == 13
    rel = next(r for r in result['types'] if r['type']=='relay')
    assert rel['synapses'] == 18
    assert rel['cells'] == 2  # shared source to two targets is one cell
    assert rel['sign_synapses'] == {'-':7, '+':11}
    assert rel['share'] == 18/43
    assert sum(r['synapses'] for r in cells) == 43
    assert (5,5,13) in edges


@pytest.mark.parametrize('depth', [1,2,3])
def test_paths_against_independent_permutation_oracle(graph, depth):
    rows, covered = Map(graph).source_paths([0,1], [5,6], depth)
    expected = oracle(graph, {0,1}, {5,6}, depth)
    r = rows[-1]
    assert r['paths'] == len(expected)
    assert r['flow'] == sum(w for _,w in expected)
    assert r['maximum'] == max(w for _,w in expected)
    best = max(expected, key=lambda pw: (pw[1], tuple(graph['body_id'][list(pw[0])])) )
    assert r['best']['body_ids'] == graph['body_id'][list(best[0])].tolist()
    assert r['best']['signs'] == ''.join({-1:'-',0:'0',1:'+'}[int(graph['sign'][u])] for u in best[0][:-1])
    expected_signs = {}
    for p,w in expected:
        signs = ''.join({-1:'-',0:'0',1:'+'}[int(graph['sign'][u])] for u in p[:-1])
        expected_signs[signs] = expected_signs.get(signs,0)+w
    assert r['sign_flow'] == expected_signs
    expected_edges = {p[-2:] for d in range(1,depth+1) for p,w in oracle(graph,{0,1},{5,6},d)}
    assert set(covered) == expected_edges


def test_m2_e3_maximum_tie_and_simple_paths(graph):
    rows, origins = Map(graph).m2([5,6])
    expected = oracle(graph, set(range(8)), {5,6}, 2)
    assert sum(r['paths'] for r in rows) == len(expected)
    assert sum(r['flow'] for r in rows) == sum(w for p,w in expected)
    for row in rows:
        subset = [(p,w) for p,w in expected if (graph['type'][p[1]] or 'unnamed')==row['type']]
        p,w = max(subset, key=lambda pw:(pw[1],pw[0]))
        assert row['maximum'] == w
        assert row['best']['body_ids'] == graph['body_id'][list(p)].tolist()
    assert sum(r['flow'] for r in origins.values()) == sum(w for p,w in expected)


def test_coverage_deduplicates_and_zero_sources(graph):
    rows, covered = Map(graph).source_paths([0,1], [5,6], 3)
    assert sum(covered.values()) == 30  # self input excluded; repeated final edges counted once
    assert rows[-1]['cumulative_covered_synapses'] == 30
    empty, cov = Map(graph).source_paths([], [5,6])
    assert cov == {}
    assert [(r['paths'],r['flow'],r['maximum'],r['best']) for r in empty] == [(0,0,0,None)]*3
    result, cells, edges = Map(graph).direct([])
    assert result['total_synapses']==0 and cells==[] and edges==[]


def test_b1_restricted_paths(graph):
    mapping = Map(graph)
    one,_,_ = mapping.direct([5,6])
    _,origins = mapping.m2([5,6])
    selected = {B1[0]:np.array([2]), B1[1]:np.array([7])}
    rows = m4(mapping,selected,np.array([5,6]),one,origins,np.array([0,1]))
    assert rows[0]['direct_synapses']==7
    assert rows[0]['direct_share']==7/43
    assert rows[0]['two_edge']['maximum']==6
    assert rows[0]['jo_middle']['maximum']==7
    assert rows[1]['direct_synapses']==0 and rows[1]['two_edge']['best'] is None


def test_m5_same_cell_two_directions_against_oracle(graph):
    mapping=Map(graph)
    _,origins=mapping.m2([5,6])
    rows,cells=m5(mapping,np.array([0,1]),np.array([5,6]),origins)
    expected={}
    for c in (2,3,4,7):
        ins=[x for d in (1,2) for x in oracle(graph,{0,1},{c},d)]
        outs=[x for d in (1,2) for x in oracle(graph,{c},{5,6},d)]
        if ins and outs:
            expected[c]=(sum(w for _,w in ins),sum(w for _,w in outs))
    assert {r['index']:(r['incoming']['flow'],r['outgoing']['flow']) for r in cells}==expected
    assert sum(r['paired_score'] for r in rows)==sum(min(a,b) for a,b in expected.values())
    assert rows[0]['type']=='relay'
    assert rows[0]['cells']==2


def test_overlap_unnamed_not_homology_and_limit():
    a=[{'type':n} for n in ['unnamed','A','B','C']]
    b=[{'type':n} for n in ['B','unnamed','C','D']]
    r=overlap(a,b,2)
    assert r['shared']==['B'] and r['intersection']==1 and r['union']==3
    assert r['jaccard']==1/3 and r['unnamed_banc']==[{'type':'unnamed'}]


def test_m5_does_not_join_different_cells_of_same_type(graph):
    g = dict(graph)
    # Cell 2 has JO input but no target output. Cell 7 shares its type and
    # has target output but no JO input. Their type must not become eligible.
    a = csr_matrix(([8,9], ([0,7], [2,5])), shape=(8,8), dtype=np.int32)
    g.update(indptr=a.indptr, indices=a.indices, count=a.data)
    g['type'] = graph['type'].copy()
    g['type'][7] = 'relay'
    mapping = Map(g)
    _, origins = mapping.m2([5])
    rows, cells = m5(mapping, np.array([0]), np.array([5]), origins)
    assert rows == [] and cells == []


def test_harness_failure_probe():
    enabled = os.environ.get('VPOEN_INPUTS_FAIL_PROBE') == '1'
    assert not enabled, 'deliberate harness failure'


def test_witness_sign_string_is_forward_order():
    # Chain 0 -> 1 -> 2 with presynaptic signs (+, -): the witness string must
    # read "+-" in path order, so a reversal or a target-sign leak is caught.
    edges = [(0,1,5), (1,2,7)]
    a = csr_matrix(([w for _,_,w in edges], ([u for u,_,_ in edges], [v for _,v,_ in edges])), shape=(3,3), dtype=np.int32)
    signs = np.array([1,-1,1], dtype=np.int8)
    g = dict(indptr=a.indptr, indices=a.indices, count=a.data,
             data=np.repeat(signs, np.diff(a.indptr))*a.data, sign=signs,
             body_id=np.arange(200,203,dtype=np.int64),
             type=np.array(['JO-A','relay','vpoEN']),
             nt=np.array(['acetylcholine','gaba','acetylcholine']))
    rows, _ = Map(g).source_paths([0], [2], 2)
    assert rows[-1]['best']['signs'] == '+-'
    assert rows[-1]['sign_flow'] == {'+-': 5}
