# Calibración local del desafío units

C3 cerrado por señal global; no demuestra calibración suficiente de cada celda ni mejora tras entrenamiento. [Bitácora](2026-11-07_200958_bitacora_ejecucion_desafio_units.md).

Composición precongelamiento: velocidad/energía del piloto1, luminosidad fácil/media del piloto2 y difícil del piloto3. No se seleccionan respuestas individuales.90tareas,30problemasfísicos,3muestras; todos quedan excluidos del final.

| Familia/nivel | Correctas/30 | pass@1 | pass@3 | Sin interpretar |
| --- | --- | --- | --- | --- |
| energy/easy | 18/30 | 60.00% | 70.00% | 1 |
| energy/hard | 5/30 | 16.67% | 40.00% | 2 |
| energy/medium | 18/30 | 60.00% | 80.00% | 0 |
| luminosity/easy | 4/30 | 13.33% | 40.00% | 2 |
| luminosity/hard | 2/30 | 6.67% | 20.00% | 5 |
| luminosity/medium | 7/30 | 23.33% | 50.00% | 1 |
| speed/easy | 30/30 | 100.00% | 100.00% | 0 |
| speed/hard | 19/30 | 63.33% | 90.00% | 0 |
| speed/medium | 29/30 | 96.67% | 100.00% | 1 |

| Nivel | Correctas/90 | pass@1 | pass@3 |
| --- | --- | --- | --- |
| easy | 52/90 | 57.78% | 70.00% |
| medium | 54/90 | 60.00% | 76.67% |
| hard | 26/90 | 28.89% | 50.00% |

**Global:**132correctas,126numeric,12unparsed; cobertura95,56%;pass@1=48,89%,pass@3=65,56%;cotas superiores53,33%/71,11%. Tres truncamientos conservados. Unparsed no demuestra error matemático; cotas no son intervalos de confianza.

Alarma de techo en velocidad fácil/media: se conservan como controles. Primer piloto luminosidad2/30por nivel; rangos reducidos a distancias enteras2–30m y flujo0,01–0,99W/m². Segundo piloto4/30fácil,7/30medio,0/30difícil. Tercero conserva dosconversiones de entrada y salidaW:2/30difícil. Este estrato sigue cerca delsuelo; se retiene como estrés y se declara esa limitación. Fácil/media no muestran orden empírico estricto en esta muestra. No atribuir efectos solo al número de conversiones.

Las45trazas de auditoría (5/celda) están en[datos de calibración](../../data/units/pilot-calibrated/audit.jsonl), conjuicios de agente y hashes; no son revisión humana docente. Ejemplos: omisión de factor60 en velocidad; sustitución de operandos en energía; pérdida de exponentes y mezcla m²/cm² en luminosidad. Un final dentro1% puede acompañarse de una igualdad aritmética o conversión falsa: esas trazas no son automáticamente SFT.

Verificadorv8: JSON o cantidad terminal, equivalencias dimensionales, coma decimal y notación científica; rechaza alternativas, finales contradictorios, claves duplicadas, no finitos y negaciones del JSON. Son límites conocidos: expresiones no evaluadas, resultados finales con camposvalue/unit en prosa o subíndices LaTeX no admitidos; las ambigüedades permanecenunparsed aun cuando una lectura contextual sugiera cantidad. No rescatar números por coincidencia con referencia.

Historialv1–v7 calculado sobre un mismo corpus de270respuestas: [comparación](../../data/units/pilot-v1/evaluator-history/full-corpus-comparison.json).v8 añade negación en línea previa y conserva las métricas de pilotos1/2/3 frente av7. Estos son cambios de extracción/evaluación, nunca mejora de capacidad del modelo.

Fuente ejecutable:[summary.json](../../data/units/pilot-calibrated/summary.json); fuentes y huellas:[sources.json](../../data/units/pilot-calibrated/sources.json). Las variantes relacionadas no son observaciones independientes; los promedios no garantizan generalización a otras plantillas, unidades o dominios.
