


'''
print('-'* 50)
print('GROQ')
groq_response = call_groq(model_name= 'deepseek-r1-distill-llama-70b', content_prompt = prompt)
pprint(groq_response)
print(json.loads(groq_response.model_dump_json(indent=2)))
'''

GROQ_MODELS = [
    'gemma2-9b-it',
    'llama-3.3-70b-versatile',
    'llama-3.1-8b-instant',
    'llama3-70b-8192',
    'deepseek-r1-distill-llama-70b',
    'deepseek-r1-distill-qwen-32b',
    'mixtral-8x7b-32768'
]
