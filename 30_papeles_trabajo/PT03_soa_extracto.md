# PT03 · Extracto de la Declaración de Aplicabilidad

| Control | Título | ¿Aplica? | Justificación | Estado | Riesgo que trata |
|---|---|---|---|---|---|
| A.8.8 | Gestión de vulnerabilidades técnicas | Sí | El laboratorio contiene aplicaciones y componentes con vulnerabilidades que deben identificarse, priorizarse y tratarse. | No implementado | R-001, R-002 y R-003 |
| A.8.9 | Gestión de la configuración | Sí | Se emplean configuraciones y credenciales débiles definidas directamente en Docker Compose. | Parcial | R-004, R-005, R-006, R-007 y R-009 |
| A.5.17 | Información de autenticación | Sí | Las credenciales de los servicios se almacenan en variables de entorno y algunas utilizan valores débiles. | No implementado | R-004 y R-006 |
| A.8.24 | Uso de criptografía | Sí | Los servicios web del laboratorio operan mediante HTTP y el tráfico interno no está cifrado. | No implementado | R-008 |
| A.7.4 | Monitoreo de la seguridad física | No | El alcance del taller es un entorno virtual local y no incluye instalaciones físicas. | N/A | — |

> Los identificadores se vinculan con el registro
> `40_hallazgos/PT03_registro_riesgos.csv`. El riesgo R-010 se relaciona además
> con la continuidad y respaldo de la información persistente.
