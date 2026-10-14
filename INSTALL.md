# Установка / Installation

Обычная установка включает Палыча для всех ответов Codex или Claude Code:
правила добавляются в общие инструкции агента. Отдельный вызов не нужен.
Нужны Python 3.9+, Git и macOS/Linux.

The default installation enables Palych for all Codex or Claude Code replies by
adding the rules to the agent's global instructions. No invocation is needed.
Requires Python 3.9+, Git and macOS/Linux.

Для каждого агента выбери один способ: общие инструкции **или** плагин
(раздел «Плагины» ниже). Если поставить оба, правила загрузятся дважды,
а состояния режима могут разойтись.

Choose one route per host: global instructions **or** a plugin (see Plugins
below). Installing both loads the rules twice, and their mode states can conflict.

## Инструкция для агента / Agent instructions

1. Определи используемый агент и его каталог настроек. Если выбор нельзя понять
   из контекста, уточни Codex или Claude Code. Соблюдай действующие правила
   пользователя об установке: если общие инструкции управляются другим
   репозиторием или установщиком, внеси блок через этот источник.
2. Получи репозиторий и проверь `SKILL.md` и `scripts/install.py` до запуска.
   Не запускай код из непроверенного источника. Запомни установленный commit.
3. Выполни подходящую команду `install` ниже. Затем `check`: она проверяет
   наличие актуальных правил, а не качество ответов модели.
4. Сообщи, какой файл изменён и где резервная копия. Попроси начать новый
   разговор. Если доступна проверка в хосте, проверь загрузку правил с первого
   сообщения и после сжатия контекста. Не заявляй об этой проверке без результата.

Identify the host and configuration directory. Follow the user's existing
installation workflow, especially for generated or centrally managed instructions.
Review the source, record the installed commit, run `install`, then `check`.
Report the changed file and backup path. Start a new conversation. Verify actual
host loading and compaction when possible; file checks alone do not establish it.

## Команды / Commands

```sh
git clone https://github.com/ponomr/palych.git
cd palych
```

**Codex:**

```sh
python3 scripts/install.py install --host codex
python3 scripts/install.py check --host codex
```

**Claude Code:**

```sh
python3 scripts/install.py install --host claude-code
python3 scripts/install.py check --host claude-code
```

Codex: `$CODEX_HOME/AGENTS.md`, по умолчанию `~/.codex/AGENTS.md`.
Если `AGENTS.override.md` уже существует, блок добавляется туда: Codex выбирает
этот файл вместо базового. Claude Code: `$CLAUDE_CONFIG_DIR/CLAUDE.md`,
по умолчанию `~/.claude/CLAUDE.md`. Другой каталог можно задать через
`--config-dir /path/to/config`.

Codex uses `$CODEX_HOME/AGENTS.md` (default `~/.codex/AGENTS.md`), or an existing
`AGENTS.override.md`, which takes precedence. Claude Code uses
`$CLAUDE_CONFIG_DIR/CLAUDE.md` (default `~/.claude/CLAUDE.md`).
Use `--config-dir /path/to/config` to select another directory.

Установщик добавляет один блок из `SKILL.md`. Остальное содержимое файла
сохраняется. Перед изменением существующего файла создаётся резервная копия
в `.palych-backups/` рядом с ним. Повторная установка не дублирует блок.
Если блок изменён вручную или файл связан с другим файлом, установщик
останавливается, чтобы сохранить эти изменения. Он не меняет разрешения
агента, настройки моделей или другие скиллы и не обращается к сети.

The installer inserts one block generated from `SKILL.md`, preserving other
content. It backs up an existing file under `.palych-backups/` beside it.
Repeated installation does not duplicate the block. Edited blocks and linked
files need review through their managing workflow. The installer does not change
agent permissions, model settings or other skills, and makes no network requests.

## Обновление / Update

Обнови чистый checkout репозитория через обычный Git-процесс и повтори `install`
и `check`. Сохрани собственные изменения перед обновлением. Затем начни новый
разговор. Генерируемый блок обновляется из единственного источника — `SKILL.md`.

Update a clean checkout through your normal Git workflow, preserving local edits,
then repeat `install` and `check`. Start a new conversation. `SKILL.md` is the
single source for the generated block.

## Отключение и удаление / Disable and remove

«Отключи Палыча» / “Turn off palych” — выключить в текущем разговоре.
Это не удаляет общие инструкции: в новом разговоре Палыч снова включён.
«Включи Палыча» / “Enable palych” — вернуть в текущем разговоре.

Чтобы выключить постоянный режим, удали только блок Палыча:

To disable it for future conversations, remove only Palych's managed block:

```sh
python3 scripts/install.py uninstall --host codex
# Or:
python3 scripts/install.py uninstall --host claude-code
```

Начни новый разговор. Остальные инструкции и резервные копии сохраняются.
Если пользователь просит постоянное отключение, агент выполняет `uninstall`
через разрешённый способ управления общими инструкциями, а не обещает
постоянство по одной фразе в чате.

Start a new conversation. Other instructions and backups are preserved. A request
to disable Palych permanently requires removing the block through the authorized
configuration workflow, rather than promising persistence from a chat reply alone.

## Плагины и другие агенты / Plugins and other hosts

Готовые пакеты лежат в `packages/` и собираются из `SKILL.md`. Если блок
Палыча уже есть в общих инструкциях, сначала удали его (`uninstall` выше).

Ready-made packages live in `packages/` and are generated from `SKILL.md`. If
Palych's block is already in the global instructions, remove it first
(`uninstall` above).

**Claude Code** (плагин с хуком / plugin with hooks):

```sh
claude plugin marketplace add ponomr/palych
claude plugin install palych@palych
```

Обновление / Update:

```sh
claude plugin marketplace update palych
claude plugin update palych@palych
```

**Codex** (плагин с хуком / plugin with hooks):

```sh
codex plugin marketplace add ponomr/palych
codex plugin add palych@palych
```

Или установи Palych в каталоге плагинов приложения Codex.
Or install Palych from the Codex app's plugin directory.

**Обязательный шаг: разреши хук.** Codex не запускает хуки плагина, пока
пользователь их не проверил и не разрешил. Без этого плагин числится включённым,
но правила не загружаются, и Codex не сообщает об ошибке. После установки открой
в Codex CLI команду `/hooks`, найди хук Палыча и разреши его. Codex запоминает
разрешение для текущего определения хука: если после обновления он снова
попросит открыть `/hooks`, разреши хук ещё раз. Затем начни новый разговор
и проверь, что правила загружены.

**Required: trust the hook.** Codex does not run plugin hooks until the user
reviews and trusts them. Until then the plugin is listed as enabled but loads
no rules, and Codex reports no error. After installing, open `/hooks` in the
Codex CLI, find Palych's hook and trust it. Codex records trust for the current
hook definition: if it asks you to open `/hooks` again after an update, trust
the hook again. Then start a new conversation and check that the rules are loaded.

Обновление: обнови каталог и поставь плагин заново. Update: refresh the
marketplace and add the plugin again:

```sh
codex plugin marketplace upgrade palych
codex plugin add palych@palych
```

Плагины Claude Code и Codex используют хук начала разговора (`SessionStart`)
и хранят состояние режима отдельно. В новой установке режим включён. Сохранённое
выключение переживает обновление. После сжатия правила восстанавливаются, если
хост отправляет событие `compact`. Команды режима — в
[adapters/README.md](adapters/README.md).

The Claude Code and Codex plugins use a SessionStart hook and store mode state
separately. A fresh installation defaults to on; a saved off state survives
updates. Rules return after compaction when the host delivers the compact event.
See [adapters/README.md](adapters/README.md) for mode controls.

**Hermes:**

```sh
hermes skills install ponomr/palych/packages/hermes/palych
```

Hermes загружает скилл с начала разговора, если запустить его с флагом
(проверено на v0.16.0 и v0.22.0):
Hermes preloads the skill when started with the flag (checked on v0.16.0 and
v0.22.0):

```sh
hermes -s palych
```

В Hermes v0.22.0 есть настройка `skills.auto_load` в `config.yaml` профиля: она
загружает перечисленные скиллы в каждый новый разговор. Мы видели её в коде
Hermes, но с Палычем не проверяли. В v0.16.0 её нет.
Hermes v0.22.0 has a `skills.auto_load` list in the profile's `config.yaml` that
loads the listed skills into every new session. It was seen in the Hermes source
but not tested with Palych; v0.16.0 lacks it:

```yaml
skills:
  auto_load:
    - palych
```

Скилл, поставленный из GitHub, удаляется командой `hermes skills uninstall palych`.
A skill installed from GitHub is removed with `hermes skills uninstall palych`.

**Cursor:** пакет `packages/cursor` содержит правило `rules/palych.mdc` с
`alwaysApply: true`. До публикации в каталоге Cursor скопируй этот файл в
`.cursor/rules/` проекта. The `packages/cursor` package holds an always-applied
rule; until it is listed in Cursor's marketplace, copy `rules/palych.mdc` into a
project's `.cursor/rules/`.

**Другие агенты / Other agents:**

```sh
npx skills add ponomr/palych/packages/hermes/palych
```

Команда ставит только папку скилла (`SKILL.md`, примеры, лицензию) как обычный
скилл. Агент вызывает его по описанию, а не в каждом ответе. Короткая форма
`npx skills add ponomr/palych` копирует весь репозиторий, включая оценки и
документацию. Удаление — `npx skills remove palych`.

It installs only the skill folder (`SKILL.md`, examples, license) as a regular
skill that the agent invokes by description, not in every reply. The short form
`npx skills add ponomr/palych` copies the whole repository, including evaluations
and docs. Remove it with `npx skills remove palych`.

В Hermes и Cursor нет хуков Палыча: «Отключи Палыча» действует только
в текущем разговоре. Постоянно отключить — удалить скилл или правило.
Hermes and Cursor have no Palych hooks: “Turn off palych” lasts only
for the current conversation. Remove the skill or rule to disable it
permanently.

## Проверка в агенте / Host verification

В новом разговоре задай обычный вопрос без имени Палыча. Проверь, что агент
видит общие правила Палыча. Затем отключи режим, сожми контекст средствами хоста
и проверь, что выключение сохранено в этом разговоре. В новом разговоре режим
должен снова включиться. Для плагина проверь также доставленный контекст хука.
Стиль одного ответа сам по себе не доказывает загрузку правил.

In a new conversation, ask an ordinary question without mentioning Palych and
check that its global rules are loaded. Turn it off, compact the conversation
and check that off is retained. A new conversation should default to on again.
For plugins, inspect delivered hook context as well. Reply style alone does not
prove that the rules loaded.

Механизм общих инструкций описан в документации
[Codex](https://learn.chatgpt.com/docs/agent-configuration/agents-md) и
[Claude Code](https://code.claude.com/docs/en/memory).
[Проверено и не проверено в Палыче](docs/STATUS.md).
