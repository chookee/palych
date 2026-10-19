# Переключатель Палыча / Palych toggle

Мод для Claude Code: строка над полем ввода показывает «Палыч вкл» или
«Палыч выкл» и кнопку, которая переключает режим в текущем разговоре.

A Claude Code mod: a row above the prompt shows «Палыч вкл» or «Палыч выкл»
and a button that switches the mode for the current conversation.

## Как работает / How it works

Мод рассчитан на установку Палыча через общие инструкции
(`scripts/install.py install --host claude-code`). Он не меняет файлы и
настройки. Пока переключатель выключен, к каждому сообщению пользователя
добавляется скрытая для пользователя пометка: Палыч выключен, это явная
просьба пользователя. Правила Палыча уже требуют исполнять такую просьбу.
После включения следующее сообщение один раз получает пометку о включении.

The mod targets the global-instructions installation. It edits no files or
settings. While the switch is off, every user message carries a note the user
does not see: Palych is off at the user's explicit request, which Palych's
rules already honour. Switching it back on adds a one-time note to the next
message.

Фразы управления из `adapters/README.md`, отправленные отдельным сообщением
(«Отключи Палыча», “Turn off palych”), двигают переключатель тоже.

The control phrases from `adapters/README.md`, sent as a whole message, move
the switch too.

## Ограничения / Limits

- Новый разговор начинается с «Палыч вкл»; состояние не сохраняется между
  разговорами. / A new conversation starts on; the state is per conversation.
- Другие формулировки выключения модель поймёт, но переключатель о них не
  узнает. / Other wording reaches the model but does not move the switch.
- Пометка — инструкция модели, а не удаление правил из контекста: проверка
  стиля ответа в живой сессии не проводилась. / The note is an instruction to
  the model, not removal of the rules from context; reply style in a live
  session is not verified.
- Не проверено вместе с плагином `palych@palych`: у него своё сохранённое
  состояние. / Not tested together with the `palych@palych` plugin, which keeps
  its own saved state.

## Проверка / Checks

```sh
claude plugin validate mods/palych-toggle
claude plugin test mods/palych-toggle
```

Для пробного запуска / To try it in one session:

```sh
claude --plugin-dir mods/palych-toggle
```
