# Spike: razonamiento cuantitativo con unidades

> **Congelado (2026-11-07).** El entorno principal vive en `src/challenge/` (ver README raíz); allí se corrigieron el separador de miles, el hedge JSON, los alias de unidades y la unidad pedida. Para el informe, usar la vista **automática** (Qwen pass@1 70.74%), no la `final` con revisiones manuales: el verificador será la recompensa.

Evaluar si Qwen3-1.7B tiene aciertos y errores cuantitativos reales en tareas con fórmulas y conversiones explícitas. Comparación local con Llama 3.2-1B sobre 90 tareas y tres intentos por tarea. [Informe y resultados](report.md).

Este spike aporta evidencia para elegir y calibrar el problema del desafío; el entorno principal y los datos de entrenamiento siguen pendientes. El tema elegido quedó registrado en [Decisiones](../../docs/2026-10-29_093018_decisiones.md).

## Archivos

```text
spikes/units/
├── README.md
├── report.md
├── units.py
├── evaluate.py
├── test_units.py
└── results/
    ├── tasks.jsonl
    ├── environment.json
    ├── comparison.json
    ├── qwen3-1.7b/
    │   ├── metadata.json
    │   ├── responses.jsonl
    │   └── summary.json
    └── llama3.2-1b/
        ├── metadata.json
        ├── responses.jsonl
        └── summary.json
```

- `units.py`: genera tareas, extrae respuestas y verifica cantidad/unidad con tolerancia relativa del 1%.
- `evaluate.py`: ejecuta inferencia, calcula métricas y comprueba los artefactos guardados.
- `tasks.jsonl`: único conjunto compartido de tareas, con referencias calculadas por código. Solo el prompt se envía al modelo.
- `responses.jsonl`: respuestas completas, extracción y clasificación automáticas y resultado final. Las cinco revisiones contextuales de Qwen están integradas como `manual_review`, con cantidad, unidad, evidencia y hash de la respuesta revisada.
- `summary.json`: métricas globales, por nivel y por familia, con vistas `automatic` y `final`.
- `comparison.json`: comparación derivada de los resúmenes de ambos modelos.
- `metadata.json`: modelo y digest de pesos, configuración, semillas, fecha y commit de inferencia, hashes de tareas, respuestas y código de evaluación. `inference_script_sha256` identifica el código usado al generar las respuestas; `evaluation` identifica el código que verifica los artefactos vigentes. Las fechas corresponden a las inferencias guardadas.
- `environment.json`: hardware y backend del experimento; cada modelo también registra su entorno en metadatos.

## Comprobar resultados sin modelos

Desde esta carpeta, con `uv` instalado:

```bash
uv run --no-project --isolated --python 3.12 python -m unittest discover -s . -v
uv run --no-project --isolated --python 3.12 python evaluate.py check results
```

Diez pruebas, sin Ollama ni GPU. `check` vuelve a extraer y verificar las 540 respuestas, aplica las revisiones contextuales documentadas, verifica integridad/completitud, coteja resúmenes y comparación e imprime el resultado. Comprueba también que todos los modelos compartan tareas, configuración y semillas. No modifica archivos ni llama a un modelo.

Los hashes fijan el código con que se calcularon los resultados guardados: modificar el evaluador requiere actualizar explícitamente las clasificaciones y sus artefactos; `check` detecta la discrepancia.

## Ejecutar nuevas inferencias

Requiere Ollama disponible en `http://127.0.0.1:11434`, repositorio Git y espacio para los modelos. En una terminal:

```bash
ollama serve
```

En otra, desde esta carpeta:

```bash
ollama pull qwen3:1.7b
ollama pull llama3.2:1b
uv run --no-project --isolated --python 3.12 python evaluate.py run --model qwen3:1.7b --samples 3 --output /tmp/units-run/qwen3-1.7b
uv run --no-project --isolated --python 3.12 python evaluate.py run --model llama3.2:1b --samples 3 --output /tmp/units-run/llama3.2-1b
uv run --no-project --isolated --python 3.12 python evaluate.py check /tmp/units-run
```

Ejecutar un modelo a la vez. Cada carpeta de modelo debe ser nueva; cambiar `/tmp/units-run` al repetir. Los modelos comparten `tasks.jsonl` en la carpeta padre. Una ejecución incompleta conserva sus respuestas parciales y no pasa la comprobación de completitud.

Configuración común: semilla del dataset 43; `think=false`, contexto 4096, hasta 1024 tokens. Tres muestras usan temperatura 0.7 y semillas 42, 43 y 44; una muestra usa temperatura 0. No se fuerza JSON desde Ollama. Repetir la inferencia puede producir otras respuestas por diferencias de hardware, pesos o backend. Las revisiones manuales corresponden a respuestas concretas y no se transfieren automáticamente a nuevas ejecuciones.

## Evaluación

`extract_answer(completion)` interpreta una respuesta terminal sin consultar la referencia: JSON o texto, Markdown, coma decimal, notación científica y envoltorios LaTeX sencillos. Se aceptan unidades equivalentes del catálogo. No se ejecutan expresiones del modelo ni se busca en su desarrollo un número que coincida con la referencia.

`verify(task, completion)` clasifica:

- `correct`: cantidad y unidad compatibles, dentro del 1% relativo.
- `numeric`: cantidad interpretable, fuera de tolerancia tras convertir unidades.
- `unit`: unidad fuera del catálogo de la dimensión; requiere comprobar si es incompatible o una notación equivalente aún no soportada.
- `unparsed`: ambigüedad, unidad ausente o sintaxis no soportada. No demuestra error matemático.

La vista `automatic` usa exclusivamente el parser. La vista `final` incorpora las extracciones contextuales documentadas y aplica el mismo verificador numérico. Una revisión debe tener evidencia, coincidir con el hash de la respuesta y corresponder a un caso no interpretado automáticamente. Nunca cambia la referencia ni ejecuta código del modelo.

Las métricas publican cobertura, exactitud condicionada a extracción y cotas de pass@k: `1 - C(n-c,k)/C(n,k)`. La cota inferior usa aciertos verificados; `pass_at_k_upper_bound` considera correctos los `unparsed`. Son cotas de incertidumbre de extracción, no intervalos de confianza. Con tres muestras se reportan pass@1 y pass@3; este último mide problemas con al menos un acierto observado.

Resultado final de Qwen: 193/270 aciertos, pass@1 71.48% y pass@3 85.56%. Llama conserva 115 respuestas sin interpretar; su cota inferior no debe presentarse como exactitud matemática puntual. Ver el [informe](report.md) para límites, ejemplos y pendientes de la entrega.
