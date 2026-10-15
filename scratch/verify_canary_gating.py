"""
Empirical verification of Canary Gating and Anti-Flapping in ProviderCircuitBreaker
"""
import sys
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from app.core.model_adapter import ProviderCircuitBreaker, CircuitBreakerState

def test_canary_probe_concurrency():
    cb = ProviderCircuitBreaker(failure_threshold=3, recovery_timeout=0.05, half_open_success_threshold=2)
    cb.trip("groq", Exception("Initial trip"))
    time.sleep(0.06)
    assert cb.get_state("groq") == CircuitBreakerState.HALF_OPEN

    # Launch 20 concurrent threads calling can_execute
    results = []
    def probe(idx):
        return cb.can_execute("groq")

    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = [pool.submit(probe, i) for i in range(20)]
        results = [f.result() for f in futures]

    true_count = sum(1 for r in results if r is True)
    false_count = sum(1 for r in results if r is False)
    print(f"Canary probe concurrency results: True={true_count}, False={false_count}")
    assert true_count == 1, f"Expected exactly 1 probe granted, got {true_count}"
    assert false_count == 19, f"Expected 19 probes denied, got {false_count}"
    print("PASS: Exactly 1 probe allowed in HALF_OPEN, preventing thundering herd.")

def test_anti_flapping_threshold():
    cb = ProviderCircuitBreaker(failure_threshold=3, recovery_timeout=0.05, half_open_success_threshold=2)
    cb.trip("groq", Exception("Initial trip"))
    time.sleep(0.06)
    assert cb.get_state("groq") == CircuitBreakerState.HALF_OPEN

    # 1st probe
    assert cb.can_execute("groq") is True
    # 1st success reported
    cb.record_success("groq")
    # State must still be HALF_OPEN because threshold is 2!
    state_after_1st = cb.get_state("groq")
    print(f"State after 1st success: {state_after_1st}")
    assert state_after_1st == CircuitBreakerState.HALF_OPEN, f"Expected HALF_OPEN, got {state_after_1st}"

    # 2nd probe
    assert cb.can_execute("groq") is True
    # 2nd success reported
    cb.record_success("groq")
    state_after_2nd = cb.get_state("groq")
    print(f"State after 2nd success: {state_after_2nd}")
    assert state_after_2nd == CircuitBreakerState.CLOSED, f"Expected CLOSED, got {state_after_2nd}"
    print("PASS: Anti-flapping requires 2 consecutive successes to close.")

def test_half_open_failure_re_trips_immediately():
    cb = ProviderCircuitBreaker(failure_threshold=3, recovery_timeout=0.05, half_open_success_threshold=2)
    cb.trip("groq", Exception("Initial trip"))
    time.sleep(0.06)
    assert cb.get_state("groq") == CircuitBreakerState.HALF_OPEN

    assert cb.can_execute("groq") is True
    # Probe fails
    cb.record_failure("groq", Exception("Still failing"))
    state = cb.get_state("groq")
    print(f"State after probe failure: {state}")
    assert state == CircuitBreakerState.OPEN, f"Expected OPEN, got {state}"
    print("PASS: Probe failure immediately re-trips to OPEN.")

if __name__ == "__main__":
    test_canary_probe_concurrency()
    test_anti_flapping_threshold()
    test_half_open_failure_re_trips_immediately()
    print("ALL CANARY GATING EMPIRICAL TESTS PASSED!")
