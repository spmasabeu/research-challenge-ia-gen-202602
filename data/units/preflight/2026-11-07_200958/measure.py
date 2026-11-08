"""C1: cinco consultas de desarrollo por modelo; sin test ni API pagada."""
import json
import time
import urllib.request
from pathlib import Path

OUT = Path(__file__).parent
MODELS = ['qwen3:1.7b', 'llama3.2:1b', 'smollm2:1.7b-instruct-q4_K_M', 'qwen3:8b']
PROMPTS = [
    'Recorrido de 137 m en 13 s. Calcula v=d/t en m/s.',
    'Masa 7 kg y velocidad 13 m/s. Calcula E=m*v^2/2 en J.',
    'Distancia 7 m y flujo 3.7e-8 W/m^2. Calcula L=4*pi*d^2*F en W. Usa pi=3.141592653589793.',
    'Dos tramos de 0.127 km y 0.293 km en tiempo total 0.35 min. Calcula v=(d1+d2)/t en km/h. 1 km=1000 m; 1 min=60 s; 1 m/s=3.6 km/h.',
    'Dos masas de 1300 g y 2700 g se mueven a 28.8 km/h. Calcula E=(m1+m2)*v^2/2 en kJ. 1000 g=1 kg; 3.6 km/h=1 m/s; 1000 J=1 kJ.'
]


def api(route, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request('http://127.0.0.1:11434/api/' + route, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=600) as response:
        return json.load(response)


if __name__ == '__main__':
    assert len(PROMPTS) == 5 and len(set(PROMPTS)) == 5
    (OUT / 'tags.json').write_text(json.dumps(api('tags'), indent=2))
    path = OUT / 'responses.jsonl'
    done = set()
    if path.exists():
        done = {(r['model'], r['sample_index']) for r in map(json.loads, path.read_text().splitlines())}
    for model in MODELS:
        (OUT / (model.replace(':', '_') + '-show.json')).write_text(json.dumps(api('show', {'model': model}), indent=2))
        for i, prompt in enumerate(PROMPTS):
            if (model, i) in done:
                continue
            prompt += ' Responde en español, explica brevemente los pasos y termina con un único JSON {"value": numero, "unit": "unidad"}.'
            payload = {'model': model, 'messages': [{'role': 'user', 'content': prompt}], 'stream': False, 'think': False, 'keep_alive': '5m', 'options': {'temperature': 0.7, 'seed': 42 + i, 'num_ctx': 4096, 'num_predict': 2048 if model == 'qwen3:8b' else 1024}}
            start = time.monotonic()
            result = api('chat', payload)
            row = {'model': model, 'sample_index': i, 'request': payload, 'result': result, 'seconds': time.monotonic() - start, 'ps': api('ps')}
            with path.open('a') as stream:
                stream.write(json.dumps(row, ensure_ascii=False) + '\n')
                stream.flush()
            print(model, i, round(row['seconds'], 2), result.get('eval_count'), result.get('done_reason'), flush=True)
        api('generate', {'model': model, 'keep_alive': 0})
