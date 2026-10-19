# Переключатель Палыча / Palych toggle

Мод для Claude Code: справа над полем ввода стоят надпись «Палыч» и
переключатель, который включает и выключает режим в текущем разговоре.
В приложении это зелёная таблетка в стиле iOS в цветах темы приложения;
в терминале — кнопка `●` (вкл) или `○` (выкл).

A Claude Code mod: the label «Палыч» and a switch sit at the right above the
prompt and turn the mode on or off for the current conversation. The desktop
app draws an iOS-style pill in the app theme's colours; the terminal draws a
`●` (on) or `○` (off) button.

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

Переключатель и определение темы взяты из переключателя auto compact мода
usage-quota (MIT, © 2026 Anant Raghunath). Чтобы узнать тему, мод раз в 2 с
проверяет `userThemeMode` в настройках приложения Claude
(`~/Library/Application Support/Claude/config.json` или
`%APPDATA%/Claude/config.json`), а для «system» спрашивает ОС
(`defaults read -g AppleInterfaceStyle` или реестр Windows).

The switch and the theme detection come from the usage-quota mod's auto
compact switch (MIT, © 2026 Anant Raghunath). To learn the theme, the mod
checks `userThemeMode` in the Claude app's settings every 2 s and, for
"system", asks the OS.

## Ограничения / Limits

- Новый разговор начинается с «Палыч вкл»; состояние не сохраняется между
  разговорами. / A new conversation starts on; the state is per conversation.
- Другие формулировки выключения модель поймёт, но переключатель о них не
  узнает. / Other wording reaches the model but does not move the switch.
- Пометка — инструкция модели, а не удаление правил из контекста. В живой
  сессии приложения видно, что пометка доходит до модели; стиль ответов
  систематически не оценивался. / The note is an instruction to the model, not
  removal of the rules from context. A live desktop session shows the note
  reaching the model; reply style was not evaluated systematically.
- Сдвиг на целые клетки нельзя сделать тоньше, поэтому таблетка нарисована на
  1 pt ниже внутри SVG, к строчным буквам. Подсветка при наведении остаётся по
  центру клетки. / Layout moves only by whole cells, so the pill is drawn 1 pt
  lower inside its SVG, level with the lowercase letters; the hover light stays
  centred in the cell.
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
