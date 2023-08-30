FROM python:3.9

ENV PYTHONUNBUFFERED 1

# Создайте директорию приложения и установите рабочую директорию в неё
RUN mkdir /app
WORKDIR /app

# Копируйте файлы проекта в контейнер
COPY . /app/

# Перейдите в директорию с файлом setup.py и выполните команду
WORKDIR /app/diploma-frontend
RUN python setup.py sdist

WORKDIR /app/diploma-frontend/dist
RUN pip install diploma-frontend-0.6.tar.gz

WORKDIR /app

# Копируйте зависимости и установите их
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/megano

RUN python manage.py migrate

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
