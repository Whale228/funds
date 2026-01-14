# Руководство по работе с полным универсумом акций (5000+)

## Обзор

Market Scanner поддерживает два режима работы:
1. **Быстрый режим**: Топ-100 акций (~5 минут)
2. **Полный режим**: Весь рынок США с капитализацией ≥$500M

## Методы загрузки полного универсума

### Метод 1: Готовый список (текущий - 394 акции)

```bash
python3 create_universe_manual.py
```

Создает кураторский список из ~400 крупнейших акций США.

**Плюсы**: Быстро, надежно, покрывает все основные секторы
**Минусы**: Не полный рынок (только крупные компании)

### Метод 2: Импорт из FinViz (рекомендуется для 5000+)

**Шаг 1**: Получите CSV с finviz.com

1. Зайдите на https://finviz.com/screener.ashx
2. Установите фильтры:
   - Market Cap: +Mid (over $2bln) или +Small (over $300mln)
   - Country: USA
3. Нажмите **Export** в правом нижнем углу
4. Сохраните файл как `finviz_export.csv`

**Шаг 2**: Импортируйте CSV

```bash
python3 import_from_csv.py data/finviz_export.csv
```

Скрипт:
- Автоматически найдет колонку с тикерами
- Очистит данные
- Сохранит в `data/us_stock_universe.txt`

### Метод 3: Импорт из других источников

Любой CSV файл с колонкой "Ticker" или "Symbol":

```bash
python3 import_from_csv.py path/to/your/file.csv
```

Поддерживаемые источники:
- TradingView Screener
- Yahoo Finance
- Bloomberg Export
- Custom CSV

## Запуск полного сканирования

После подготовки универсума:

```bash
python3 main_full.py
```

### Время выполнения

| Акций | Время загрузки | Общее время |
|-------|----------------|-------------|
| 500   | ~4 мин         | ~5 мин      |
| 1000  | ~8 мин         | ~10 мин     |
| 2000  | ~17 мин        | ~20 мин     |
| 5000  | ~42 мин        | ~50 мин     |

*Время указано с учетом задержки 0.5 сек между запросами*

### Запуск в фоне

Для долгих сканирований используйте:

```bash
# Вариант 1: nohup
nohup python3 main_full.py > scan.log 2>&1 &
tail -f scan.log  # Мониторинг прогресса

# Вариант 2: screen (рекомендуется)
screen -S scanner
python3 main_full.py
# Отсоединиться: Ctrl+A, затем D
# Вернуться: screen -r scanner

# Вариант 3: tmux
tmux new -s scanner
python3 main_full.py
# Отсоединиться: Ctrl+B, затем D
# Вернуться: tmux attach -t scanner
```

## Оптимизация для больших объемов

### 1. Уменьшите задержку (рискованно)

В `config.py`:
```python
REQUEST_DELAY = 0.2  # Вместо 0.5
```

⚠️ **Предупреждение**: Yahoo Finance может заблокировать при слишком частых запросах.

### 2. Пакетная обработка

Разделите универсум на части:

```python
# В main_full.py измените:
tickers = tickers[:1000]  # Первая 1000
```

Запустите несколько раз с разными диапазонами.

### 3. Кэширование

Программа автоматически сохраняет кэш:
- `data/cache_YYYYMMDD_HHMMSS.json` - все загруженные данные
- Используйте для повторного анализа без перезагрузки

## Структура выходных файлов

### results/scan_YYYYMMDD_HHMMSS.json

```json
{
  "timestamp": "20260114_143000",
  "statistics": {
    "initial_tickers": 5234,
    "data_fetched": 4891,
    "passed_filters": 3567,
    "fetch_success_rate": "93.4%",
    "filter_pass_rate": "72.9%"
  },
  "results": {
    "strong_trend": [...],
    "panic": [...],
    "euphoria": [...]
  }
}
```

## Проблемы и решения

### Проблема: "Too many requests" от Yahoo Finance

**Решение**:
1. Увеличьте `REQUEST_DELAY` до 1.0 секунды
2. Используйте VPN
3. Запускайте ночью (меньше нагрузка)

### Проблема: Программа зависает

**Решение**:
1. Проверьте интернет-соединение
2. Перезапустите с меньшим числом акций
3. Используйте кэшированные данные

### Проблема: Не хватает памяти

**Решение**:
1. Обрабатывайте по частям (по 1000 акций)
2. Отключите сохранение кэша (закомментируйте `save_cache()`)

## Пример: Полный workflow

```bash
# 1. Получите список акций
# Вариант A: Кураторский список
python3 create_universe_manual.py

# Вариант B: Импорт из FinViz (для 5000+)
# - Скачайте CSV с finviz.com
python3 import_from_csv.py data/finviz_export.csv

# 2. Проверьте количество тикеров
wc -l data/us_stock_universe.txt

# 3. Запустите сканирование
screen -S scanner
python3 main_full.py

# 4. Отсоединитесь (Ctrl+A, D) и займитесь другими делами

# 5. Проверьте прогресс позже
screen -r scanner

# 6. Посмотрите результаты
cat results/scan_*.json | jq '.summary'
```

## Автоматизация

Создайте cron job для ежедневного сканирования:

```bash
# Редактируйте crontab
crontab -e

# Добавьте строку (каждый день в 18:00 после закрытия рынка)
0 18 * * 1-5 cd /path/to/market_scanner && python3 main_full.py >> daily_scan.log 2>&1
```

## Мониторинг результатов

Создайте простой скрипт для мониторинга:

```python
# monitor.py
import json
import glob

latest = max(glob.glob('results/scan_*.json'))
with open(latest) as f:
    data = json.load(f)

print(f"Scan: {data['timestamp']}")
print(f"Strong Trend: {data['summary']['strong_trend_count']}")
print(f"Panic: {data['summary']['panic_count']}")
print(f"Euphoria: {data['summary']['euphoria_count']}")
```

## Заключение

Для полноценной работы с 5000+ акциями:
1. Используйте FinViz для получения полного списка
2. Запускайте сканирование в фоне
3. Настройте автоматизацию через cron
4. Мониторьте результаты регулярно
