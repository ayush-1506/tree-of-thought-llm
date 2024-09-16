import os
from groq import Groq
import backoff 

completion_tokens = prompt_tokens = 0

api_key = os.getenv("GROQ_API_KEY", "")
if api_key == "":
    raise Exception("Please set API Key")

client = Groq()


@backoff.on_exception(backoff.expo, Exception)
def completions_with_backoff(**kwargs):
    return client.chat.completions.create(
                model=kwargs["model"],
                messages=kwargs["messages"],
                max_tokens=kwargs["max_tokens"],
                temperature=kwargs["temperature"],
            )

def gpt(prompt, model="llama-3.1-70b-versatile", temperature=0.7, max_tokens=1000, n=1, stop=None) -> list:
    messages = [{"role": "user", "content": prompt}]
    return llm(messages, model=model, temperature=temperature, max_tokens=max_tokens, n=n, stop=stop)
    
def llm(messages, model="llama-3.1-70b-versatile", temperature=0.7, max_tokens=1000, n=1, stop=None) -> list:
    global completion_tokens, prompt_tokens
    outputs = []
    while n > 0:
        cnt = min(n, 20)
        n -= cnt
        res = completions_with_backoff(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens, n=cnt, stop=stop)
        print(res.choices)
        outputs.extend([choice.message.content for choice in res.choices])
        # log completion tokens
        #completion_tokens += res["usage"]["completion_tokens"]
        #prompt_tokens += res["usage"]["prompt_tokens"]
    return outputs
    
#def gpt_usage(backend="gpt-4"):
#    global completion_tokens, prompt_tokens
#    if backend == "gpt-4":
#        cost = completion_tokens / 1000 * 0.06 + prompt_tokens / 1000 * 0.03
#    elif backend == "gpt-3.5-turbo":
#        cost = completion_tokens / 1000 * 0.002 + prompt_tokens / 1000 * 0.0015
#    return {"completion_tokens": completion_tokens, "prompt_tokens": prompt_tokens, "cost": cost}
