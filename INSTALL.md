# Установка / Installation

Обычная установка включает Палыча для всех ответов Codex или Claude Code:
правила добавляются в общие инструкции агента. Отдельный вызов не нужен.
Нужны Python 3.9+, Git и macOS/Linux.

The default installation enables Palych for all Codex or Claude Code replies by
adding the rules to the agent's global instructions. No invocation is needed.
Requires Python 3.9+, Git and macOS/Linux.

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

## Вариант с плагином / Plugin alternative

Плагин использует хук начала разговора (`SessionStart`) и сохраняет состояние
режима отдельно. В новой установке режим включён по умолчанию. Старое сохранённое
выключение при обновлении сохраняется. Правила восстанавливаются после сжатия,
если хост отправляет событие `compact`.

A plugin uses a SessionStart hook and stores mode state separately. A fresh
installation defaults to on; existing saved off states survive updates.
It restores rules after compaction when the host delivers the compact event.

Сборка и команды режима — в [adapters/README.md](adapters/README.md).
Выбери один способ: общие инструкции **или** плагин. Их одновременная загрузка
может добавить правила дважды и создать разные состояния режима.

See [adapters/README.md](adapters/README.md) for building and controls.
Choose global instructions **or** the plugin to avoid duplicate rules and
conflicting mode state.

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
