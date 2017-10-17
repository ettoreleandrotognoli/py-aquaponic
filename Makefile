venv: requirements.txt requirements-dev.txt
	virtualenv venv -p python3
	venv/bin/python -m pip install -U pip
	venv/bin/python -m pip install -Ur requirements.txt
	venv/bin/python -m pip install -Ur requirements-dev.txt

bower: src/iot/bower.json
	cd src/iot && bower install

static:
	venv/bin/python src/manage.py collectstatic --no-input -i bower
	venv/bin/python src/manage.py collectstatic --no-input -i "[^(bower)]" --no-post-process

test:
	venv/bin/python src/manage.py test src/

.coverage:
	venv/bin/coverage run src/manage.py test src/

coverage.xml: .coverage
	venv/bin/coverage xml --include="src/*"

coverage: coverage.xml


clean:
	rm -Rf static