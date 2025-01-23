FROM python:latest

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY hiram_dashboard.py .

EXPOSE 8501

CMD ["streamlit", "run", "hiram_dashboard.py"]