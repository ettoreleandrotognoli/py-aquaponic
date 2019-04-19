bower: src/iot/bower.json
	cd src/iot && bower install

static:
	python src/manage.py collectstatic --no-input -i bower
	python src/manage.py collectstatic --no-input -i "[^(bower)]" --no-post-process

test:
	python src/manage.py test src/

.coverage:
	coverage run src/manage.py test src/

coverage.xml: .coverage
	coverage xml --include="src/*"

coverage: coverage.xml

%.key:
	openssl genrsa -out $@ 4096

%.crt: %.key
	openssl req -new -x509 -key $^ -out $@ -days 3650 -subj /CN=${CERT_CN}

ssl: config/ssl/server.crt config/ssl/server.key
	pipenv run python manage.py collectstatic --no-input -i bower
	pipenv run python manage.py collectstatic --no-input -i "[^(bower)]" --no-post-process

clean:
	rm -Rf src/static
	rm -f .coverage coverage.xml