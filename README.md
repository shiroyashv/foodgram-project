# Foodgram
![example workflow](https://github.com/TheXtreme30/foodgram-project-react/actions/workflows/main.yml/badge.svg)

Проект Foodgram позволяет пользователям публиковать рецепты, добавлять рецепты в избранное и список покупок, подписыватся на других пользователей и скачивать список продуктов.

### Технологии
- Python
- Django
- Docker
- postgresql
- nginx
- gunicorn

### Запуск проекта
- Перейдите в папку backend:
```
cd backend/
``` 
- Выполните команду для запуска контейнера:
```
docker-compose up -d
``` 
- Создайте миграции:
```
docker-compose exec web python manage.py makemigrations users --noinput
docker-compose exec web python manage.py makemigrations recipes --noinput
``` 
- Выполните миграции:
```
docker-compose exec web python manage.py migrate --noinput
``` 
- Команда для сбора статики:
```
- docker-compose exec web python manage.py collectstatic --no-input
``` 
- Команда для создания суперпользователя:
```
docker-compose exec web python manage.py createsuperuser
``` 

### Автор
Сергей. Студент Яндекс.Практикум 


