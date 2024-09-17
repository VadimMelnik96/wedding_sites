FROM python:3.12.2-slim

ARG POETRY_PARAMS="--without dev"

ENV PYTHONUNBUFFERED 1
ENV PYTHONWARNINGS=ignore
ENV POETRY_VIRTUALENVS_CREATE=false
# Add src to PYTHONPATH
ENV PYTHONPATH=/app/src


# обновление и установка рекомендованных и необходимых системных библиотек
RUN apt-get update -y --no-install-recommends
RUN apt-get install -y --no-install-recommends \
    git `# для установки зависимостей из git` \
    gcc `# для cryptography`

# устанавлием рабочую директорую
WORKDIR /app

# инсталляция зависимостей
COPY requirements.lock /app/


RUN sed '/-e/d' requirements.lock > requirements.txt
RUN pip install -r requirements.txt

# копируем файлы проекта
COPY . .



EXPOSE 8000


CMD ["python", "src/main.py"]