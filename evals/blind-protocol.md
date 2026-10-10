# Слепое сравнение / Masked paired evaluation

Этот протокол проверяет редакторские признаки понятности. Оценка модели не
доказывает, что читатели лучше поняли ответ. Проверяйте понимание отдельно по
[протоколу для читателей](reader-check.md).

## Подготовка ответов

Используйте [prompts.json](prompts.json): для полного запуска нужны все задания,
каждое в трёх отдельных повторениях для двух условий. Это 60 пар для текущего
набора из 20 заданий. При расширении набора число пар увеличится.

1. До генерации сохраните общие инструкции, точную версию модели, доступные
   настройки и разрешённые инструменты. Зафиксируйте хеши общих инструкций,
   `SKILL.md` и файла заданий. Записывайте только наблюдаемые сведения.
2. Для каждой пары начните два новых разговора с одинаковыми общими инструкциями
   и настройками. В одном добавьте `SKILL.md`. Затем задайте один и тот же вопрос.
   Генераторам передавайте только их инструкции и вопрос: критерии, примеры
   правильных ответов и ответы другого условия остаются у организатора.
3. Сохраняйте исходные ответы без редактирования, с условием и номером повторения.
   Если разговоры использовали общий контекст, укажите это как ограничение.
   Если модель или настройки недоступны, назовите неизвестные сведения и
   используйте явно обозначенный исследовательский режим, описанный ниже.
   Полный запуск и обычный пробный запуск требуют наблюдаемые настройки.
4. Сохраните `manifest.json` и `responses.json` вне публичного пакета. Не включайте
   в них личные данные. Все настройки и инструменты должны совпадать между
   условиями; добавление скилла — единственное запланированное различие.

`manifest.json` содержит:

```json
{
  "model": "observed-model-version",
  "settings": {"temperature": 0},
  "tools": [],
  "base_instructions_sha256": "actual 64-character lowercase SHA-256",
  "skill_sha256": "actual 64-character lowercase SHA-256",
  "prompts_sha256": "actual 64-character lowercase SHA-256",
  "verified": true,
  "verification_note": "How the model, settings and base instructions were observed"
}
```

Это схема, не готовый манифест: замените значения реально наблюдаемыми данными.
Если параметр не используется, не придумывайте его. Совпадение хешей скилла и
заданий проверяет инструмент; достоверность сведений о генерации и хеша общих
инструкций проверяет организатор. `verified: true` — его явное подтверждение.

`responses.json` — массив объектов. Каждый объект имеет ровно эти поля:

```json
{
  "case_id": "ru-short",
  "repetition": 1,
  "condition": "baseline",
  "response": "Unedited reply",
  "metadata": {
    "model": "observed-model-version",
    "settings": {"temperature": 0},
    "tools": [],
    "base_instructions_sha256": "actual 64-character lowercase SHA-256"
  }
}
```

Для второй версии условие — `skill`. Номера повторений: 1, 2, 3.
`metadata` должна в точности совпадать с общими полями манифеста. Хеш скилла
остаётся в манифесте и не считается общей инструкцией базового условия.

## Оценка без названий условий

Все пути ниже относятся к отдельной рабочей папке проверки. Команды запускаются
из корня пакета и используют только стандартную библиотеку Python 3.

```sh
python3 evals/blind_eval.py prepare --responses run/responses.json --manifest run/manifest.json --prompts evals/prompts.json --skill SKILL.md --output run/masked
```

Инструмент проверит полноту пар и создаст:

- `packets.json`: вопросы, ответы A/B и критерии. Порядок пар случайный; первое
  место между условиями распределяется поровну или с разницей в одну пару.
- `judgments-template.json`: форму для оценщика.
- `private-mapping.json`: соответствие A/B исходным условиям и сведения о запуске.

Оценщику передавайте только первые два файла. Лучше использовать нового
оценщика, который не видел генерацию и ожидаемого победителя. Внешние платные
сервисы инструмент не вызывает. При оценке той же моделью укажите это
ограничение. Маскировка убирает явные метки, но узнаваемый стиль ответа может
раскрыть условие; это также ограничивает слепой режим.

Сохраните заполненную форму отдельно как `judgments.json`. Сначала проверьте
сохранение смысла каждого ответа, затем пять редакторских признаков по шкале
0–2 с описанными уровнями. Для неприменимого признака используйте `null` и
объясните причину. Итоговую среднюю «понятность» из этих чисел не вычисляйте:
шкала помогает назвать конкретный дефект, а не измеряет понимание читателя.

Оценщик выбирает A, B или ничью и объясняет выбор. Ответ с ошибкой смысла не
может победить ответ без такой ошибки. Если оба ответа искажают смысл, выберите
ничью и отметьте обе ошибки. Не исправляйте ответ при оценке.

```sh
python3 evals/blind_eval.py lock --packets run/masked/packets.json --judgments run/judgments.json --output run/judgments-lock.json
python3 evals/blind_eval.py score --packets run/masked/packets.json --judgments run/judgments.json --mapping run/masked/private-mapping.json --lock run/judgments-lock.json --output run/results.json
```

Только после фиксации оценки разрешено открыть соответствие условий. Изменение
оценок или пакета после `lock` остановит обработку. Это защита от случайного
изменения, а не криптографическое доказательство независимости: организатор
должен хранить карту отдельно и вести историю исходных файлов.

Результат содержит победы каждого условия, ничьи и ошибки смысла по всем парам,
по заданиям и по повторениям. «Победа в задании» означает больше побед в его
повторениях, чем у второго условия; равное число даёт ничью. Ошибка смысла
в версии со скиллом при правильной базовой версии отмечается отдельно как
регрессия. Не скрывайте такую ошибку за большинством голосов.

Для небольшого пробного запуска разрешены выбранные задания и другое число
повторений. Добавьте `--pilot --repetitions 1 --limitation "Конкретные ограничения"`.
Пробный запуск остаётся пробным; его результат нельзя описывать как полный
контролируемый эксперимент. Новый запуск всегда сохраняйте в новой папке.

## Исследовательский режим с недоступными параметрами

Когда встроенная среда позволяет наследовать одну конфигурацию, но не показывает
версию модели или параметры генерации, добавьте **оба** флага `--pilot
--exploratory`. Это редакторская исследовательская проверка, а не контролируемое
сравнение. По-прежнему обязательны точные хеши скилла и заданий, совпадающие
наблюдаемые условия и конкретное ограничение `--limitation`. Если полный набор
унаследованных общих инструкций недоступен, `base_instructions_sha256` тоже
может быть `null` только в этом режиме. Не заменяйте его хешем предполагаемой
инструкции или доступной части, выдавая эту часть за весь набор.

Запишите недоступное значение как JSON `null`, а не придуманный идентификатор
или строку «unknown». `model` может быть `null`; `settings` может быть целиком
`null` или объектом с отдельными недоступными значениями, например:

```json
{
  "model": null,
  "settings": {"sampling": null, "seed": null, "context_mode": "batched"},
  "base_instructions_sha256": null,
  "observed_host_configuration": "Both conditions inherit the same host configuration; model identifier and sampling are not exposed; cases share a context."
}
```

Эти поля дополняют остальные обязательные поля манифеста. `verified: true`
подтверждает наблюдаемые сведения и хеши; неизвестные параметры остаются
неподтверждёнными. В `metadata` **каждого** ответа повторите те же `model`,
`settings`, `tools`, `base_instructions_sha256` и `observed_host_configuration`.
Несимметричные неизвестные значения и различия наблюдаемых параметров будут
отклонены. Допуск `null` не означает, что скрытые параметры действительно
совпадали: это ограничение сохраняется в результате.

Если служебные запросы генераторам близки по содержанию, но различаются путями
к файлам, формулировками загрузки условий или другими деталями, опишите эти
различия. Недоступные общие инструкции и различия служебных запросов — отдельные
ограничения исследовательской проверки; сходство видимой конфигурации их не
устраняет. Сохраняйте доступные запросы и их хеши отдельно, с точным названием
проверенной части, без утверждения о совпадении всего скрытого контекста.

```sh
python3 evals/blind_eval.py prepare --responses run/responses.json --manifest run/manifest.json --prompts evals/prompts.json --skill SKILL.md --output run/masked --pilot --exploratory --repetitions 3 --limitation "Batched native contexts; exact model, sampling and seed not exposed; repetitions are not independent statistical samples."
```

Маскировка, фиксация оценок и проверка ошибок смысла работают так же. В итоговом
файле будут явные поля `exploratory`, `unknown_generation_fields` и тип проверки
`exploratory editorial pilot`, а также ограничения. Их нужно сохранять при
публикации выводов. Нельзя объединять такой запуск с полным контролируемым
сравнением без отдельного обозначения.

## English notes

Generate matched replies in fresh conversations with observed identical model,
settings, tools and base instructions. Add only `SKILL.md` in the skill condition;
keep rubrics, reference answers and paired responses away from both generators.
The default run requires every supplied case and three repetitions. An explicit
pilot may use fewer cases or repetitions. An ordinary pilot still requires
verified metadata. With both `--pilot --exploratory`, unavailable model/sampling
fields and an inaccessible complete base-instruction hash may be `null`; the
skill and prompt hashes must always match the actual files. Disclose differences
in generation wrappers, including artifact paths; do not hash a guessed brief
and label it the complete base. Record identical observed host configuration in every
reply metadata object and mandatory limitations. Hidden settings remain
unverified, so this mode must never be called a controlled comparison.

Give an independent assessor only the masked packets and judgment template.
Lock judgments before opening the condition mapping. Semantic preservation
precedes clarity: a failing reply cannot beat a passing one. Report ties and
regressions, observed settings, tested hashes and limitations. Repeated judgments
from one model remain editorial evidence; they do not establish a human
comprehension gain or independent statistical samples.
