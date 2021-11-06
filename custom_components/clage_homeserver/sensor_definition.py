""" Module for the structured defition of the a sensor"""


class SensorDefinition:
    """An class for the definition of a sensor."""

    system_name: str
    """The technical name of a sensor, that can be used in automations; e.g. my_great_sensor"""

    name: str
    """"""

    definition: str
    """"""

    unit: str
    """"""

    state_class: str
    """"""

    device_class: str
    """"""

    entity_category: str
    """"""

    def __init__(
        self,
        system_name,
        name,
        definition,
        unit,
        state_class,
        device_class,
        entity_category,
    ):
        self.system_name = system_name
        self.name = name
        self.definition = definition
        self.unit = unit
        self.state_class = state_class
        self.device_class = device_class
        self.entity_category = entity_category
