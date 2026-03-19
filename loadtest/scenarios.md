# Сценарии нагрузочного тестирования

## Цель

Проверить поведение сервиса под нагрузкой на инференс и собрать ключевые метрики:

- RPS по эндпоинтам
- Латентность p50/p95/p99
- Доля ошибок (4xx/5xx)
- Время инференса p50/p95

## Сценарий 1 - Базовый (стабильная нагрузка)

- 20 пользователей, скорость запуска 5 пользователей/сек
- Длительность: 10 минут
- Смешанная нагрузка:
  - 70% `POST /models/{model_id}/predict`
  - 20% `GET /healthz`
  - 10% `GET /models/`
- Цель: зафиксировать стабильные базовые значения p50/p95 и RPS.

## Сценарий 2 - Постепенное наращивание нагрузки

- Старт с 20 пользователей, увеличение до 200 пользователей шагами по 20 каждые 2 минуты
- Длительность: 20 минут
- Та же смесь эндпоинтов, что и в базовом сценарии
- Цель: найти точку насыщения, где p95 латентности и доля ошибок начинают резко расти.

## Сценарий 3 - Устойчивость к пиковому всплеску

- Прогрев: 30 пользователей в течение 5 минут
- Пик: 300 пользователей в течение 2 минут
- Восстановление: 30 пользователей в течение 8 минут
- Цель: оценить обработку кратковременного всплеска и время восстановления.

## Критерии приемки (начальные)

- Доля ошибок < 1% в базовом сценарии
- p95 HTTP-латентности для эндпоинта predict < 500ms в базовом сценарии
- p95 времени инференса < 400ms в базовом сценарии

## PromQL-запросы

### RPS по эндпоинтам

```promql
sum(rate(http_requests_total{job="ml-rest"}[1m])) by (handler, method)
```

### HTTP-латентность p50/p95/p99

```promql
histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket{job="ml-rest"}[5m])) by (le, handler))
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="ml-rest"}[5m])) by (le, handler))
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{job="ml-rest"}[5m])) by (le, handler))
```

### Доля ошибок (4xx+5xx)

```promql
100 * sum(rate(http_requests_total{job="ml-rest",status=~"4..|5.."}[5m])) by (handler)
  / clamp_min(sum(rate(http_requests_total{job="ml-rest"}[5m])) by (handler), 1e-9)
```

### Время инференса p50/p95

```promql
histogram_quantile(0.50, sum(rate(ml_inference_duration_seconds_bucket{status="success"}[5m])) by (le))
histogram_quantile(0.95, sum(rate(ml_inference_duration_seconds_bucket{status="success"}[5m])) by (le))
```


