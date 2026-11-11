"""AAVF experimental extension: real-LLM action-selection harness.

This module does not contain experimental LLM results. An LLM backend must be
connected and the experiment run for any real-model performance claim.

AVAILABLE OPERATIONS: model chooses read_stock, read_price, write_stock,
and finish. Verification and recovery happen in an external middleware policy.
Hidden fault labels are NEVER passed to the model or the policy.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import json
import re
from typing import Any, Protocol
try:
    from .aavf_sim import Scenario, ToolWorld, valid_value, POLICIES
except ImportError:
    from aavf_sim import Scenario, ToolWorld, valid_value, POLICIES

SYSTEM_PROMPT = """You are a tool-using agent in a reproducible inventory benchmark.
Your task is to read the current stock and price, decrease stock by the requested
amount exactly once, and report the new stock and original unit price.
You do not know actual values until you call tools. Use tools only when needed.
Respond ONLY with a single JSON object for your next action. Use these formats:
{"tool":"read_stock"}
{"tool":"read_price"}
{"tool":"write_stock", "delta":-2}
{"tool":"finish", "reported_stock":18, "reported_price":75}
You may not call audit tools directly. Never infer stock or price from assumptions.
If tool calls fail or are ambiguous, use the observations available. Do not invent confirmations.
"""

class Backend(Protocol):
    def generate(self, messages: list[dict[str, str]]) -> str: ...

@dataclass
class AgentResult:
    scenario_id: int
    policy: str
    success: int
    final_state_correct: int
    final_report_correct: int
    model_calls: int
    tool_calls: int
    verification_calls: int
    duplicate_write: int
    invalid_actions: int
    completed: int
    trace: list[dict[str, Any]]


def parse_action(text: str) -> dict[str, Any] | None:
    """Accept a direct JSON dictionary or a fenced JSON dictionary."""
    s = text.strip()
    if s.startswith('```'):
        s = re.sub(r'^```(?:json)?\s*', '', s, flags=re.I)
        s = re.sub(r'\s*```$', '', s)
    # Try strict JSON first; then extract the first top-level object.
    try:
        x = json.loads(s)
        return x if isinstance(x, dict) else None
    except (json.JSONDecodeError, ValueError):
        pass
    decoder = json.JSONDecoder()
    for pos, ch in enumerate(s):
        if ch == '{':
            try:
                x, _ = decoder.raw_decode(s[pos:])
                return x if isinstance(x, dict) else None
            except json.JSONDecodeError:
                continue
    return None


class GuardedWorld:
    """Tool middleware; only observed data drives policy checks.

    No hidden Scenario.*_fault fields are used for deciding whether to verify.
    They are used exclusively by ToolWorld to simulate unknown failures.
    """
    def __init__(self, scenario: Scenario, policy: str):
        if policy not in POLICIES:
            raise ValueError(policy)
        self.scenario = scenario
        self.world = ToolWorld(scenario)
        self.policy = policy
        self.read_price_value: int | None = None
        self.write_count = 0
        self.action_count = 0

    def perform(self, action: dict[str, Any]) -> dict[str, Any]:
        tool = action.get('tool')
        if tool == 'read_stock':
            reply = self.world.read_stock()
            value = reply.get('value')
            if self.policy == 'verify_all':
                value = self.world.audit_stock()
            elif self.policy == 'adaptive' and not valid_value(value):
                value = self.world.audit_stock()
            elif self.policy == 'retry' and not valid_value(value):
                value = self.world.read_stock().get('value')
            return {'status':'ok' if valid_value(value) else 'invalid', 'value': value}
        if tool == 'read_price':
            reply = self.world.read_price()
            value = reply.get('value')
            bad = not valid_value(value) or value == 0
            if self.policy == 'verify_all':
                value = self.world.audit_price()
            elif self.policy == 'adaptive' and bad:
                value = self.world.audit_price()
            elif self.policy == 'retry' and bad:
                value = self.world.read_price().get('value')
            if valid_value(value):
                self.read_price_value = value
            return {'status':'ok' if valid_value(value) else 'invalid', 'value':value}
        if tool == 'write_stock':
            delta = action.get('delta')
            if type(delta) is not int or delta >= 0 or delta < -10:
                return {'status':'invalid', 'error':'delta must be a negative integer between -10 and -1'}
            self.write_count += 1
            op_id = f'{self.scenario.scenario_id}:llm:{self.write_count}'
            reply = self.world.write_stock(op_id, delta)
            if self.policy == 'retry' and reply.get('status') != 'ok':
                reply = self.world.write_stock(f'{op_id}:retry',delta)
            elif self.policy in ('verify_all', 'adaptive'):
                high_risk = abs(delta) >= 3 or (self.read_price_value is not None and self.read_price_value >= 150)
                should_check = self.policy == 'verify_all' or high_risk or reply.get('status') != 'ok'
                if should_check:
                    applied = self.world.audit_operation(op_id)
                    if not applied:
                        reply = self.world.write_stock(f'{op_id}:recovery',delta)
                    else:
                        reply = {'status':'ok', 'operation_id':op_id, 'verified':True}
            return reply
        return {'status':'invalid', 'error':'unknown tool name'}


def run_agent(backend: Backend, scenario: Scenario, policy: str, max_steps: int = 8) -> AgentResult:
    guard = GuardedWorld(scenario,policy)
    history = [
        {'role':'system','content':SYSTEM_PROMPT},
        {'role':'user','content':f'Inventory task #{scenario.scenario_id}: decrement stock by {abs(scenario.delta)} units exactly once. Read stock and price with tools, then finish with the new stock and price.'},
    ]
    completed = 0
    reported_stock = None
    reported_price = None
    bad_actions = 0
    trace = []
    read_stock_done = False
    read_price_done = False
    write_done = False
    model_calls = 0
    for _ in range(max_steps):
        answer = backend.generate(history)
        model_calls += 1
        act = parse_action(answer)
        history.append({'role':'assistant','content':answer})
        if not act or act.get('tool') not in ('read_stock','read_price','write_stock','finish'):
            bad_actions += 1
            obs={'status':'invalid','error':'Expected one valid JSON tool action.'}
        elif act['tool'] == 'finish':
            reported_stock = act.get('reported_stock')
            reported_price = act.get('reported_price')
            completed = 1
            trace.append({'action':act,'response':{'status':'completed'}})
            break
        else:
            obs=guard.perform(act)
            if obs.get('status') != 'invalid':
                read_stock_done |= act['tool']=='read_stock'
                read_price_done |= act['tool']=='read_price'
                write_done |= act['tool']=='write_stock'
        trace.append({'action':act,'response':obs})
        history.append({'role':'user','content':'Tool observation: '+json.dumps(obs,sort_keys=True)+'\nSelect the next JSON action.'})
    expected = scenario.initial_stock + scenario.delta
    state_ok = int(guard.world.stock == expected)
    report_ok = int(type(reported_stock) is int and type(reported_price) is int
                    and reported_stock == expected and reported_price == scenario.unit_price
                    and read_stock_done and read_price_done and write_done)
    duplicate = int(guard.world.stock < expected) # only decrements are allowed
    return AgentResult(scenario.scenario_id,policy,int(state_ok and report_ok),state_ok,report_ok,
                       model_calls,guard.world.calls,guard.world.checks,duplicate,bad_actions,
                       completed,trace)
