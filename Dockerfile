FROM python:3.10-slim-bullseye

RUN apt-get update
RUN apt-get install -y libopus0
RUN apt-get install -y git

WORKDIR /app
COPY setup.cfg setup.cfg
COPY pyproject.toml pyproject.toml
COPY voice_eq_bot voice_eq_bot

RUN pip install .

CMD ["python", "-m", "voice_eq_bot"]
