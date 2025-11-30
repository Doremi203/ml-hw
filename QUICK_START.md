## 🚀 Запуск

```bash
# Запустить все сервисы
docker compose up -d

# Проверить статус
docker compose ps

```

## 🌐 Доступные интерфейсы

После запуска будут доступны:

- **🎛️ Streamlit Dashboard**: http://localhost:8501
- **📦 MinIO Console**: http://localhost:9001 (логин: minio, пароль: minio123)
- **🔌 ML API**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs

## 📋 Основные команды

```bash
# Запуск
docker compose up -d

# Остановка
docker compose down

# Перезапуск
docker compose restart

# Просмотр логов
docker compose logs -f

# Пересборка образов
docker compose build

# Полная очистка
docker compose down -v
```