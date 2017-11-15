FROM pypy:3
RUN mkdir -p /opt/py-aquaponic/
WORKDIR /opt/py-aquaponic/
RUN pip install psycopg2cffi asgi_redis pyopenssl
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
