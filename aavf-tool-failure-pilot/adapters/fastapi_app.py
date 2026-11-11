"""Optional FastAPI wrapper for the offline AAVF simulation.
Install: pip install fastapi uvicorn
Run: uvicorn adapters.fastapi_app:app --reload
Not used in the reported pilot experiments.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from dataclasses import asdict
from typing import Literal
from fastapi import FastAPI
from pydantic import BaseModel, Field
from aavf_sim import Scenario, execute

app = FastAPI(title='AAVF Simulation Adapter', version='0.1.0')

class ScenarioRequest(BaseModel):
    scenario_id: int = 1
    initial_stock: int = Field(40, ge=5)
    unit_price: int = Field(120, ge=1)
    delta: int = Field(-4, ge=-5, le=-1)
    read_stock_fault: Literal['none','missing','corrupt','invalid']='none'
    read_price_fault: Literal['none','missing','corrupt','invalid']='none'
    write_fault: Literal['none','error','timeout_pre','timeout_post','silent_drop']='none'
    policy: Literal['no_check','retry','verify_all','adaptive']='adaptive'

@app.get('/health')
def health(): return {'ok':True,'note':'Scripted simulation; not a live LLM'}

@app.post('/simulate')
def simulate(request: ScenarioRequest):
    spec=request.model_dump() if hasattr(request, 'model_dump') else request.dict()
    policy=spec.pop('policy')
    return asdict(execute(Scenario(**spec), policy))
