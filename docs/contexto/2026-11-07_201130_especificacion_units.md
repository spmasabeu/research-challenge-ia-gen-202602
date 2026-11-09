# Especificación ejecutable units

Estado vigente: diseño y datos cerrados en C4/C5; C6 en ejecución. Las propuestas iniciales siguientes se conservan como historial; el cierre C3 y la actualización v9 fijan el protocolo actual.

## Contrato y datos

Español, magnitudes positivas, un turno sin herramientas. Fórmulas, pi y equivalencias se dan explícitamente. Respuesta con desarrollo breve y un único resultado terminal JSON `{"value": número, "unit": "unidad"}` o cantidad/unidad terminal. Sin expresiones ejecutables, listas de alternativas ni campos privados enviados al modelo.

Familias: velocidad `v=d/t`, energía cinética `E=m*v²/2` y luminosidad `L=4*pi*d²*F`. Dos estructuras por familia: magnitud de entrada directa o suma de dos componentes (distancias, masas o flujos). La suma introduce composición real frente al spike; se balancea por estructura dentro de cada familia y split. Cambiar números no se presenta como originalidad suficiente. Se mantiene el mismo problema físico en tres representaciones, una por dificultad.

Rangos SI propuestos: distancias para velocidad 101–9999 m, tiempos 7–199 s; masas 1,1–49,9 kg, velocidades 1,1–49,9 m/s; distancias luminosas 1,1–99,9 m y flujos 1,1e-10–9,9e-6 W/m². Componentes positivos con fracción 0,2–0,8. Representación a 15 cifras significativas para evitar redondeos que cambien la referencia. Fuera del alcance: cero, signos negativos, incertidumbre física y unidades no catalogadas.

Fácil: SI sin conversiones; medio: una entrada convertida; difícil: dos entradas y salida convertidas. Operaciones y representación se registran: suma opcional, división/cuadrado/productos de fórmula, decimal o científica. No atribuir causalmente las diferencias solo al número de conversiones.

Catálogo de resultados: velocidad m/s y km/h; energía J, kJ, erg; luminosidad W, kW, erg/s, Lsun (1 Lsun=3,828e26 W). Entradas adicionales: km, min, g, erg/s/cm². Compatibilidad dimensional obligatoria. Unidades equivalentes aceptadas aun si la salida solicitada es otra. Tolerancia de recompensa 1% relativa, sin tolerancia absoluta; referencias positivas. Comprobación de generación relativa 1e-10, independiente del umbral de recompensa.

`reward(prompt: str, completion: str) -> float` usa registro privado de prompts exactos cargado por el consumidor; prompt desconocido levanta ValueError. `verify(task, completion)` ofrece clasificación `correct/numeric/unit/unparsed`. Unparsed no demuestra error matemático. Extracción no recibe referencia. Contradicciones finales se rechazan; no rescatar un valor anterior porque coincide con la referencia. Tabla privada entregada separada de prompts públicos.

## Modelos y ejecución

Objetivo Qwen3-1.7B (`qwen3:1.7b`); comparadores Llama-3.2-1B-Instruct (`llama3.2:1b`) y SmolLM2-1.7B-Instruct (`smollm2:1.7b-instruct-q4_K_M`); profesor Qwen3-8B (`qwen3:8b`). Artefactos GGUF y tokenizer/template identificados mediante digest de Ollama y `/api/show`; no atribuir revisión upstream inexistente. Licencias declaradas: Apache-2.0 para Qwen/SmolLM2; Llama 3.2 Community License para Llama. Tamaños reportados por backend se publican junto a etiquetas comerciales.

Ollama 0.18.0 local. Un proceso de inferencia a la vez; descarga solo SmolLM2 faltante. Piloto y baseline: temperatura 0,7, semillas 42/43/44, contexto 4096, máximo 1024 tokens, think=false, sin formato JSON forzado. Profesor train inicialmente máximo 2048 tokens y 4–8 respuestas por tarea, sujeto a calibración. Registrar parámetros enviados y respuesta íntegra del servidor; valores por defecto no controlados quedan identificados por template/versión, sin afirmar que toda diferencia causal procede del modelo.

Guardar cada respuesta y sincronizarla a disco antes de continuar. Reanudar solo claves ausentes con tareas/configuración/digest/código idénticos; no sobrescribir resultados ni completar una corrida bajo otro protocolo. Ejecuciones largas mediante servicio systemd de usuario, logs y estado persistentes. Fallos paran el lote; respuestas completadas permanecen.

Frontera después de C6: candidato DeepSeek-V4-Pro-0813 vía OpenRouter, pendiente de verificación de disponibilidad, credencial y presupuesto específicos. No usar `.env` ni API OpenAI. No se ejecuta entrenamiento.

## Bibliografía y límites de originalidad

- [Reasoning Gym, Stojanovski et al., 2025](https://arxiv.org/abs/2505.24760): generadores y recompensas verificables como antecedente metodológico. Nuestra contribución es acotada: unidades explícitas en español, variantes físicas agrupadas y composición con verificación dimensional; no se reclama inventar la generación procedural.
- [GSM-Symbolic, Mirzadeh et al.](https://arxiv.org/abs/2410.05229): variación simbólica como antecedente para estudiar sensibilidad. Aquí los tríos físicos controlan magnitudes entre representaciones; no constituyen observaciones independientes.
- Model cards oficiales: [Qwen3-1.7B](https://huggingface.co/Qwen/Qwen3-1.7B), [Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B), [Llama](https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct), [SmolLM2](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct). SmolLM2 documenta foco en inglés: la limitación en español se medirá, no se presupone equivalencia multilingüe.
- [API Ollama](https://docs.ollama.com/api/chat), [tag SmolLM2](https://ollama.com/library/smollm2:1.7b-instruct-q4_K_M). Fuentes consultadas 2026-11-07.

Plantillas compartidas entre splits limitan generalización a nuevas estructuras. Cuantizaciones distintas impiden aislar efecto del tamaño. La aceptación final no certifica coherencia de todos los pasos: se auditarán muestras SFT y se documentarán defectos y alcance de la revisión.

## Decisión C1

Cinco controles por modelo y cinco adicionales profesor validan acceso. Propuesta90 train/36 eval/54 test (20 grupos por familia), cuatro muestras profesor. Referencia bitácora para costo temporal. Todos los controles excluidos del final. Contexto2048, batch128, num_gpu99 permiten profesor íntegro en GPU; parámetros finales tras C3. Bibliografía consultada y límites documentados.

## Ajuste C3 antes de congelar

Luminosidad original quedó en6,67% por nivel. Versión units-2 usa distancias enteras2–30m y flujo0,01–0,99W/m², conservando estructura directa/suma y conversiones. Nuevo piloto independiente4304; evidencia anterior preservada. representation describe notación de magnitudes en campos visibles, no equivalencias ni la respuesta del modelo. Rangos anteriores de luminosidad quedan como historial, no diseño final.

## Diseño aceptado tras C3

units-3 conserva rangosv2 y cambia luminosidad/hard a salidaW, dosconversiones de entrada. Otros difíciles conservan tres. Composición piloto132/270correct,126numeric,12unparsed;pass@1=48,89%,pass@3=65,56%. Luminosidad/hard permanece cerca delsuelo(2/30); se retiene comoestrato de estrés, sin afirmar calibración suficiente porcelda. Fácil/medio no separan empíricamente. Verificadorv8 y guardia de backend comunes; máxima1024/contexto2048 confirmados con5controles profesor completos. Final90/36/54 y4muestrastrain.

## Actualización final del evaluador antes de test

El primer test se ejecuta con verifier-9 y dataset final-v2. Las seis particiones públicas/privadas son idénticas a final-v1; cambian código de evaluador y protocolo, preservando ambas versiones. v9 añade etiquetas terminales con signo igual y Watts observados en controles de desarrollo de SmolLM2, sin consultar test. No cambia etiquetas del piloto calibrado, profesor o negativos; controles Smol pasan de cinco unparsed a dos numeric y tres unparsed, sin aciertos nuevos. Parámetros efectivos comunes: contexto 2048, batch 128, num_gpu 99, máximo 1024 tokens, temperatura 0,7, top_p 0,9, top_k 40, min_p 0, think=false. Derivados finales derived-v3: 121 SFT y 35 DPO, con las 178 candidatas correctas distintas revisadas individualmente.
