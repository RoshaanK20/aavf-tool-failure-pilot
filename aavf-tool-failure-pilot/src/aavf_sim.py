"""AAVF controlled pilot: scripted tool-using workflow, NOT an LLM-agent benchmark.
All task specifications and failure draws are shared across policies.
The audit endpoints reveal state/operation status but not hidden injected fault labels.
No network or paid APIs needed. Python 3.9+.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from random import Random
from typing import Optional

POLICIES = ('no_check', 'retry', 'verify_all', 'adaptive')

@dataclass(frozen=True)
class Scenario:
    scenario_id: int
    initial_stock: int
    unit_price: int
    delta: int
    read_stock_fault: str
    read_price_fault: str
    write_fault: str

@dataclass
class Outcome:
    scenario_id: int
    policy: str
    success: int
    state_correct: int
    report_correct: int
    duplicate_write: int
    extra_checks: int
    total_calls: int
    tool_fault_count: int
    write_fault: str
    read_stock_fault: str
    read_price_fault: str

class ToolWorld:
    def __init__(self, scenario: Scenario):
        self.s = scenario
        self.stock = scenario.initial_stock
        self.price = scenario.unit_price
        self.applied_ops: set[str] = set()
        self.calls = 0
        self.checks = 0
        self._read_stock_calls = 0
        self._read_price_calls = 0
        self._write_calls = 0

    def read_stock(self) -> dict:
        self.calls += 1
        self._read_stock_calls += 1
        fault = self.s.read_stock_fault if self._read_stock_calls == 1 else 'none'
        if fault == 'missing': return {'status': 'ok'}
        if fault == 'corrupt': return {'status': 'ok', 'value': self.stock + 2}
        if fault == 'invalid': return {'status': 'ok', 'value': -5}
        return {'status': 'ok', 'value': self.stock}

    def read_price(self) -> dict:
        self.calls += 1
        self._read_price_calls += 1
        fault = self.s.read_price_fault if self._read_price_calls == 1 else 'none'
        if fault == 'missing': return {'status': 'ok'}
        if fault == 'corrupt': return {'status': 'ok', 'value': self.price + 7}
        if fault == 'invalid': return {'status': 'ok', 'value': -1}
        return {'status': 'ok', 'value': self.price}

    def write_stock(self, op_id: str, delta: int) -> dict:
        self.calls += 1
        self._write_calls += 1
        fault = self.s.write_fault if self._write_calls == 1 else 'none'
        if fault == 'error': return {'status': 'error', 'message': 'service unavailable'}
        if fault == 'timeout_pre': return {'status': 'timeout'}
        if fault == 'silent_drop': return {'status': 'ok', 'operation_id': op_id}
        self.stock += delta
        self.applied_ops.add(op_id)
        if fault == 'timeout_post': return {'status': 'timeout'}
        return {'status': 'ok', 'operation_id': op_id}

    def audit_stock(self) -> int:
        self.calls += 1; self.checks += 1
        return self.stock

    def audit_price(self) -> int:
        self.calls += 1; self.checks += 1
        return self.price

    def audit_operation(self, op_id: str) -> bool:
        self.calls += 1; self.checks += 1
        return op_id in self.applied_ops


def valid_value(v: Optional[int]) -> bool:
    return isinstance(v, int) and v >= 0


def execute(s: Scenario, policy: str) -> Outcome:
    assert policy in POLICIES
    w = ToolWorld(s)
    raw_stock = w.read_stock()
    stock = raw_stock.get('value')
    raw_price = w.read_price()
    price = raw_price.get('value')
    invalid_stock = not valid_value(stock)
    invalid_price = not valid_value(price) or price == 0
    # These policies are fixed before test-data generation. 'Adaptive' is a
    # rule-based controller, not a learned risk model.
    if policy == 'retry':
        if invalid_stock: stock = w.read_stock().get('value')
        if invalid_price: price = w.read_price().get('value')
    elif policy == 'verify_all':
        stock = w.audit_stock()
        price = w.audit_price()
    elif policy == 'adaptive':
        if invalid_stock: stock = w.audit_stock()
        if invalid_price: price = w.audit_price()
        # For this pilot, schema-invalid outputs require independent checking.
        # Silent but plausible read errors are intentionally not detected.

    # The agent performs one non-idempotent stock adjustment.
    # Crucially, we only use observable action semantics and tool responses.
    op_id = f'{s.scenario_id}:first'
    reply = w.write_stock(op_id, s.delta)
    if policy == 'retry':
        if reply.get('status') != 'ok':
            w.write_stock(f'{s.scenario_id}:retry', s.delta)
    elif policy == 'verify_all':
        if not w.audit_operation(op_id):
            w.write_stock(f'{s.scenario_id}:recovery', s.delta)
    elif policy == 'adaptive':
        # Ex ante higher-risk transactions (larger quantity adjustment or
        # high-value item) are proactively verified; any explicit uncertainty
        # is also independently checked before a potential retry.
        high_risk = abs(s.delta) >= 3 or (valid_value(price) and price >= 150)
        needs_check = high_risk or reply.get('status') != 'ok'
        if needs_check and not w.audit_operation(op_id):
            w.write_stock(f'{s.scenario_id}:recovery', s.delta)

    expected_stock = s.initial_stock + s.delta
    state_correct = int(w.stock == expected_stock)
    # Report is produced using the observations the simulated decision maker
    # actually received, not evaluator-only authoritative labels.
    report_correct = int(valid_value(stock) and valid_value(price)
                         and stock + s.delta == expected_stock and price == s.unit_price)
    duplicate = int(w.stock < expected_stock)  # all deltas are negative
    faults = sum(x != 'none' for x in (s.read_stock_fault, s.read_price_fault, s.write_fault))
    return Outcome(s.scenario_id, policy, state_correct * report_correct,
                   state_correct, report_correct, duplicate, w.checks, w.calls,
                   faults, s.write_fault, s.read_stock_fault, s.read_price_fault)


def make_scenarios(n: int = 1600, seed: int = 20261110) -> list[Scenario]:
    rng = Random(seed)
    def draw(opts):
        r = rng.random()
        z = 0.0
        for name, prob in opts:
            z += prob
            if r < z: return name
        return opts[-1][0]
    read_faults = [('none', .85), ('corrupt', .07), ('missing', .05), ('invalid', .03)]
    write_faults = [('none', .80), ('error', .05), ('timeout_pre', .05),
                    ('timeout_post', .05), ('silent_drop', .05)]
    sc = []
    for i in range(n):
        sc.append(Scenario(i, rng.randint(15, 100), rng.randint(25, 250),
             -rng.randint(1, 5), draw(read_faults), draw(read_faults), draw(write_faults)))
    return sc


def run(n: int = 1600, seed: int = 20261110) -> tuple[list[Scenario], list[Outcome]]:
    scenarios = make_scenarios(n, seed)
    outcomes = [execute(s, policy) for s in scenarios for policy in POLICIES]
    return scenarios, outcomes

if __name__ == '__main__':
    from collections import defaultdict
    sc, rows = run()
    grouped = defaultdict(list)
    for r in rows: grouped[r.policy].append(r)
    for name in POLICIES:
        r = grouped[name]
        print(name, 'success', round(sum(x.success for x in r)/len(r), 4),
              'calls', round(sum(x.total_calls for x in r)/len(r), 3),
              'checks', round(sum(x.extra_checks for x in r)/len(r), 3),
              'dupes', sum(x.duplicate_write for x in r))
