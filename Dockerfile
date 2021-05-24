FROM snakepacker/python:modern as builder

RUN python3.6 -m venv /venv

COPY ./requirements.txt requirements.txt
RUN /venv/bin/python3.6 -m pip install -r requirements.txt


FROM snakepacker/python:3.6 as app
WORKDIR /app

COPY --from=builder /venv /venv
COPY . /app

ENV PATH /venv/bin:$PATH

CMD python /app/app.py