"""Run a reproducible simulation, write artifacts and bootstrap CIs.
No LLM or network calls are made. These are SCRIPTED-POLICY simulation results.
"""
import sys, csv, json, statistics
from collections import defaultdict, Counter
from pathlib import Path
from random import Random
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from aavf_sim import run, POLICIES

ROOT = Path(__file__).parent
RESULTS = ROOT/'results'
RESULTS.mkdir(parents=True, exist_ok=True)
SEED=20261110
N=1600
B=3000
scenarios, rows = run(N, seed=SEED)

with open(RESULTS/'scenarios.jsonl', 'w') as f:
    for s in scenarios: f.write(json.dumps(vars(s),sort_keys=True)+'\n')
with open(RESULTS/'outcomes.csv', 'w', newline='') as f:
    wr=csv.DictWriter(f, fieldnames=list(vars(rows[0])))
    wr.writeheader(); wr.writerows(vars(x) for x in rows)

by=defaultdict(dict)
for r in rows: by[r.scenario_id][r.policy]=r
rng=Random(SEED+13)

def paired_ci(a,b,metric):
    diffs=[getattr(by[i][a],metric)-getattr(by[i][b],metric) for i in range(N)]
    observed=sum(diffs)/N
    samples=sorted(sum(diffs[rng.randrange(N)] for _ in range(N))/N for _ in range(B))
    return {'diff': round(observed,5), 'low95': round(samples[int(B*.025)],5),
            'high95':round(samples[int(B*.975)],5)}

summaries={}
for policy in POLICIES:
    subset=[by[i][policy] for i in range(N)]
    summaries[policy]={
       'success_rate': round(sum(x.success for x in subset)/N,5),
       'state_correct_rate': round(sum(x.state_correct for x in subset)/N,5),
       'report_correct_rate': round(sum(x.report_correct for x in subset)/N,5),
       'duplicate_count': sum(x.duplicate_write for x in subset),
       'mean_tool_calls':round(sum(x.total_calls for x in subset)/N,5),
       'mean_extra_verification_calls': round(sum(x.extra_checks for x in subset)/N,5)}
summary={
    'study_type':'Controlled simulation of scripted tool-using policies; NO LLM evaluated',
    'scenario_count':N, 'seed':SEED, 'bootstrap_iterations':B,
    'fault_probability_assumptions': {
      'read_each': {'none':.85,'corrupt':.07,'missing':.05,'invalid':.03},
      'write':{'none':.80,'error':.05,'timeout_pre':.05,'timeout_post':.05,'silent_drop':.05}},
    'policies':summaries,
    'paired_success_difference_adaptive_minus_no_check':paired_ci('adaptive','no_check','success'),
    'paired_success_difference_adaptive_minus_verify_all':paired_ci('adaptive','verify_all','success'),
    'paired_call_difference_adaptive_minus_verify_all':paired_ci('adaptive','verify_all','total_calls'),
    'paired_duplicate_difference_retry_minus_adaptive':paired_ci('retry','adaptive','duplicate_write'),
    'write_faults':dict(Counter(s.write_fault for s in scenarios)),
    'read_stock_faults':dict(Counter(s.read_stock_fault for s in scenarios)),
    'read_price_faults':dict(Counter(s.read_price_fault for s in scenarios)),
}
with open(RESULTS/'summary.json','w') as f: json.dump(summary,f,indent=2)
print(json.dumps(summary,indent=2))

# Optional figures when matplotlib is available. Figures display simulated outputs.
try:
    import matplotlib.pyplot as plt
    p=list(POLICIES)
    fig, ax=plt.subplots(figsize=(7,3.5))
    ax.bar([x.replace('_','\n') for x in p],[100*summaries[x]['success_rate'] for x in p])
    ax.set_ylim(0,100);ax.set_ylabel('End-to-end success (%)')
    ax.set_title('Simulation only: scripted tool workflows')
    fig.tight_layout();fig.savefig(ROOT/'figures'/'simulation_success.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,3.5))
    ax.bar([x.replace('_','\n') for x in p],[summaries[x]['mean_tool_calls'] for x in p])
    ax.set_ylabel('Mean total tool calls per scenario')
    ax.set_title('Simulation only: verification overhead included')
    fig.tight_layout();fig.savefig(ROOT/'figures'/'simulation_calls.png',dpi=180);plt.close(fig)
except ImportError: pass
