"""Optional MCP tool adapter exposing AAVF's synthetic simulator.
Install MCP Python SDK: pip install mcp
Run: python adapters/mcp_server.py
Not used in the reported simulation results. Do not claim this tests an LLM.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from dataclasses import asdict
from mcp.server.fastmcp import FastMCP
from aavf_sim import Scenario, execute

mcp = FastMCP('AAVF Synthetic Agent Lab')

@mcp.tool()
def simulate_inventory_tool_failure(
    policy: str = 'adaptive',
    write_fault: str = 'timeout_post',
    read_stock_fault: str = 'none',
    read_price_fault: str = 'none',
    delta: int = -4
) -> dict:
    """Run one SCRIPTED inventory workflow under injected faults.
    Returns simulation metrics, not an LLM inference result.
    """
    if policy not in ('no_check','retry','verify_all','adaptive'):
        raise ValueError('invalid policy')
    if write_fault not in ('none','error','timeout_pre','timeout_post','silent_drop'):
        raise ValueError('invalid write fault')
    if read_stock_fault not in ('none','missing','corrupt','invalid') or read_price_fault not in ('none','missing','corrupt','invalid'):
        raise ValueError('invalid read fault')
    if delta not in (-1,-2,-3,-4,-5): raise ValueError('delta must be -1..-5')
    s = Scenario(1, 40, 120, delta, read_stock_fault, read_price_fault, write_fault)
    return asdict(execute(s, policy))

if __name__ == '__main__':
    mcp.run()
