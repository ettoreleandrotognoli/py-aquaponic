FROM pypy:3
ADD . /code
WORKDIR /code
RUN pip install psycopg2cffi asgi_redis
RUN pip install -r requirements.txt
