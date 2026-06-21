FROM python:3.13-alpine AS base
LABEL maintainer="PINDU"
RUN apk --no-cache add bash curl gcc musl-dev libffi-dev g++ make build-base

FROM base AS builder
COPY ./requirements.txt .
RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt \
  && rm requirements.txt

FROM base
RUN mkdir /code
WORKDIR /code
COPY ./requirements.txt .
RUN pip install -r requirements.txt && rm requirements.txt
COPY --chown=user:group --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
ENV PATH /usr/local/lib/python3.13/site-packages:$PATH
RUN ln -s /usr/share/zoneinfo/America/Cordoba /etc/localtime

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]