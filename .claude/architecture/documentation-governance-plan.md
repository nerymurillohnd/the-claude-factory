# Plan: gobernanza de documentación con agentes especializados

## Contexto

Hay 15 templates en `.claude/templates/` y 16 referencias en `.claude/references/`. Nada obliga a consultarlos; las referencias mezclan situaciones, citan scripts que no existen aquí (37 menciones) y llevan fechas que van a memoria. Lo que salga de aquí es la base de toda la documentación que llega a terceros.

Fuentes leídas completas el 2026-11-10 (Claude Code 2.1.322): `agents`, `workflows`, `agent-teams`, `sub-agents`, `skills`, `hooks`, `features-overview`, `model-config`, `checkpointing`, `memory`, la guía de esfuerzo de la plataforma y la referencia `/workflow-authoring`.

## Tus decisiones, incorporadas

1. **Un solo skill de gobernanza documental**, que clasifica los agentes y dice cuándo y cómo lanzar cada uno.
2. **Agentes especializados como contrato**: reglas, procedimiento por situación y template embebido.
3. **Eliminar `CLAUDE_CODE_SUBAGENT_MODEL`** y fijar por convención modelo y esfuerzo de cada agente.

## Un hecho que cambia cómo se cumple la decisión 1

Un skill no puede "cargar siempre" en la sesión principal. Cita de `skills` → Control who invokes a skill: *"In a regular session, skill descriptions are loaded into context so Claude knows what's available, but full skill content only loads when invoked."* Lo que carga siempre, según `features-overview` → tabla de carga, es `CLAUDE.md` y las reglas sin `paths`.

Para que tu intención se cumpla de verdad (nadie escribe documentación sin pasar por la gobernanza), uso tres piezas, cada una con el mecanismo que la documentación le asigna:

| Pieza | Mecanismo | Qué garantiza |
| :-- | :-- | :-- |
| Regla `.claude/rules/documentation-governance.md`, sin `paths`, de pocas líneas | Carga en cada sesión y también en cada subagente | Claude siempre sabe que los documentos gobernados solo los escribe su agente y que debe cargar el skill antes de cualquier trabajo de documentación |
| Skill `documentation-governance` (el único) | Carga al empezar trabajo de documentación | El registro completo: agentes, situaciones, entradas obligatorias y vía de lanzamiento |
| Hook `PreToolUse` sobre `Write\|Edit` en rutas gobernadas | Determinista | Deniega la escritura directa desde la sesión principal, con el motivo "lánzalo por `documentation-governance`". Aunque la regla se ignore, el archivo no se escribe fuera del flujo |

Así el registro detallado no cuesta tokens en cada petición ni en cada subagente, y la obligación no depende de que Claude se acuerde.

## Qué modalidad para qué, según la documentación

`agents` → Choose an approach, y `workflows` → When to use a workflow:

| Modalidad | La doc dice usarla cuando | Aquí |
| :-- | :-- | :-- |
| Subagentes | "A side task would flood your main conversation"; el trabajo es autocontenido y solo importa el resultado | Cada escritor y el revisor |
| Workflows | "A script holds the plan instead of Claude's turn-by-turn judgment"; se quiere verificación cruzada y que la orquestación sea repetible | Escribir → revisar → corregir, como script fijo |
| Agent teams | Los trabajadores necesitan hablar entre sí y coordinarse; experimental; no aísla archivos | No aplica: cada documento es un archivo independiente con un solo dueño |
| Orquestación desde la sesión principal | Tareas con ida y vuelta, o pocas delegaciones por turno | Decide la situación con el skill y lanza; no redacta |
| Agent view, Projects | Tareas independientes de días, en segundo plano o en la nube | Fuera de alcance |

### 8. Advisor
- Un modelo igual o más capaz que Claude consulta antes de comprometerse con un enfoque, ante un error recurrente y antes de declarar terminado; recibe la conversación completa (`advisor` → When Claude consults the advisor).
- "Subagents inherit the configured advisor and apply the same pairing check against their own model" (`advisor` → Choose an advisor model). Con Fable 5.2 como principal solo se acepta Fable 5.2, pero los subagentes cuyo modelo cumple el emparejamiento sí lo usan.
- Experimental; el momento lo decide el modelo y no hay ajuste para forzarlo, solo instrucciones; cada consulta relee la transcripción sin caché (`advisor` → Cost, Impact on prompt caching).
- **Decisión:** `advisorModel: "opus"`. El contrato de cada escritor le ordena consultar al advisor antes de dar el documento por terminado. Es una segunda opinión dentro del contexto del propio escritor, no una revisión independiente: `doc-reviewer` y los hooks se mantienen.
- **Costo de la sesión:** recomendación, a tu elección con `/model`: trabajar este repo con la sesión principal en Opus (o Sonnet para rutina) con advisor, en lugar de Fable en cada turno. "Pairing a faster main model with a stronger advisor typically costs less than running the stronger model throughout".

## Arquitectura

```
Regla siempre cargada ──► skill documentation-governance ──► clasifica la situación
                                                               │
Detector (hooks) ──► cadena pendiente ─────────────────────────┤
                                                               ▼
                                          workflow documentation-chain (mapa chains.json):
                                          etapas en orden, agentes en paralelo, revisión, corrección
Hooks en settings.json: deniegan escritura directa, validan cada archivo, bloquean el cierre defectuoso
```

### Agentes (`.claude/agents/docs/`)

Modelo y esfuerzo según la convención nueva; son puntos de partida y se ajustan con evidencia de evals, como indica la guía oficial ("Run an effort sweep on your own evals").

| Agente | Absorbe | Situaciones (etapas de refactor.md) | Modelo · esfuerzo |
| :-- | :-- | :-- | :-- |
| `plugin-readme-writer` | plugin-readme | esqueleto (4), finalizar (11), actualizar (13, 18) | sonnet · high |
| `marketplace-readme-writer` | root-readme | base (3), alta, renombre o retiro (7, 19) | sonnet · high |
| `changelog-writer` | CHANGELOG, marketplace-changelog | crear (2, 4), Unreleased (12), release (13–14), yank (18) | sonnet · medium |
| `license-notice-writer` | LICENSE, NOTICE | base (3), plugin nuevo (4), terceros (6) | sonnet · medium |
| `governance-writer` | CODE_OF_CONDUCT, SECURITY, CONTRIBUTING, SUPPORT, PRIVACY | base (3), cambio de política (18) | sonnet · medium |
| `plugin-manifest-writer` | plugin.json, skill, agent | scaffolding (4), bump (13) | sonnet · medium |
| `doc-reviewer` (solo lectura, adversarial) | — | revisa contra el contrato del escritor | opus · high |

Base del esfuerzo: guía de la plataforma, Sonnet 5.5: "For agentic coding and multistep tool use, start with `medium` for well-specified tasks and move to `high` for harder or longer ones".

Contrato de cada agente: rol y archivos que gobierna → entradas obligatorias → procedimiento por situación → formato de salida (template embebido) → reglas y prohibiciones → checks que ejecuta → informe final con evidencia. Frontmatter: `model` y `effort` explícitos, `tools` mínimos, sin `Agent`, `maxTurns` como tope (el resultado llega marcado como parcial y se puede reanudar). `memory: project` solo en los escritores: la memoria activa Read, Write y Edit automáticamente (`sub-agents` → Enable persistent memory), así que `doc-reviewer` va sin memoria para seguir siendo de solo lectura.

Permisos: los subagentes en segundo plano muestran cada solicitud de permiso en la sesión principal (`sub-agents` → Tools, permissions, and results of background subagents). Para que una cadena no se detenga, se añaden a `permissions.allow` reglas precisas: escritura en las rutas gobernadas y ejecución de los scripts de `.claude/hooks/`.

Excepción: los textos MIT y Contributor Covenant quedan como archivo en `assets/` del skill y se copian con `cp`; un check compara contra el asset.

### Cadenas de eventos: qué desencadena qué, sin que tú invoques nada

Tres piezas:

**1. El mapa de cadenas, como datos** (`.claude/skills/documentation-governance/chains.json`). Una sola fuente que leen el skill, el detector y el workflow. Cada evento define etapas en orden; dentro de una etapa los agentes corren en paralelo; cada etapa recibe el resultado estructurado de la anterior.

| Evento | Cadena (→ secuencial, ∥ paralelo) |
| :-- | :-- |
| Base del repositorio | LICENSE ∥ gobernanza ∥ README del marketplace → changelog del marketplace → revisión |
| Plugin nuevo | manifest → README (esqueleto) ∥ LICENSE ∥ CHANGELOG → catálogo en README del marketplace → changelog del marketplace → revisión |
| Plugin terminado (etapa 11) | README del plugin (final) → catálogo en README del marketplace → revisión |
| Cambio de componentes | CHANGELOG (Unreleased) → README del plugin → README del marketplace solo si cambió descripción o categoría → revisión |
| Release | manifest (versión) → CHANGELOG (fecha) → README del plugin → changelog del marketplace → README del marketplace → revisión |
| Material de terceros añadido | NOTICE → sección de licencia del README → revisión |
| Renombre o retiro de plugin | manifest → README del marketplace → changelog del marketplace → README del plugin → revisión |
| Cambio de política | archivo de gobernanza → enlaces en README del marketplace → revisión |
| Revisión total | por cada plugin en paralelo: `doc-reviewer` sobre sus documentos → correcciones dentro del plugin; después, en una etapa secuencial única: README del marketplace → changelog del marketplace → revisión |

Regla de propiedad de archivos (`agents` → Choose an approach: "Do the tasks touch the same files?"): en una etapa paralela, ningún archivo tiene dos dueños. Los archivos compartidos por todos los plugins (README y changelog del marketplace) van siempre en una etapa secuencial final, con un solo agente que recibe los datos de todos. Un check valida esto sobre `chains.json` antes de aceptar cualquier cambio al mapa.

La lista sale del mapa de etapas que hicimos al inicio; en el piloto la repasamos contigo caso por caso antes de fijarla.

**2. El detector, determinista** (`.claude/hooks/docs-pending.sh`, bash + `jq`). No guarda estado: calcula desde git y los archivos qué cadenas están pendientes, con invariantes comprobables:

- Un plugin sin README, LICENSE o CHANGELOG → *plugin nuevo*.
- Componentes de un plugin cambiados y su CHANGELOG sin entrada nueva en Unreleased → *cambio de componentes*.
- `version` de `plugin.json` distinta de la última versión del CHANGELOG → *release*.
- Un plugin en `marketplace.json` que no está en el catálogo del README raíz, o al revés → *catálogo*.

Lo usan dos hooks:

- `PostToolUse` sobre `plugins/**`: avisa a Claude en el momento qué cadena quedó pendiente.
- `Stop`: si queda una cadena pendiente, devuelve `decision: "block"` con el motivo "ejecuta la cadena X para el plugin Y". Claude no puede terminar el turno con la documentación desfasada, así que la lanza solo. Se protege contra bucles con `stop_hook_active` (`hooks` → Stop decision control).

**3. El ejecutor, un único workflow guardado** (`.claude/workflows/documentation-chain`). Recibe en `args` el evento y los plugins, y ejecuta las etapas del mapa: `await` entre etapas, `parallel()` dentro de cada una, `pipeline()` por plugin. Llama a los agentes con `agentType` y exige `schema`; la etapa siguiente recibe los datos de la anterior (por ejemplo, el README del plugin devuelve descripción, categoría y versión, y el README del marketplace los usa). Tras cada cadena, `doc-reviewer` y hasta dos rondas de corrección.

Se añade `Workflow(documentation-chain)` a `permissions.allow` para que arranque sin pedir confirmación (`workflows` → Approve the plan before it runs).

Por qué script y no agentes que se hablan entre sí: la doc reserva los teams para cuando los trabajadores deben debatir; aquí el orden es fijo y conocido, y `workflows` → When to use a workflow lo asigna al script: "A workflow moves the plan into code".

Cómo te llega a ti: hablas en lenguaje natural ("añade este skill al plugin X"); Claude hace el cambio; el detector marca la cadena; el workflow la ejecuta; recibes un resumen por archivo. Si pides documentación directamente, la regla y el skill clasifican el evento y lanzan la misma cadena.

Costo: la sesión principal solo clasifica y lanza; los escritores corren en Sonnet y solo el revisor en Opus, y los resultados intermedios quedan en el script, no en el contexto principal.

### Hooks (`.claude/settings.json`; scripts en `.claude/hooks/`, bash + `jq`)

| Evento | Tipo | Hace |
| :-- | :-- | :-- |
| `PreToolUse` `Write\|Edit`, rutas gobernadas | síncrono | Deniega la escritura que no venga del agente dueño |
| `PostToolUse` `Write\|Edit`, rutas gobernadas | síncrono | Bloquea placeholders, comentarios de instrucción, encabezados ausentes |
| `SubagentStop`, por agente | síncrono | Corre los checks del contrato; si fallan, el agente continúa con el motivo |
| `PostToolUse` en `plugins/**` | síncrono | Corre el detector y avisa qué cadena quedó pendiente |
| `Stop` | síncrono | Bloquea el cierre del turno mientras haya una cadena pendiente |
| `PostToolUse`, README | `asyncRewake` | Enlaces y badges; avisa solo si falla (un hook async no puede bloquear) |

Los hooks van en `settings.json` y no en el frontmatter, porque los de un agente de proyecto exigen el diálogo de confianza y no corren en `-p`. Tipo `command`, no `agent` (experimental). Sin `onFailure: "block"`.

### Base heredada

`.claude/CLAUDE.md` mínimo que importa `@architecture/project-conventions.md`: todo agente hereda `CLAUDE.md` y las reglas (`sub-agents` → What loads at startup), y hoy el repo no tiene ninguno.

## Cambios en convenciones y configuración

- `project-conventions.md`, sección nueva **Models and effort**:
  - Executors and simple auditors run on Sonnet.
  - Adversarial reviewers, orchestrators and reviewers of critical, complex or broad work run on Opus.
  - Every project agent declares `model` and `effort`; effort is set per task, following the official recommendations for that model, and adjusted with eval evidence.
- `project-conventions.md`, sección nueva **Documentation governance**: tabla archivo → agente; nadie escribe un documento gobernado fuera de su agente.
- `.claude/settings.json`: quitar `CLAUDE_CODE_SUBAGENT_MODEL`. Efecto: un subagente sin `model`, y los integrados como `general-purpose`, pasan a correr en el modelo de la sesión (`sub-agents` → Built-in subagents, Choose a model). Por eso la convención añade: every delegation to a built-in agent passes the model for its role.
- No se deniega `SendMessage`: también sirve para reanudar subagentes (`cross-session-messaging` → Turn off cross-session messaging).

## Riesgos y mitigación

| Riesgo | Mitigación | Prueba |
| :-- | :-- | :-- |
| Un cambio deja documentos dependientes sin actualizar | Detector + hook `Stop` que bloquea el cierre | Añadir un skill a un plugin de prueba sin pedir documentación: la cadena corre sola y actualiza CHANGELOG y README |
| El detector marca una cadena que no aplica y entra en bucle | `stop_hook_active`; invariantes deterministas; una cadena ejecutada deja el invariante cumplido | Tras la cadena, el detector devuelve vacío |
| Dos agentes en paralelo sobrescriben el mismo archivo | Regla de propiedad + check sobre `chains.json`; archivos compartidos solo en etapa secuencial | Revisión total sobre dos plugins: el README del marketplace conserva las dos entradas |
| Se escribe documentación sin la gobernanza | Regla siempre cargada + hook `PreToolUse` que deniega | Pedir a la sesión principal que edite un README: denegado |
| El agente escribe sin los hechos reales | Entradas obligatorias en el contrato; `schema` en workflows; el agente lee el plugin y el diff por sí mismo | Lanzar sin un dato: lo pide, no lo inventa |
| Declara éxito con un archivo defectuoso | `PostToolUse` y `SubagentStop` síncronos | Dejar un `{{placeholder}}`: se bloquea y lo corrige |
| Quien escribe se califica a sí mismo | `doc-reviewer` en Opus, obligatorio en los workflows | Devuelve diferencias concretas |
| Texto legal alterado | Copia desde asset + comparación | `diff` sin diferencias fuera del copyright |
| Ediciones de subagentes fuera de `/rewind` | El skill exige árbol limpio o commit previo; se revierte con git | Revertir una ejecución con git |
| El contrato corre como teammate | Ver decisión pendiente | `/tasks` muestra subagente |
| El control falla y frena todo | Sin `onFailure: "block"` | Forzar un fallo del script: no bloquea |
| Agente fuera de su ámbito | `tools` mínimos + `PreToolUse` por dueño | Escritor de README sobre un changelog: denegado |
| Errores repetidos entre sesiones | `memory: project` | Segunda ejecución no repite un error corregido |
| Campo mal escrito ignorado | `claude --debug`, buscar `does not recognize or apply`; `claude plugin validate .claude/agents`; `/doctor` para nombres duplicados | Sin coincidencias ni errores |
| Una cadena se detiene pidiendo permiso | Reglas `permissions.allow` precisas | La cadena del piloto termina sin ninguna solicitud |
| El revisor escribe archivos | Sin `memory`, `tools: Read, Grep, Glob` | `/tasks` y el intento de escritura: denegado |
| Modelo o esfuerzo distinto al declarado | `/tasks` muestra modelo y esfuerzo por agente | Coincide con la tabla |

Sin confirmar en la documentación; se comprueba en el piloto antes de replicar: que el advisor esté disponible en sesión cloud y lo hereden los agentes lanzados por un workflow (la línea `Advising` en la transcripción del agente); que la entrada de `PreToolUse` distinga sesión principal de agente, y que `agentType` aplique el frontmatter completo (`model`, `effort`, `tools`, `memory`) dentro de un workflow. Si alguna falla, te lo reporto con la alternativa antes de seguir.

## Decisión pendiente

**Agent teams.** `.claude/settings.json` tiene `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Con eso, un subagente al que Claude dé nombre se lanza como teammate, y un teammate in-process recibe el contrato como instrucciones añadidas, no como system prompt (`agent-teams` → Use subagent definitions for teammates). Recomiendo quitarlo del repo y activarlo por sesión cuando quieras un equipo. Si prefieres dejarlo, lo pruebo en el piloto y te muestro el efecto.

**"Carga siempre", alternativa más estricta.** Agente de sesión en `"agent"` de `.claude/settings.json` con `initialPrompt: /documentation-governance`, que carga el skill como primer turno de cada sesión (`sub-agents` → Frontmatter reference, Invoke subagents explicitly). Cuesta un turno automático por sesión y, si el agente tiene cuerpo, reemplaza el system prompt de Claude Code. Recomiendo la regla siempre cargada más el hook; esta queda a tu elección.

**Auditoría programada (opcional).** Una tarea programada en la nube que corra el detector y `doc-reviewer` en solo lectura y te reporte desfases (`agents`: "A cloud scheduled task runs a session on a schedule in the cloud"). Consume uso en cada ejecución; se decide después del piloto.

Descartados con motivo: `/batch` (no fija nuestros agentes ni la revisión), Projects (sus hilos cloud no cargan los skills del repo) y agent view (tareas independientes que despachas tú).

Fuera de este pase: `evals-ci` (los evals son decisión tuya); se guarda en `.claude/architecture/`.

## Implementación

0. Convenciones (dos secciones nuevas), `.claude/CLAUDE.md`, quitar la variable de modelo, `advisorModel: "opus"`.
1. **Piloto completo, una cadena de punta a punta** ("cambio de componentes"): regla, skill `documentation-governance`, `chains.json` con esa cadena, `changelog-writer`, `plugin-readme-writer`, `doc-reviewer`, detector, hooks y workflow `documentation-chain`. Fuentes fechadas → `.claude/memory/`. Se corren todas las pruebas, en nube y en la CLI de macOS. Repasamos contigo la lista de cadenas. Lo revisas antes de replicar.
2. Los otros cuatro agentes; se completan `chains.json`, los invariantes del detector y el registro del skill; se eliminan las menciones a scripts inexistentes.
3. Cadena "revisión total", probada en un plugin antes de los 22.
4. Borrar `.claude/templates/` y `.claude/references/`; actualizar el Apéndice E de `refactor.md`.

Se construye con `skill-creator`, `hook-engineering`, `instruction-engineering`, `plugin-engineering` y `/workflow-authoring`. Commits por tema; sin push hasta que lo autorices.
