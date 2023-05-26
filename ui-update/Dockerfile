FROM python:alpine

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY update_meta_ui.py .

CMD [ "python", "-u", "./update_meta_ui.py" ]
