FROM python:alpine

WORKDIR /app
COPY ui-update/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ui-update/update_meta_ui.py .

CMD [ "python", "-u", "./update_meta_ui.py" ]
