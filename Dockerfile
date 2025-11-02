FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./app /app

# Set PYTHONPATH to include the parent directory
ENV PYTHONPATH=/

EXPOSE 80