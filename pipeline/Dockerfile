FROM python:latest

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY logger_config.py .

COPY pipeline_2.py .

COPY extract_2.py .

COPY transform_2.py .

COPY load.py .

CMD ["python3", "pipeline_2.py"]
