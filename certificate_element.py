from typing import Union


class CertificateElement:

    def __init__(self, table_index, x_coordinate, y_coordinate, name, value):
        self.table_index = table_index
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.name = name
        self.value = value

    def __repr__(self):
        return (
            f"{self.name}: {self.value} [table_index: {self.table_index}, x_coordinate: {self.x_coordinate} , "
            f"y_coordinate: {self.y_coordinate}]"
        )


class SteelPlant(CertificateElement):

    def __init__(self, value):
        super(SteelPlant, self).__init__(
            table_index=None,
            x_coordinate=None,
            y_coordinate=None,
            name='Steel Plant',
            value=value)

    def __repr__(self):
        return f"{self.name}: {self.value}"


class Specification(CertificateElement):

    def __init__(self, table_index, x_coordinate, y_coordinate, value):
        super(Specification, self).__init__(
            table_index=table_index,
            x_coordinate=x_coordinate,
            y_coordinate=y_coordinate,
            name='Specification',
            value=value
        )


class Thickness(CertificateElement):

    def __init__(self, table_index, x_coordinate, y_coordinate, value):
        super(Thickness, self).__init__(
            table_index=table_index,
            x_coordinate=x_coordinate,
            y_coordinate=y_coordinate,
            name='Thickness',
            value=value
        )
        self.valid_flag = True
        self.message = None

    def is_valid(self):
        if self.valid_flag:
            return True
        else:
            return False


class SerialNumber(CertificateElement):

    def __init__(self, table_index, x_coordinate, y_coordinate, value):
        super(SerialNumber, self).__init__(
            table_index=table_index,
            x_coordinate=x_coordinate,
            y_coordinate=y_coordinate,
            name='SerialNumber',
            value=value
        )
        self.length = len(value)

    def __repr__(self):
        return (
            f"{self.name}: length={self.length} sequence={self.value} [table_index: {self.table_index}, "
            f"x_coordinate: {self.x_coordinate} , y_coordinate: {self.y_coordinate}]"
        )


class ChemicalElement(CertificateElement):

    def __init__(self, table_index, x_coordinate, y_coordinate, row_index: int, value, precision: int):
        super(ChemicalElement, self).__init__(
            table_index=table_index,
            x_coordinate=x_coordinate,
            y_coordinate=y_coordinate,
            name='ChemicalElementName',
            value=value
        )
        self.row_index=row_index
        self.precision = precision

    def __repr__(self):
        return (
            f"{self.name}: {self.value} precision: {self.precision} [table_index: {self.table_index}, "
            f"x_coordinate: {self.x_coordinate} , y_coordinate: {self.y_coordinate}]"
        )


class ChemicalElementValue(CertificateElement):

    def __init__(self, table_index, x_coordinate, y_coordinate, value, index, element: str, precision):
        super(ChemicalElementValue, self).__init__(
            table_index=table_index,
            x_coordinate=x_coordinate,
            y_coordinate=y_coordinate,
            name='ChemicalElementValue',
            value=value
        )
        self.index = index
        self.element = element
        self.precision = precision
        self.valid_flag = True
        self.message = None

    def __repr__(self):
        return (
            f"value: {self.value} precision: {self.precision} [table_index: {self.table_index}, "
            f"x_coordinate: {self.x_coordinate} , y_coordinate: {self.y_coordinate}, index: {self.index}] "
            f"[valid_flag: {self.valid_flag}, message: {self.message}]"
        )

    def calculated_value(self):
        return round(self.value * (10 ** -self.precision), self.precision)

    def is_valid(self):
        if self.valid_flag:
            return True
        else:
            return False


class DeliveryCondition(CertificateElement):

    def __init__(self, table_index, x_coordinate, y_coordinate, index, value):
        super(DeliveryCondition, self).__init__(
            table_index=table_index,
            x_coordinate=x_coordinate,
            y_coordinate=y_coordinate,
            name='DeliveryCondition',
            value=value
        )
        self.index = index

    def __repr__(self):
        return (
            f"{self.name}: {self.value} [table_index: {self.table_index}, "
            f"x_coordinate: {self.x_coordinate} , y_coordinate: {self.y_coordinate}, index: {self.index}]"
        )


class YieldStrength(CertificateElement):

    def __init__(self, table_index, x_coordinate, y_coordinate, index, value):
        super(YieldStrength, self).__init__(
            table_index=table_index,
            x_coordinate=x_coordinate,
            y_coordinate=y_coordinate,
            name='YieldStrength',
            value=value
        )
        self.index = index
        self.valid_flag = True,
        self.message = None

    def __repr__(self):
        return (
            f"{self.name}: {self.value} [table_index: {self.table_index}, "
            f"x_coordinate: {self.x_coordinate} , y_coordinate: {self.y_coordinate}, index: {self.index}] "
            f"[valid_flag: {self.valid_flag}, message: {self.message}]"
        )


class TensileStrength(CertificateElement):

    def __init__(self, table_index, x_coordinate, y_coordinate, index, value):
        super(TensileStrength, self).__init__(
            table_index=table_index,
            x_coordinate=x_coordinate,
            y_coordinate=y_coordinate,
            name='TensileStrength',
            value=value
        )
        self.index = index
        self.valid_flag = True,
        self.message = None

    def __repr__(self):
        return (
            f"{self.name}: {self.value} [table_index: {self.table_index}, "
            f"x_coordinate: {self.x_coordinate} , y_coordinate: {self.y_coordinate}, index: {self.index}] "
            f"[valid_flag: {self.valid_flag}, message: {self.message}]"
        )


class Elongation(CertificateElement):

    def __init__(self, table_index, x_coordinate, y_coordinate, index, value):
        super(Elongation, self).__init__(
            table_index=table_index,
            x_coordinate=x_coordinate,
            y_coordinate=y_coordinate,
            name='Elongation',
            value=value
        )
        self.index = index
        self.valid_flag = True,
        self.message = None

    def __repr__(self):
        return (
            f"{self.name}: {self.value} [table_index: {self.table_index}, "
            f"x_coordinate: {self.x_coordinate} , y_coordinate: {self.y_coordinate}, index: {self.index}] "
            f"[valid_flag: {self.valid_flag}, message: {self.message}]"
        )


class PositionDirectionImpact(CertificateElement):

    def __init__(self, table_index, x_coordinate, y_coordinate, index, value):
        super(PositionDirectionImpact, self).__init__(
            table_index=table_index,
            x_coordinate=x_coordinate,
            y_coordinate=y_coordinate,
            name='Position Direction of Impact Test',
            value=value
        )
        self.index = index

    def __repr__(self):
        return (
            f"{self.name}: {self.value} [table_index: {self.table_index}, "
            f"x_coordinate: {self.x_coordinate} , y_coordinate: {self.y_coordinate}, index: {self.index}] "
        )


class Temperature(CertificateElement):

    def __init__(self, table_index, x_coordinate, y_coordinate, index, value):
        super(Temperature, self).__init__(
            table_index=table_index,
            x_coordinate=x_coordinate,
            y_coordinate=y_coordinate,
            name='Temperature',
            value=value
        )
        self.index = index
        self.valid_flag = True,
        self.message = None

    def __repr__(self):
        return (
            f"{self.name}: {self.value} [table_index: {self.table_index}, "
            f"x_coordinate: {self.x_coordinate} , y_coordinate: {self.y_coordinate}, index: {self.index}] "
            f"[valid_flag: {self.valid_flag}, message: {self.message}]"
        )


class ImpactEnergy(CertificateElement):

    def __init__(self, table_index, x_coordinate, y_coordinate, index, test_number, value):
        super(ImpactEnergy, self).__init__(
            table_index=table_index,
            x_coordinate=x_coordinate,
            y_coordinate=y_coordinate,
            name='Impact Energy',
            value=value
        )
        self.index=index
        self.test_number = test_number
        self.valid_flag = True
        self.message = None

    def __repr__(self):
        return (
            f"{self.name}: test_number={self.test_number}, value={self.value} [table_index: {self.table_index}, "
            f"x_coordinate: {self.x_coordinate} , y_coordinate: {self.y_coordinate}, index: {self.index}] "
            f"[valid_flag: {self.valid_flag}, message: {self.message}]"
        )


class SteelPlate:

    def __init__(self, serial_number: int):
        self.serial_number = serial_number
        self.chemical_compositions = dict()
        self.yield_strength = None
        self.tensile_strength = None
        self.elongation = None
        self.position_direction_impact: Union[PositionDirectionImpact, None] = None
        self.temperature = None
        self.impact_energy_list = []
        self.delivery_condition: Union[DeliveryCondition, None] = None

    def __repr__(self):
        chemical_repr = '\n\t'.join(
            ['chemical element: ' + element + ' ' + str(self.chemical_compositions[element]) for element in
             self.chemical_compositions])
        impact_energy_repr = '\n'.join([str(impact_energy) for impact_energy in self.impact_energy_list])
        return (
            f"No. {self.serial_number}\n"
            f"{self.delivery_condition}\n"
            f"Chemical composition: \n\t{chemical_repr}\n"
            f"{self.yield_strength}\n"
            f"{self.tensile_strength}\n"
            f"{self.elongation}\n"
            f"{self.position_direction_impact}\n"
            f"{self.temperature}\n"
            f"{impact_energy_repr}\n\n"
        )