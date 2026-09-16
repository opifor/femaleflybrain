"""Synthetic world acceptance and deliberate harness failure probe."""
import json
import math
import os
from dataclasses import fields
import numpy as np
import pytest
from scipy.sparse import csr_matrix
from flybench import eye, scent, motor
from flybench.world import Arena, Body, Observation
from flybench.world import constants as C
from flybench.world.loop import Brain, Loop


def graph():
    types = ["ORN_VA1v", "ppk23", "L1", "L1", "L2", "L2", "JO-A", "JO-B",
             "DNa02", "DNa02", "DNa01", "MDN", "DNp09", "pIP10", "ps1 MN",
             "i1 MN", "pC1_1a", "LC10a", "vpoDN", "pC1a"]
    n = len(types)
    weights = np.zeros((n, n))
    weights[0, [8, 10, 13, 14, 16, 17]] = 500
    weights[6, [18, 19]] = 500
    csr = csr_matrix(weights)
    return {"body_id": np.arange(n), "type": np.array(types),
            "side": np.array(["L", "L", "L", "R", "L", "R", "L", "R", "R", "L"] + ["L"]*10),
            "superclass": np.array(["vnc_motor" if i in (14, 15) else "cb_intrinsic" for i in range(n)]),
            "class": np.array([""]*n), "nt": np.array(["acetylcholine"]*n),
            "data": csr.data, "indices": csr.indices, "indptr": csr.indptr}


def make_loop():
    return Loop(Brain(graph(), "male", seed=3, device="cpu"),
                Brain(graph(), "female", seed=4, device="cpu"), seed=7)


def test_observable_interface():
    arena = Arena()
    assert {f.name for f in fields(Observation)} == {"distance", "bearing", "other_speed", "contact", "sound"}
    assert set(Arena.__slots__) == {"bodies", "sound", "size"}
    for obj in (arena, arena.observe(0), *arena.bodies):
        for name in ("neurons", "state", "virgin", "mated", "accept", "brain", "rates", "__dict__"):
            with pytest.raises(AttributeError):
                getattr(obj, name)
            with pytest.raises((AttributeError, TypeError)):
                setattr(obj, name, True)


def test_geometry_and_boundary():
    arena = Arena(8)
    assert arena.bodies == Arena(8).bodies
    assert arena.observe(0).distance == pytest.approx(6)
    assert abs(arena.observe(0).bearing) <= math.pi/6
    arena.bodies = (Body(1, 1, 0), Body(4, 5, 0, 3))
    obs = arena.observe(0)
    assert obs.distance == 5 and obs.bearing == pytest.approx(math.atan2(4, 3))
    assert obs.other_speed == 3 and not obs.contact
    arena.bodies = (Body(39.9, 1, 0), Body(39, 1, 0))
    assert arena.observe(0).contact
    arena.advance([motor.Command(0, 10), motor.Command(0, 0)], [])
    assert arena.bodies[0] == Body(40, 1, 0, 0)


def test_eye_contralateral_and_deterministic():
    brain = Brain(graph(), "male", device="cpu")
    retina = brain.retina
    assert retina == eye.columns(graph(), brain.groups)
    obs = Observation(1, -math.radians(75), 0, True, ())
    drive = eye.rates(obs, retina)
    assert drive[2] == C.EYE_MAX_HZ and drive[4] == C.EYE_MAX_HZ
    assert drive[3] == drive[5] == 0
    assert all(v == 0 for v in eye.rates(Observation(1, math.pi, 0, True, ()), retina).values())
    assert all(v == 0 for v in eye.rates(obs, retina, contrast=-1).values())
    assert all(v == 0 for v in eye.rates(Observation(1, 0, 0, True, ()), [eye.Column(0, 0, math.pi)]).values())


def test_scent():
    assert scent.falloff(0) == 1
    assert scent.falloff(5) == 0.5
    assert scent.falloff(10) == 0.2
    assert scent.rates(Observation(2, 0, 0, True, ()))["ppk23"] == C.CONTACT_MAX_HZ
    assert scent.rates(Observation(3, 0, 0, False, ()))["ppk23"] == 0
    with pytest.raises(ValueError):
        scent.falloff(-1)


def test_motor_direction_and_stop():
    cmd = motor.command({"DNa02_R": 450, "DNa02_L": 0, "DNa01": 450})
    assert cmd.turn == math.pi and cmd.forward == 10
    arena = Arena()
    origin = arena.bodies[0]
    arena.advance([cmd, motor.Command(0, 0)], [])
    assert arena.bodies[0].heading == pytest.approx(math.pi*.05)
    assert arena.bodies[0].y > origin.y
    assert motor.command({"DNa01": 450, "DNp09": 450}).forward == 0
    assert motor.command({"MDN": 450}).forward == -5


def test_closed_loop_ten_windows():
    loop = make_loop()
    states = [b.state for b in loop.brains]
    first = loop.run(5)
    halfway = [b.state.step for b in loop.brains]
    second = loop.run(5)
    assert halfway == [2500, 2500]
    assert [b.state.step for b in loop.brains] == [5000, 5000]
    assert all(b.state is s for b, s in zip(loop.brains, states))
    records = first+second
    assert records == make_loop().run(10)
    assert records[0]["sensory"][1]["delivered_wave_rms"] == 0
    assert any(r["sensory"][1]["delivered_wave_rms"] > 0 for r in records[1:])
    assert any(r["male"]["pIP10"] > 0 for r in records)
    assert records[-1]["bodies"][0]["x"] != records[0]["bodies"][0]["x"]
    for i, record in enumerate(records):
        assert record["time_ms"] == (i+1)*50
        assert set(record["female"]) == {"vpoDN", "pC1"}
        assert set(record["male"]) == {"P1", "pIP10", "LC10a", "DNa02", "DNa02_L", "DNa02_R"}
        assert record["song"]["female_song_hz"] == 0
        assert record["sensory"][0]["delivered_wave_rms"] == 0
        for body in record["bodies"]:
            assert set(body) == {"x", "y", "heading", "speed"}
        if i:
            expected = records[i-1]["song"]["emitted_rms"] * scent.falloff(records[i-1]["observations"][0]["distance"])
            assert record["sensory"][1]["delivered_wave_rms"] == pytest.approx(expected)
    assert loop.metadata["brains"][0]["scent"]["confidence"] == "proxy"
    json.dumps({"metadata": loop.metadata, "records": records}, allow_nan=False)


def test_hidden_state_cannot_change_observation_or_peer_drive():
    loop = make_loop()
    before = loop.arena.observe(0)
    loop.brains[1].state.v.fill_(123)
    assert loop.arena.observe(0) == before
    assert scent.rates(loop.arena.observe(0)) == scent.rates(before)
    assert eye.rates(loop.arena.observe(0), loop.brains[0].retina) == eye.rates(before, loop.brains[0].retina)


def test_per_target_drive_adapter():
    from types import SimpleNamespace
    from flybench.world.loop import _TargetRates
    brain = Brain(graph(), "male", seed=12, device="cpu")
    hz = np.zeros(len(brain.sim.targets))
    hz[0] = 1000 / brain.sim.params.dt
    brain.sim.drive = SimpleNamespace(mode="poisson", rate_hz=_TargetRates(hz))
    result = brain.sim.run(5, state=brain.state)
    np.testing.assert_array_equal(result.requested_hz[brain.sim.targets], hz)
    np.testing.assert_array_equal(result.sampled_drive_hz[brain.sim.targets], hz)
    assert result.delivered_hz[brain.sim.targets[0]] == hz[0]


@pytest.mark.skipif(os.environ.get("FLYBENCH_FAIL_PROBE") != "1", reason="Opt-in harness probe")
def test_harness_failure_probe():
    assert False, "Deliberate failure must return exit 1"
