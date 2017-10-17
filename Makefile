venv: requirements.txt requirements-dev.txt
	virtualenv venv -p python3
	venv/bin/python -m pip install -U pip
	venv/bin/python -m pip install -Ur requirements.txt
	venv/bin/python -m pip install -Ur requirements-dev.txt

bower: src/iot/bower.json
	cd src/iot && bower install

static:
	venv/bin/python manage.py collectstatic --no-input -i bower
	venv/bin/python manage.py collectstatic --no-input -i "[^(bower)]" --no-post-process


clean:
	rm -Rf static