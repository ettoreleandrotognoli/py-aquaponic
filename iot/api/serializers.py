from iot.models import Actuator, ActuatorData
from iot.models import PID
from iot.models import Sensor, SensorData, Magnitude, MeasureUnit, Position
from rest_framework.serializers import ModelSerializer


class MagnitudeSerializer(ModelSerializer):
    class Meta:
        model = Magnitude
        fields = ['id', 'name']


class MeasureUnitSerializer(ModelSerializer):
    class Meta:
        model = MeasureUnit
        fields = ['id', 'name', 'symbol']


class PositionSerializer(ModelSerializer):
    class Meta:
        model = Position
        exclude = ['id']


class ActuatorDetailSerializer(ModelSerializer):
    class Meta:
        model = Actuator
        fields = '__all__'

    magnitude = MagnitudeSerializer(many=False)
    measure_unit = MeasureUnitSerializer(many=False)
    position = PositionSerializer(many=False)


class ActuatorSerializer(ModelSerializer):
    class Meta:
        model = Actuator
        fields = '__all__'

    position = PositionSerializer(
        many=False,
        read_only=False,
        required=False,
    )

    def create(self, validated_data):
        position = validated_data.get('position', None)
        if position:
            position = PositionSerializer().create(position)
        validated_data['position'] = position
        return super(ActuatorSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        position = validated_data.pop('position', None)
        if position:
            position = PositionSerializer().create(position)
        instance.position = position
        return super(ActuatorSerializer, self).update(instance, validated_data)


class ActuatorDataSerializer(ModelSerializer):
    class Meta:
        model = ActuatorData
        exclude = ['actuator']


class SensorDetailSerializer(ModelSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'

    magnitude = MagnitudeSerializer(many=False)
    measure_unit = MeasureUnitSerializer(many=False)
    position = PositionSerializer(many=False)


class SensorSerializer(ModelSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'

    position = PositionSerializer(
        many=False,
        read_only=False,
        required=False,
    )

    def create(self, validated_data):
        position = validated_data.get('position', None)
        if position:
            position = PositionSerializer().create(position)
        validated_data['position'] = position
        return super(SensorSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        position = validated_data.pop('position', None)
        if position:
            position = PositionSerializer().create(position)
        instance.position = position
        return super(SensorSerializer, self).update(instance, validated_data)


class SensorDataSerializer(ModelSerializer):
    class Meta:
        model = SensorData
        exclude = ['sensor']


class PIDDetailSerializer(ModelSerializer):
    class Meta:
        model = PID
        fields = '__all__'

    input = SensorDetailSerializer(many=False)
    output = ActuatorDetailSerializer(many=False)


class PIDSerializer(ModelSerializer):
    class Meta:
        model = PID
        fields = '__all__'
