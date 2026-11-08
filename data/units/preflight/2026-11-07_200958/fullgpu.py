"""C1: comprobar si el profesor cabe completo en GPU con contexto 2048."""
import json
import time

from measure import OUT, PROMPTS, api

if __name__ == '__main__':
    path = OUT / 'fullgpu.jsonl'
    assert not path.exists(), 'No sobrescribir calibración'
    for i, prompt in enumerate(PROMPTS):
        prompt += ' Responde en español, explica brevemente los pasos y termina con un único JSON {"value": numero, "unit": "unidad"}.'
        payload = {'model': 'qwen3:8b', 'messages': [{'role': 'user', 'content': prompt}], 'stream': False, 'think': False, 'keep_alive': '5m', 'options': {'temperature': 0.7, 'seed': 42 + i, 'num_ctx': 2048, 'num_batch': 128, 'num_gpu': 99, 'num_predict': 1024}}
        start = time.monotonic()
        result = api('chat', payload)
        row = {'model': 'qwen3:8b', 'sample_index': i, 'request': payload, 'result': result, 'seconds': time.monotonic() - start, 'ps': api('ps')}
        with path.open('a') as stream:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')
        print(i, row['seconds'], result.get('eval_count'), result.get('done_reason'), flush=True)
    api('generate', {'model': 'qwen3:8b', 'keep_alive': 0})
