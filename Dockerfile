FROM python:3.9-slim as builder
WORKDIR /app

COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.9-slim
WORKDIR /app

COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

RUN mkdir -p /app/instance

COPY . .

EXPOSE 5000 587

VOLUME ["/app/instance"]

CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]
