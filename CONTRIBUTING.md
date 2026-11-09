# Convenciones de colaboración

Usar ramas `feat/<tema>` para funcionalidades, `fix/<tema>` para correcciones y
`docs/<tema>` para documentación. Integrar a `main` mediante pull request.

Los commits y el título del PR siguen Conventional Commits:

```text
tipo(alcance): resumen imperativo
```

Tipos habituales: `feat`, `fix`, `docs`, `test`, `refactor`, `build`, `ci` y
`chore`. Alcance opcional; asunto breve, preferiblemente hasta 50 caracteres y
sin punto final. Mantener asuntos en inglés, como el historial del repositorio.
Separar commits por responsabilidad; incluir pruebas junto al cambio que validan.

Ejemplos: `feat(challenge): add unit verification`,
`docs(report): clarify extraction limits`.

Todo PR tiene exactamente estas cuatro secciones, definidas en
[la plantilla](.github/pull_request_template.md):

1. Problema y objetivo.
2. Cambios realizados.
3. Validación y evidencia.
4. Limitaciones y seguimiento.

Las pruebas y resultados declarados deben tener evidencia. Identificar lo no
ejecutado; nunca incluir credenciales, pesos ni entornos virtuales. Las llamadas
pagadas requieren presupuesto explícito; recalcular métricas guardadas no lo necesita.
