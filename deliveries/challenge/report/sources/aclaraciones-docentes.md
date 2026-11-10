# Aclaraciones docentes sobre datos derivados y línea base del desafío

Fecha de incorporación: 2026-11-07. Fecha de la respuesta original y enlace: no aportados.
Fuente: respuesta atribuida al equipo docente, transcrita por el usuario en esta conversación. Se conserva como aclaración complementaria al PDF, sin atribuirle una publicación o fecha no verificadas.

## Interpretación para ejecutar el plan

- Obligatorio: SFT generado mediante inferencia de un modelo abierto mayor y filtrado por el verificador; las trazas programáticas son un complemento.
- Obligatorio: referencias de tareas calculadas por código; el modelo generador produce respuestas candidatas, no valida ni reemplaza esas referencias.
- Obligatorio según esta aclaración: al menos tres modelos pequeños de aproximadamente 1–2B en la línea base, incluido el objetivo; preferiblemente de familias distintas.
- Recomendado: muestrear 4–8 respuestas por problema de train y apuntar a unas 4.000 trazas correctas SFT y 2.000 pares DPO, cubriendo dificultad. Son metas orientativas; menos datos requieren justificación y análisis.
- Permitido: usar respuestas incorrectas de un modelo pequeño como rechazadas cuando el modelo generador casi no falla, identificando su procedencia.
- Ampliación ideal: evaluar también un mediano y un grande, privilegiando abiertos; si no es viable, justificarlo. La lectura anterior de una referencia de frontera incondicional se actualiza con esta indicación.
- Se mantiene: solo inferencia en el desafío, pass@1/pass@k por dificultad y evidencia de zona aprendible del objetivo.

## Respuesta compartida

> 1. Sí. El enunciado pide explícitamente “trazas para SFT generadas con un modelo abierto de mayor tamaño y filtradas con el verificador”. Las trazas que genera su harness de forma programática están muy bien y las pueden incluir como un plus, pero no reemplazan a las del modelo, por dos razones:
>
> Las trazas generadas por código suelen salir de plantillas y no se parecen a cómo razona un LLM. Para el SFT conviene que el modelo pequeño imite razonamiento en lenguaje natural que use bien el harness.
> Los pares para DPO necesitan respuestas correctas e incorrectas muestreadas de un modelo para un mismo problema, y eso sale naturalmente de muestrear varias veces y filtrar con el verificador.
> Ojo: el modelo grande solo genera datos; no valida las tareas. Las respuestas de las tareas deben ser verificables por construcción, es decir, calculadas por código.
>
> 2. Sí, es solo inferencia: hacen prompting del modelo grande contra el harness, muestrean varias respuestas por problema y se quedan con las que el verificador aprueba. No hay que entrenar nada en esta etapa.
>
> El enunciado no fija un número. Como referencia razonable:
>
> Muestreen k respuestas por problema (por ejemplo, k = 4–8) sobre el split de train.
> Apunten a del orden de 4.000 trazas correctas para SFT y unos 2.000 pares para DPO. Más trazas son bienvenidas; si quedan con menos, justifíquenlo.
> Cubran todos los niveles de dificultad.
> Para DPO, si el modelo grande casi no falla, pueden usar respuestas incorrectas de un modelo más pequeño como “rejected”, indicándolo.
> Más que llegar a un número exacto, importa que reporten cuántas trazas generaron, cuántas pasaron el filtro (por dificultad), qué modelo usaron y con qué procedimiento. Si tienen poco cómputo, es preferible tener menos trazas bien documentadas que muchas sin análisis.
>
> 3. La línea base también es solo inferencia: evalúan los modelos tal cual, sin entrenar. Como mínimo usen 3 modelos pequeños (~1–2B), incluido el modelo objetivo, idealmente de familias distintas (Qwen, Llama, OLMo, etc.). Lo ideal es sumar también un modelo mediano y uno grande, privilegiando modelos abiertos; si no pudieron correrlos/llamarlos, justifíquenlo. Reporten pass@1 y pass@k por nivel de dificultad y muestren que el modelo objetivo cae en la zona aprendible (ni siempre 0, ni siempre 1).
