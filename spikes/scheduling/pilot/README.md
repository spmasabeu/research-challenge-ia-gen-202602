# Piloto inicial histórico

Tres tareas, una muestra Qwen, semilla 99. El parser inicial exigía JSON completo sin prosa: rechazó respuestas con explicación y cerco JSON. Se amplió antes de congelar el benchmark para aceptar arrays en cercos inequívocos (y repetición idéntica), rechazando candidatos contradictorios. Los artefactos crudos se conservan; sus hashes de código identifican la versión histórica, por lo que check con el código actual detecta discrepancia esperada. El piloto vigente está en pilot-v2/. No usar este piloto para métricas del benchmark.

Se conservan scheduling.py y evaluate.py históricos, con hashes originales. Validación histórica: `.venv/bin/python spikes/scheduling/pilot/evaluate.py check spikes/scheduling/pilot` (pasa). No cambiar esos snapshots.
