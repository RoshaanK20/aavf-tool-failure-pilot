"""REAL language-model agent runner; requires local / Colab HF model weights.

Example (Colab): python run_llm_experiment.py --n 12 --model Qwen/Qwen2.5-1.5B-Instruct
No result is reported until model inference actually finishes.
"""
import argparse,csv,json,time,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'src'))
from aavf_sim import make_scenarios
from llm_agent_eval import run_agent
from hf_backend import HFBackend

p=argparse.ArgumentParser()
p.add_argument('--n',type=int,default=12)
p.add_argument('--seed',type=int,default=20261110)
p.add_argument('--model',default='Qwen/Qwen2.5-1.5B-Instruct')
p.add_argument('--max-steps',type=int,default=8)
p.add_argument('--output',default='results/llm_runs')
a=p.parse_args()
if not 1 <= a.n <= 1000: p.error('--n should be 1 to 1000')
backend=HFBackend(a.model)
scenarios=make_scenarios(a.n,a.seed)
output=BASE/a.output;output.mkdir(parents=True,exist_ok=True)
rows=[]
with (output/'detailed_traces.jsonl').open('w',encoding='utf-8') as f:
    for s in scenarios:
        for policy in ('no_check','retry','adaptive','verify_all'):
            t=time.perf_counter();r=run_agent(backend,s,policy,a.max_steps)
            item={'scenario_id':r.scenario_id,'policy':r.policy,'success':r.success,
                  'final_state_correct':r.final_state_correct,
                  'final_report_correct':r.final_report_correct,
                  'model_calls':r.model_calls,'tool_calls':r.tool_calls,
                  'verification_calls':r.verification_calls,'duplicate_write':r.duplicate_write,
                  'invalid_actions':r.invalid_actions,'completed':r.completed,
                  'elapsed_seconds':round(time.perf_counter()-t,4)}
            rows.append(item)
            f.write(json.dumps({**item,'trace':r.trace},ensure_ascii=False)+'\n');f.flush()
            print('scenario',s.scenario_id,'policy',policy,'success',r.success,'model calls',r.model_calls,flush=True)
with (output/'metrics.csv').open('w',newline='',encoding='utf-8') as f:
    writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
summary={}
for policy in ('no_check','retry','adaptive','verify_all'):
    r=[x for x in rows if x['policy']==policy]
    summary[policy]={k:sum(x[k] for x in r)/len(r) for k in
                     ('success','tool_calls','verification_calls','model_calls','invalid_actions','duplicate_write')}
with (output/'summary.json').open('w',encoding='utf-8') as f:
    json.dump({'study':'real LLM action selection','model':a.model,'seed':a.seed,'n_scenarios':a.n,
               'max_steps':a.max_steps,'policies':summary},f,indent=2)
print(json.dumps(summary,indent=2))
