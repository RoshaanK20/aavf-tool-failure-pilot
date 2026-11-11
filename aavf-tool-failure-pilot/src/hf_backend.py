"""Optional Hugging Face language-model backend for the AAVF LLM experiment.

Requires torch, transformers and accelerate; model weights are downloaded when
run in Colab. Offline local CI tests only validate the evaluation harness.
"""
class HFBackend:
    def __init__(self, model_id: str='Qwen/Qwen2.5-1.5B-Instruct', max_new_tokens: int=160):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, torch_dtype='auto', device_map='auto'
        ).eval()
        self.max_new_tokens=max_new_tokens

    def generate(self,messages):
        t=self.tokenizer
        prompt=t.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
        inputs=t([prompt],return_tensors='pt').to(self.model.device)
        with self.torch.inference_mode():
            output=self.model.generate(**inputs,max_new_tokens=self.max_new_tokens,
                                       do_sample=False,pad_token_id=t.eos_token_id)
        return t.decode(output[0][inputs['input_ids'].shape[-1]:],skip_special_tokens=True).strip()
