FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api.py predictions.py pharmacy_logic.py ./
COPY model/ model/
COPY frontend/ frontend/
EXPOSE 8000
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8000", "api:app"]
