import random
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from model_mommy import mommy

from iot.models import Sensor, Position, MeasureUnit


class TestSensor(TestCase):
    client = None

    def setUp(self):
        self.client = Client()
        self.client.force_login(get_user_model().objects.get_or_create(username='testuser')[0])

    def test_put_single_data(self):
        max_value = 50
        min_value = -50
        position = mommy.make(Position)
        celsius = MeasureUnit.objects.select_related('magnitude').get(name='celsius')
        sensor = mommy.make(
            Sensor,
            position=position,
            measure_unit=celsius,
            magnitude=celsius.magnitude
        )
        result = self.client.post(
            reverse('iot-api:sensor-data', kwargs=dict(endpoint=sensor.endpoint)),
            data={'value': random.uniform(min_value, max_value)}
        )
        self.assertEqual(201, result.status_code)
