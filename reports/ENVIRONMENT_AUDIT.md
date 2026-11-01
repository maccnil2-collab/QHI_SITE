# Аудит среды разработки

Дата: 2026-11-01. Проверено в каталоге `C:\Users\Asus Notebook\QHI-AUTO`.

| Инструмент | Результат |
|---|---|
| Python | 3.11.9 |
| `.venv` | Существует; запуск через `.venv\Scripts\python.exe` работает |
| FastAPI | 0.162.0 |
| SQLAlchemy | 2.1.6 |
| Alembic | 1.20.1 |
| Pydantic | 2.14.2 |
| psycopg / psycopg-binary | 3.3.6 / 3.3.6 |
| pytest | 9.2.0 |
| Node.js (локально в tools) | 26.13.0 |
| npm (локально в tools) | 11.20.0 |
| Git (portable в tools) | 2.56.0.windows.4 |
| PostgreSQL | Установлена служба `postgresql-x64-18`, состояние Running; серверную версию/подключение ещё проверить |
| Next.js / React / TypeScript / Tailwind | Ещё не установлены в проекте |
| Playwright | Ещё не найден в `.venv`/проекте |
| VS Code / Figma / Windows build / RAM / свободный диск | Не проверены в этом аудите |

Пути portable Node и Git находятся в `tools/` проекта; глобальный PATH не менялся. PostgreSQL-инсталлятор присутствует в `downloads/`, повторно не запускался. В репозитории не сохранялись секреты. Размер исходных portable tools/installer не суммировался; новые установки в рамках данного этапа не выполнялись.

## Проверки
- Успешно запущены версии Python, Node.js, npm и Git.
- Успешно прочитан список зависимостей `.venv`.
- Состояние службы PostgreSQL 18: Running.
- Git repository initialized; команда `git config` через portable Git завершилась сообщением `fatal: not in a git directory`, несмотря на успешный `git init`; фиксации пока нет.

## Ограничения
Окружение ранее блокировало системный `winget.exe` и сетевые подключения pip. Для работы используем уже имеющиеся локальные инструменты и зависимости. Системные настройки не меняются.
