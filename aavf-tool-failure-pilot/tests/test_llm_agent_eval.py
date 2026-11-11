import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from llm_agent_eval import run_agent,GuardedWorld,parse_action
from aavf_sim import Scenario

class ScriptBackend:
    """Offline stub; tests harness only and is NOT a language model."""
    def generate(self,history):
        calls=[x for x in history if x['role']=='assistant']
        if len(calls)==0:return '{"tool":"read_stock"}'
        if len(calls)==1:return '{"tool":"read_price"}'
        if len(calls)==2:return '{"tool":"write_stock","delta":-3}'
        s=[x['content'] for x in history if x['content'].startswith('Tool observation:')]
        import json
        stock=json.loads(s[0].split('Tool observation: ')[1].split('\n')[0])['value']
        price=json.loads(s[1].split('Tool observation: ')[1].split('\n')[0])['value']
        return json.dumps({'tool':'finish','reported_stock':stock-3,'reported_price':price})

class LLMHarnessTests(unittest.TestCase):
    def test_parse_json(self):
        self.assertEqual(parse_action('```json\n{"tool":"read_stock"}\n```')['tool'],'read_stock')
    def test_clean_task_passes_mock_backend(self):
        s=Scenario(3,35,100,-3,'none','none','none')
        for policy in ('no_check','retry','adaptive','verify_all'):
            r=run_agent(ScriptBackend(),s,policy)
            self.assertEqual(r.success,1, (policy,r))
            self.assertEqual(r.model_calls,4)
    def test_real_model_is_not_faked_by_harness(self):
        s=Scenario(4,35,100,-3,'corrupt','none','none')
        r=run_agent(ScriptBackend(),s,'no_check')
        self.assertEqual(r.success,0)
    def test_verifier_recovers_known_schema_anomaly(self):
        s=Scenario(7,35,100,-3,'missing','none','none')
        r=run_agent(ScriptBackend(),s,'adaptive')
        self.assertEqual(r.success,1)
        self.assertGreater(r.verification_calls,0)
    def test_duplicate_retry_and_adaptive_safety(self):
        s=Scenario(9,35,100,-3,'none','none','timeout_post')
        ret=run_agent(ScriptBackend(),s,'retry')
        adap=run_agent(ScriptBackend(),s,'adaptive')
        self.assertEqual(ret.duplicate_write,1)
        self.assertEqual(adap.duplicate_write,0)
if __name__=='__main__':unittest.main()
