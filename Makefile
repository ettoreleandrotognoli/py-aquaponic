venv: requirements.txt requirements-dev.txt
	virtualenv venv -p python3
	python -m pip install -U pip
	python -m pip install -Ur requirements.txt
	python -m pip install -Ur requirements-dev.txt

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


clean:
	rm -Rf src/static
	rm -f .coverage coverage.xml