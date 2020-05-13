FROM python:3.7

USER root

WORKDIR /app
ADD . /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8050

ENV NAME covid_app

CMD ["gunicorn", "--bind", "0.0.0.0:8050", "application.__main__:application"]
