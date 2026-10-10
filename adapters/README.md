# Сохранение режима / Persistent mode

Основной `SKILL.md` самодостаточен. Этот необязательный адаптер нужен, когда
хост может запускать локальные хуки (команды при событиях разговора).
Сборщик создаёт отдельный плагин для Codex или Claude Code из того же источника.
Он ничего не устанавливает и не меняет настройки агента. Поддерживаемые ОС адаптера — macOS и Linux; нужен Python 3.9+;
сторонних библиотек и сетевых запросов нет.

The standalone `SKILL.md` works without this adapter. The optional builder
creates a separate local plugin for Codex or Claude Code from the same source.
It does not install anything or modify host settings. The adapter supports macOS and Linux and requires Python 3.9+,
with no third-party packages or network requests.

## Сборка / Build

Из папки исходного пакета (в собранном плагине сборщика нет).
From the source package directory (the built plugin does not contain the builder):

```sh
python3 scripts/build_plugin.py --host codex --output ./dist/palych-codex
python3 scripts/build_plugin.py --host claude-code --output ./dist/palych-claude
```

Путь вывода должен быть новым: сборщик не перезаписывает существующий каталог.
Для Claude Code собранную папку можно передать в `claude --plugin-dir`.
В Codex добавьте собранный плагин способом, поддерживаемым вашей версией,
и проверьте доверие к его хукам в интерфейсе управления хуками. Новая установка включает режим по умолчанию, когда хост запускает разрешённый
хук. Старое сохранённое выключение при обновлении остаётся в силе.

Choose a new output path; the builder refuses to overwrite an existing folder.
Claude Code can load the built folder with `claude --plugin-dir`. In Codex, add
the built plugin through the local plugin mechanism supported by your version
and review/trust its hooks. A fresh installation defaults to on once the host runs its trusted hook.
Existing saved off states survive updates; installing does not grant hook trust. Check your host's current documentation before installation.

В новой установке отдельная команда включения не нужна.
A fresh installation needs no activation command.

## Управление / Controls

Отправьте отдельным сообщением одну из фраз. Английские варианты тоже работают.
Точка в конце необязательна. Цитаты, код и фразы внутри длинного сообщения
не переключают сохранённый режим автоматически.

Send one of these as a whole message. A final period is optional. Quoted text,
code and phrases embedded in a longer message do not automatically change state.

| Русский | English | Действие / Effect |
|---|---|---|
| Включи Палыча для этого разговора. | Enable palych for this conversation. | Включить здесь / Enable this session |
| Отключи Палыча. | Turn off palych. | Выключить здесь / Disable this session |
| Включи Палыча всегда. | Enable palych always. | Включить здесь и по умолчанию в новых разговорах / Enable here and by default in new sessions |
| Отключи постоянное включение Палыча. | Disable palych always-on. | Выключить здесь и отменить умолчание для новых разговоров / Disable here and the default for new sessions |

Сохранённое выключение в отдельном разговоре важнее общего флага «всегда».
Отмена общего флага не меняет ранее включённые другие разговоры. Режим
не переносится между Codex и Claude Code или компьютерами автоматически.
Произвольную просьбу о включении/выключении агент может сохранить через помощник,
который указан в доверенных данных хука. Если помощник недоступен, изменение
действует в текущем контексте; постоянство нельзя обещать.

A session's saved off state overrides the always-on default. Turning the default
off leaves other explicitly enabled sessions unchanged. State is separate per
host and computer. For a differently worded explicit request, the agent can use
the helper named in trusted hook metadata. If that tool call is unavailable, the
request applies in current context but persistence cannot be promised.

## Что сохраняется / Stored state

`~/.local/state/palych/<host>/` содержит общий булев флаг и состояния
разговоров и хеши последнего переданного ядра в одном файле `state.json`;
ключи разговоров — хеши идентификаторов. Тексты запросов, ответы,
журналы и ключи не сохраняются. Общий флаг и состояние разговора записываются атомарно вместе; блокировка
не позволяет параллельным разговорам потерять изменения друг друга. Повреждённое состояние
не перезаписывается: помощник возвращает ошибку, которую нужно разобрать.

`~/.local/state/palych/<host>/` contains a Boolean default and per-session
Boolean overrides and hashes of the last emitted core, together in `state.json`.
Session keys are hashes of session IDs. No prompts, replies,
transcripts or credentials are stored. The default and session override commit atomically together; a lock protects
concurrent session updates. Malformed state is
preserved and reported as an error instead of being silently replaced.

## События и ограничения / Events and limits

`SessionStart` восстанавливает актуальный режим при `startup`, `resume`, `clear`,
`compact` и `fork`, если хост присылает событие. При включённом режиме хук всегда
передаёт весь основной скилл; при выключенном — явное выключение.
`UserPromptSubmit` при первом включении, включении после выключения или изменении
ядра передаёт полный скилл. Повторное включение в том же контексте передаёт
короткое подтверждение. Обычные сообщения ничего не добавляют и не меняют.
Хуки не разрешают и не запрещают рабочие команды агента.

Данные `saved: true` вместе с режимом подтверждают сохранение текущей управляющей
просьбы: агенту не нужно снова вызывать помощник. Для другой явной просьбы агент
использует переданные аргументы помощника. Старое подтверждение не подтверждает
новую просьбу. Флаг и хеш переданного ядра записываются атомарно вместе.

`SessionStart` restores the current mode on startup, resume, clear, compact and
fork when delivered by the host. An active mode always emits the full core;
an off mode emits explicit off. `UserPromptSubmit` emits the full core on first
activation, reactivation or changed core. Repeated activation in the same context
emits a short acknowledgement. Ordinary messages neither inject nor mutate state.
Hooks neither authorize nor block work commands.

`saved: true` with the mode acknowledges the current control request; the agent
need not call the helper again. Another explicit request uses the supplied argv.
An old acknowledgement does not save a new request. Mode and core-emission hash
commit atomically together.

Хеш означает, что хук сформировал контекст, а не что модель получила и запомнила
его. Отсутствие события `SessionStart` при сбросе контекста нарушает предпосылку
устранения повторов. Поэтому адаптер нельзя считать проверенным в хосте только
по локальным тестам. Не устанавливайте одновременно отдельный скилл и его плагин
для одного режима без проверки: хост может добавить ядро двумя способами.

The hash records hook emission, not model delivery or retention. Deduplication
assumes the host sends `SessionStart` after context resets. Local fixtures cannot
verify that contract. Avoid loading both the standalone skill and its plugin for
the same mode without checking whether the host injects the core twice.

Проверки с подставленными событиями подтверждают работу помощника и сохранение
состояния. Они не подтверждают, что конкретная версия приложения запустила
хук после настоящего сжатия. Для такой проверки: включить режим, вызвать
сжатие средствами хоста, проверить полученный `SessionStart` и ответ; затем
выключить режим и повторить сжатие, в том числе при включённом общем флаге.
Не угадывайте состояние по тому, насколько красив ответ.

Fixture events verify the helper and stored state, not the host's delivery after
real compaction. For an integration check, enable the mode, trigger host
compaction, inspect the delivered SessionStart context and the reply, then
disable and repeat, including with always-on enabled. Reply style alone is not
proof of activation. This package has not been installed into a live host as
part of the development tests.

Sources: [Codex hooks](https://learn.chatgpt.com/docs/hooks),
[Claude Code hooks](https://code.claude.com/docs/en/hooks).
