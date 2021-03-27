FROM python:3.7-buster

RUN mkdir -p /opt/app
WORKDIR /opt/app


# Copy project code.
COPY main.py /opt/app/main.py
COPY requirements.txt /opt/app/requirements.txt

# Install dependencies.
RUN pip install -r requirements.txt

ENTRYPOINT python /opt/app/main.py