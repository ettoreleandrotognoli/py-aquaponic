from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from .actuator import ActuatorStrategy, ReadableActuator, LimitedActuator

SUPPORTED_STRATEGIES  = {
    'iot.actuators.actuator.NullActuator': _('Null Actuator'),
    'iot.actuators.parport.DataPin': _('Parallel Port Pin'),
    'iot.actuators.firmata.FirmataPin': _('Arduino Pin using Firmata Protocol'),
    'iot.actuators.mqtt.MqttDevice': _('Mqtt Remote Device'),
}
