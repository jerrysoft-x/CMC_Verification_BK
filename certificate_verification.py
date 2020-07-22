from enum import Enum, unique
from collections import defaultdict
from typing import Tuple, Union, List, Dict

from certificate_element import Thickness, ChemicalElementValue, YieldStrength, TensileStrength, Elongation, \
    Temperature, ImpactEnergy


@unique
class LimitType(Enum):
    MAXIMUM = 1
    MINIMUM = 2
    RANGE = 3
    UNIQUE = 4


class ChemicalCompositionLimit:

    def __init__(
        self,
        chemical_element: str,
        limit_type: LimitType,
        maximum: float = None,
        minimum: float = None,
        mandatory: bool = True
    ):
        self.chemical_element = chemical_element
        self.limit_type = limit_type
        self.maximum = maximum
        self.minimum = minimum
        self.mandatory = mandatory
        self.self_inspection()

    def self_inspection(self):
        if self.limit_type == LimitType.MAXIMUM:
            if self.maximum is None or str(type(self.maximum)) != "<class 'float'>":
                raise ValueError(
                    f"Maximum value {self.maximum} is not properly specified for chemical element "
                    f"{self.chemical_element} limit type {self.limit_type}. Current type is {str(type(self.maximum))}."
                )
        elif self.limit_type == LimitType.MINIMUM:
            if self.minimum is None or str(type(self.minimum)) != "<class 'float'>":
                raise ValueError(
                    f"Minimum value {self.minimum} is not properly specified for chemical element "
                    f"{self.chemical_element} limit type {self.limit_type}. Current type is {str(type(self.maximum))}."
                )
        elif self.limit_type == LimitType.RANGE:
            if self.maximum is None or str(type(self.maximum)) != "<class 'float'>":
                raise ValueError(
                    f"Maximum value {self.maximum} is not properly specified for chemical element "
                    f"{self.chemical_element} limit type {self.limit_type}. Current type is {str(type(self.maximum))}."
                )
            if self.minimum is None or str(type(self.minimum)) != "<class 'float'>":
                raise ValueError(
                    f"Minimum value {self.minimum} is not properly specified for chemical element "
                    f"{self.chemical_element} limit type {self.limit_type}. Current type is {str(type(self.maximum))}."
                )

    def is_mandatory(self) -> bool:
        if self.mandatory:
            return True
        else:
            return False

    def verify(self, value: float) -> Tuple[bool, str]:
        if self.limit_type == LimitType.MAXIMUM:
            if value <= self.maximum:
                message = (
                    f"[PASS] The value of chemical element {self.chemical_element} is {value}, meets the maximum "
                    f"limit {self.maximum}."
                )
                print(message)
                return True, message
            else:
                message = (
                    f"[FAIL] The value of chemical element {self.chemical_element} is {value}, violates the maximum "
                    f"limit {self.maximum}."
                )
                print(message)
                return False, message
        elif self.limit_type == LimitType.MINIMUM:
            if value >= self.minimum:
                message = (
                    f"[PASS] The value of chemical element {self.chemical_element} is {value}, meets the minimum "
                    f"limit {self.minimum}."
                )
                print(message)
                return True, message
            else:
                message = (
                    f"[FAIL] The value of chemical element {self.chemical_element} is {value}, violates the minimum "
                    f"limit {self.minimum}."
                )
                print(message)
                return False, message
        elif self.limit_type == LimitType.RANGE:
            if self.minimum <= value <= self.maximum:
                message = (
                    f"[PASS] The value of chemical element {self.chemical_element} is {value}, meets the valid "
                    f"range [{self.minimum}, {self.maximum}]."
                )
                print(message)
                return True, message
            else:
                message = (
                    f"[FAIL] The value of chemical element {self.chemical_element} is {value}, violates the valid "
                    f"range [{self.minimum}, {self.maximum}]."
                )
                print(message)
                return False, message


class ChemicalCompositionLimitsForHighStrengthSteel:

    # ################################ Singleton ################################ #
    _singleton = None

    @classmethod
    def get_singleton(cls):
        if not isinstance(cls._singleton, cls):
            cls._singleton = cls()
        return cls._singleton
    # ################################ Singleton ################################ #

    def __init__(self):
        self.grade_chemical_element_normal_limit_map = defaultdict(dict)
        self.grade_clusters = [
            [
                'VL A27S',
                'VL D27S',
                'VL E27S'
            ],
            [
                'VL A32',
                'VL D32',
                'VL E32',
                'VL A36',
                'VL D36',
                'VL E36',
                'VL A40',
                'VL D40',
                'VL E40'
            ],
            [
                'VL F27S',
                'VL F32',
                'VL F36',
                'VL F40'
            ]
        ]
        self.compose_map()

    def map_grade_and_limit(self, grade_cluster_list: list, limit: ChemicalCompositionLimit):
        for index in grade_cluster_list:
            for grade in self.grade_clusters[index]:
                self.grade_chemical_element_normal_limit_map[grade][limit.chemical_element] = limit

    def compose_map(self):
        # compose C 0.18
        limit = ChemicalCompositionLimit(
            chemical_element='C',
            limit_type=LimitType.MAXIMUM,
            maximum=0.18
        )
        self.map_grade_and_limit(grade_cluster_list=[0, 1], limit=limit)
        # compose C 0.16
        limit = ChemicalCompositionLimit(
            chemical_element='C',
            limit_type=LimitType.MAXIMUM,
            maximum=0.16
        )
        self.map_grade_and_limit(grade_cluster_list=[2], limit=limit)
        # compose Si 0.50
        limit = ChemicalCompositionLimit(
            chemical_element='Si',
            limit_type=LimitType.MAXIMUM,
            maximum=0.50
        )
        self.map_grade_and_limit(grade_cluster_list=[0, 1, 2], limit=limit)
        # compose Mn 0.70 - 1.60
        limit = ChemicalCompositionLimit(
            chemical_element='Mn',
            limit_type=LimitType.RANGE,
            minimum=0.70,
            maximum=1.60
        )
        self.map_grade_and_limit(grade_cluster_list=[0], limit=limit)
        # compose Mn 1.90 - 1.60
        limit = ChemicalCompositionLimit(
            chemical_element='Mn',
            limit_type=LimitType.RANGE,
            minimum=0.90,
            maximum=1.60
        )
        self.map_grade_and_limit(grade_cluster_list=[1, 2], limit=limit)
        # compose P 0.035
        limit = ChemicalCompositionLimit(
            chemical_element='P',
            limit_type=LimitType.MAXIMUM,
            maximum=0.035
        )
        self.map_grade_and_limit(grade_cluster_list=[0, 1], limit=limit)
        # compose P 0.025
        limit = ChemicalCompositionLimit(
            chemical_element='P',
            limit_type=LimitType.MAXIMUM,
            maximum=0.025
        )
        self.map_grade_and_limit(grade_cluster_list=[2], limit=limit)
        # compose S 0.035
        limit = ChemicalCompositionLimit(
            chemical_element='S',
            limit_type=LimitType.MAXIMUM,
            maximum=0.035
        )
        self.map_grade_and_limit(grade_cluster_list=[0, 1], limit=limit)
        # compose S 0.025
        limit = ChemicalCompositionLimit(
            chemical_element='S',
            limit_type=LimitType.MAXIMUM,
            maximum=0.025
        )
        self.map_grade_and_limit(grade_cluster_list=[2], limit=limit)
        # compose Cr 0.20
        limit = ChemicalCompositionLimit(
            chemical_element='Cr',
            limit_type=LimitType.MAXIMUM,
            maximum=0.20
        )
        self.map_grade_and_limit(grade_cluster_list=[0, 1, 2], limit=limit)
        # compose Mo 0.08
        limit = ChemicalCompositionLimit(
            chemical_element='Mo',
            limit_type=LimitType.MAXIMUM,
            maximum=0.08
        )
        self.map_grade_and_limit(grade_cluster_list=[0, 1, 2], limit=limit)
        # compose Ni 0.40
        limit = ChemicalCompositionLimit(
            chemical_element='Ni',
            limit_type=LimitType.MAXIMUM,
            maximum=0.40
        )
        self.map_grade_and_limit(grade_cluster_list=[0, 1], limit=limit)
        # compose Ni 0.80
        limit = ChemicalCompositionLimit(
            chemical_element='Ni',
            limit_type=LimitType.MAXIMUM,
            maximum=0.80
        )
        self.map_grade_and_limit(grade_cluster_list=[2], limit=limit)
        # compose Cu 0.35
        limit = ChemicalCompositionLimit(
            chemical_element='Cu',
            limit_type=LimitType.MAXIMUM,
            maximum=0.35,
            mandatory=False
        )
        self.map_grade_and_limit(grade_cluster_list=[0, 1, 2], limit=limit)
        # compose Al 0.020
        limit = ChemicalCompositionLimit(
            chemical_element='Al',
            limit_type=LimitType.MINIMUM,
            minimum=0.020,
            mandatory=False
        )
        self.map_grade_and_limit(grade_cluster_list=[0, 1, 2], limit=limit)
        # compose Nb 0.02 - 0.05
        limit = ChemicalCompositionLimit(
            chemical_element='Nb',
            limit_type=LimitType.RANGE,
            minimum=0.02,
            maximum=0.05,
            mandatory=False
        )
        self.map_grade_and_limit(grade_cluster_list=[0, 1, 2], limit=limit)
        # compose V 0.05 - 0.10
        limit = ChemicalCompositionLimit(
            chemical_element='V',
            limit_type=LimitType.RANGE,
            minimum=0.05,
            maximum=0.10,
            mandatory=False
        )
        self.map_grade_and_limit(grade_cluster_list=[0, 1, 2], limit=limit)
        # compose Ti 0.007 - 0.02
        limit = ChemicalCompositionLimit(
            chemical_element='Ti',
            limit_type=LimitType.RANGE,
            minimum=0.007,
            maximum=0.02,
            mandatory=False
        )
        self.map_grade_and_limit(grade_cluster_list=[0, 1, 2], limit=limit)
        # compose N 0.009
        limit = ChemicalCompositionLimit(
            chemical_element='N',
            limit_type=LimitType.MAXIMUM,
            maximum=0.009,
            mandatory=False
        )
        self.map_grade_and_limit(grade_cluster_list=[2], limit=limit)

    def get_limits_by_specification(self, specification: str) -> Dict[str, ChemicalCompositionLimit]:
        if specification in self.grade_chemical_element_normal_limit_map:
            return self.grade_chemical_element_normal_limit_map[specification]
        else:
            raise ValueError(
                f"Could not find specification {specification} in the chemical composition limit table."
            )

    def find_alternative_limit(self, specification: str, chemical_element: str, thickness: float,
                               chemical_compositions: dict) -> ChemicalCompositionLimit:

        # Table 9 Chemical composition limits for high strength steel - annotation 2
        if specification in self.grade_clusters[1] and chemical_element == 'Mn':
            if thickness <= 12.5:
                return ChemicalCompositionLimit(
                    chemical_element='Mn',
                    limit_type=LimitType.RANGE,
                    minimum=0.70,
                    maximum=1.60
                )

        # Table 9 Chemical composition limits for high strength steel - annotation 6
        if specification in self.grade_clusters[2] and chemical_element == 'N':
            if 'Al' in chemical_compositions:
                return ChemicalCompositionLimit(
                    chemical_element='N',
                    limit_type=LimitType.MAXIMUM,
                    maximum=0.012,
                    mandatory=False
                )

    def locate(self, grade: str, chemical_element: str) -> ChemicalCompositionLimit:
        if self.grade_chemical_element_normal_limit_map[grade][chemical_element] is None:
            raise ValueError(
                f"Could not find chemical composition limit for grade {grade} and chemical element {chemical_element}."
            )
        else:
            return self.grade_chemical_element_normal_limit_map[grade][chemical_element]

    def locate_multiple_limits(
        self,
        grade: str,
        element_list: Union[Tuple[str], Tuple[str, str], Tuple[str, str, str], Tuple[str, str, str, str]]
    ) -> Dict[str, ChemicalCompositionLimit]:
        limits = dict()
        for element in element_list:
            limit = self.locate(grade=grade, chemical_element=element)
            limits[element] = limit
        return limits

    def verify(self, specification: str, thickness: float, chemical_compositions: dict, pdf_path: str,
               limits=None, only_mandatory=True) -> bool:
        all_pass_flag = True
        if limits is None:
            limits = self.get_limits_by_specification(specification)
        for element in limits:
            normal_limit = limits[element]
            # skip non-mandatory limits when check only mandatory flag is True
            if only_mandatory and not normal_limit.is_mandatory():
                continue
            if element in chemical_compositions:
                chemical_element_value = chemical_compositions[element]
                element_calculated_value = chemical_element_value.calculated_value()
                chemical_element_value.valid_flag, chemical_element_value.message = normal_limit.verify(
                    element_calculated_value)
                if not chemical_element_value.is_valid():
                    alternative_limit = ChemicalCompositionLimitsForHighStrengthSteel.get_singleton() \
                        .find_alternative_limit(
                        specification=specification,
                        chemical_element=element,
                        thickness=thickness,
                        chemical_compositions=chemical_compositions
                    )
                    if alternative_limit is None:
                        all_pass_flag = False
                    else:
                        chemical_element_value.valid_flag, chemical_element_value.message = \
                            alternative_limit.verify(element_calculated_value)
                        if not chemical_element_value.is_valid:
                            all_pass_flag = False
            else:
                missing_chemical_element = ChemicalElementValue(
                    table_index=None,
                    x_coordinate=None,
                    y_coordinate=None,
                    value=None,
                    index=None,
                    element=element,
                    precision=None,
                )
                missing_chemical_element.valid_flag = False
                missing_chemical_element.message = (
                    f"[FAIL] Chemical element {element} is required to be checked, but is not present in the given "
                    f"PDF file {pdf_path}"
                )
                print(missing_chemical_element.message)
                chemical_compositions[element] = missing_chemical_element
                all_pass_flag = False
        return all_pass_flag


class ThicknessLimit:

    def __init__(self, maximum: Union[float, int], limit_type: LimitType = LimitType.MAXIMUM, unit: str = 'mm'):
        self.maximum = maximum
        self.limit_type = limit_type
        self.unit = unit

    def verify(self, value: Union[float, int]) -> Tuple[bool, str]:
        if value <= self.maximum:
            message = f"[PASS] Thickness value is {value}, meets the maximum limit {self.maximum} {self.unit}."
            print(message)
            return True, message
        else:
            message = f"[FAIL] Thickness value is {value}, violates the maximum limit {self.maximum} {self.unit}."
            print(message)
            return False, message


class HullStructureSteelPlateLimit:

    def __init__(
        self,
        # grade: str,
        # delivery_condition: str,
        thickness_limit: ThicknessLimit,
        fine_grain_elements: Union[Tuple[str], Tuple[str, str], Tuple[str, str, str], Tuple[str, str, str, str]],
        reset_elements: List[str] = None
    ):
        # self.grade = grade
        # self.delivery_condition = delivery_condition
        self.thickness_limit = thickness_limit
        self.fine_grain_elements = fine_grain_elements
        self.reset_elements = reset_elements

    def verify(
        self,
        specification: str,
        thickness: Thickness,
        chemical_compositions: Dict[str, ChemicalElementValue],
        pdf_path: str
    ) -> bool:
        # if the limit is an alternative one, its reset element list isn't None, then we need to reset those elements.
        if self.reset_elements is not None:
            for element in self.reset_elements:
                if element in chemical_compositions:
                    chemical_element_value = chemical_compositions[element]
                    chemical_element_value.valid_flag = True
                    chemical_element_value.message = None
        all_pass_flag = True
        thickness.valid_flag, thickness.message = self.thickness_limit.verify(thickness.value)
        if thickness.is_valid():
            chemical_composition_limits = ChemicalCompositionLimitsForHighStrengthSteel.get_singleton()
            limits = chemical_composition_limits.locate_multiple_limits(grade=specification,
                                                                        element_list=self.fine_grain_elements)
            if not chemical_composition_limits.verify(
                specification=specification,
                thickness=thickness.value,
                chemical_compositions=chemical_compositions,
                pdf_path=pdf_path,
                limits=limits,
                only_mandatory=False
            ):
                all_pass_flag = False
        else:
            all_pass_flag = False
        return all_pass_flag


class HullStructureSteelPlateLimitsForSteelPlant:

    def __init__(
        self,
        steel_plant: str,
        limits: Dict[str, Dict[str, Dict[str, HullStructureSteelPlateLimit]]]
        # alternative_limits: Dict[str, Dict[str, HullStructureSteelPlateLimit]]
    ):
        self.steel_plant = steel_plant
        self.limits = limits
        # self.alternative_limits = alternative_limits

    def verify(
        self,
        specification: str,
        delivery_condition: str,
        thickness: Thickness,
        chemical_compositions: Dict[str, ChemicalElementValue],
        pdf_path: str
    ) -> bool:
        print(f"Delivery Condition: {delivery_condition}\n")
        # Find out the combination of fine grained elements that fit the certificate best
        element_combinations = self.limits[specification][delivery_condition]
        best_combination = None
        minimum_standard_combination = None
        for combination in element_combinations:
            if minimum_standard_combination is None:
                minimum_standard_combination = combination
            else:
                if len(combination) < len(minimum_standard_combination):
                    minimum_standard_combination = combination
            if all(map(lambda x: x in chemical_compositions, combination)):
                if best_combination is None:
                    best_combination = combination
                else:
                    if len(combination) > len(best_combination):
                        best_combination = combination
        if best_combination is None:
            limit = element_combinations[minimum_standard_combination]
        else:
            limit = element_combinations[best_combination]
        if limit.verify(
            specification=specification,
            thickness=thickness,
            chemical_compositions=chemical_compositions,
            pdf_path=pdf_path
        ):
            return True
        else:
            return False


class HullStructureSteelPlateLimits:

    # ################################ Singleton ################################ #
    _singleton = None

    @classmethod
    def get_singleton(cls):
        if not isinstance(cls._singleton, cls):
            cls._singleton = cls()
        return cls._singleton
    # ################################ Singleton ################################ #

    def __init__(self):
        self.steel_plant_map = dict()
        self.compose_bao_steel_limits()

    def get_limits_by_steel_plant(self, steel_plant: str) -> HullStructureSteelPlateLimitsForSteelPlant:
        return self.steel_plant_map[steel_plant]

    def compose_bao_steel_limits(self):
        steel_plant = 'BAOSHAN IRON & STEEL CO., LTD.'
        bao_steel_limits = HullStructureSteelPlateLimitsForSteelPlant(
            steel_plant=steel_plant,
            limits=defaultdict(lambda: defaultdict(dict)),
            # alternative_limits=defaultdict(dict)
        )
        self.steel_plant_map[steel_plant] = bao_steel_limits
        # Define grade clusters:
        grade_clusters = [
            [
                'VL A27S',
                'VL A32'
            ],
            [
                'VL D27S',
                'VL D32'
            ],
            [
                'VL A36'
            ],
            [
                'VL D36'
            ],
            [
                'VL E27S',
                'VL E32',
                'VL E36'
            ],
            [
                'VL A27S',
                'VL A32',
                'VL A36',
                'VL D27S',
                'VL D32',
                'VL D36',
                'VL E27S',
                'VL E32',
                'VL E36',
                'VL A40',
                'VL D40',
                'VL E40'
            ],
            [
                'VL A27S',
                'VL A32',
                'VL A36',
                'VL D27S',
                'VL D32',
                'VL D36',
                'VL E27S',
                'VL E32',
                'VL E36'
            ],
            [
                'VL A32',
                'VL D32',
                'VL E32',
                'VL A36',
                'VL D36',
                'VL E36'
            ],
            [
                'VL F27S',
                'VL F32',
                'VL F36',
                'VL F40'
            ]
        ]

        def map_grade_delivery_condition_and_limit(
            limits: dict,
            grade_cluster_indexes: List[int],
            delivery_condition: str,
            fine_grain_elements: Union[Tuple[str], Tuple[str, str], Tuple[str, str, str], Tuple[str, str, str, str]],
            limit: HullStructureSteelPlateLimit
        ):
            for grade_cluster_index in grade_cluster_indexes:
                grade_cluster = grade_clusters[grade_cluster_index]
                for grade in grade_cluster:
                    limits[grade][delivery_condition][fine_grain_elements] = limit

        # compose AR 20 Al+Ti
        steel_plate_limit = HullStructureSteelPlateLimit(
            thickness_limit=ThicknessLimit(20),
            fine_grain_elements=('Al', 'Ti')
        )
        map_grade_delivery_condition_and_limit(
            limits=bao_steel_limits.limits,
            grade_cluster_indexes=[0, 1, 2, 3],
            delivery_condition='AR',
            fine_grain_elements=('Al', 'Ti'),
            limit=steel_plate_limit
        )

        # compose N 80 Al+Nb+Ti
        steel_plate_limit = HullStructureSteelPlateLimit(
            thickness_limit=ThicknessLimit(80),
            fine_grain_elements=('Al', 'Nb', 'Ti')
        )
        map_grade_delivery_condition_and_limit(
            limits=bao_steel_limits.limits,
            grade_cluster_indexes=[0, 1, 2, 3, 4],
            delivery_condition='N',
            fine_grain_elements=('Al', 'Nb', 'Ti'),
            limit=steel_plate_limit
        )

        # compose N 100 Al+Nb+Ti+V
        steel_plate_limit = HullStructureSteelPlateLimit(
            thickness_limit=ThicknessLimit(100),
            fine_grain_elements=('Al', 'Nb', 'Ti', 'V')
        )
        map_grade_delivery_condition_and_limit(
            limits=bao_steel_limits.limits,
            grade_cluster_indexes=[6],
            delivery_condition='N',
            fine_grain_elements=('Al', 'Nb', 'Ti', 'V'),
            limit=steel_plate_limit
        )

        # compose NR 40 Al+Nb+Ti
        steel_plate_limit = HullStructureSteelPlateLimit(
            thickness_limit=ThicknessLimit(40),
            fine_grain_elements=('Al', 'Nb', 'Ti')
        )
        map_grade_delivery_condition_and_limit(
            limits=bao_steel_limits.limits,
            grade_cluster_indexes=[0, 1, 2, 3],
            delivery_condition='NR',
            fine_grain_elements=('Al', 'Nb', 'Ti'),
            limit=steel_plate_limit
        )

        # compose TM 50 Al+Ti
        steel_plate_limit = HullStructureSteelPlateLimit(
            thickness_limit=ThicknessLimit(50),
            fine_grain_elements=('Al', 'Ti')
        )
        map_grade_delivery_condition_and_limit(
            limits=bao_steel_limits.limits,
            grade_cluster_indexes=[7],
            delivery_condition='TM',
            fine_grain_elements=('Al', 'Ti'),
            limit=steel_plate_limit
        )

        # compose TM 68 Al+Nb+Ti
        steel_plate_limit = HullStructureSteelPlateLimit(
            thickness_limit=ThicknessLimit(68),
            fine_grain_elements=('Al', 'Nb', 'Ti')
        )
        map_grade_delivery_condition_and_limit(
            limits=bao_steel_limits.limits,
            grade_cluster_indexes=[8],
            delivery_condition='TM',
            fine_grain_elements=('Al', 'Nb', 'Ti'),
            limit=steel_plate_limit
        )

        # compose TM 80 Al+Nb+Ti
        steel_plate_limit = HullStructureSteelPlateLimit(
            thickness_limit=ThicknessLimit(80),
            fine_grain_elements=('Al', 'Nb', 'Ti')
        )
        map_grade_delivery_condition_and_limit(
            limits=bao_steel_limits.limits,
            grade_cluster_indexes=[0, 1, 2, 3, 4],
            delivery_condition='TM',
            fine_grain_elements=('Al', 'Nb', 'Ti'),
            limit=steel_plate_limit
        )

        # compose TM 90 Al+Nb+Ti
        steel_plate_limit = HullStructureSteelPlateLimit(
            thickness_limit=ThicknessLimit(90),
            fine_grain_elements=('Al', 'Nb', 'Ti')
        )
        map_grade_delivery_condition_and_limit(
            limits=bao_steel_limits.limits,
            grade_cluster_indexes=[5],
            delivery_condition='TM',
            fine_grain_elements=('Al', 'Nb', 'Ti'),
            limit=steel_plate_limit
        )

        # alternative limits:
        # compose N 30 Al+Ti, reset Al+Nb+Ti
        steel_plate_limit = HullStructureSteelPlateLimit(
            thickness_limit=ThicknessLimit(30),
            fine_grain_elements=('Al', 'Ti'),
            # reset_elements=['Al', 'Nb', 'Ti']
        )
        map_grade_delivery_condition_and_limit(
            limits=bao_steel_limits.limits,
            grade_cluster_indexes=[0, 1],
            delivery_condition='N',
            fine_grain_elements=('Al', 'Ti'),
            limit=steel_plate_limit
        )

        # compose NR 30 Al+Ti, reset Al+Nb+Ti
        steel_plate_limit = HullStructureSteelPlateLimit(
            thickness_limit=ThicknessLimit(30),
            fine_grain_elements=('Al', 'Ti'),
            # reset_elements=['Al', 'Nb', 'Ti']
        )
        map_grade_delivery_condition_and_limit(
            limits=bao_steel_limits.limits,
            grade_cluster_indexes=[0, 2],
            delivery_condition='NR',
            fine_grain_elements=('Al', 'Ti'),
            limit=steel_plate_limit
        )


class YieldStrengthLimit:

    def __init__(self, minimum: int, limit_type: LimitType = LimitType.MINIMUM, unit: str = 'MPa'):
        self.minimum = minimum
        self.limit_type = limit_type
        self.unit = unit

    def verify(self, value: int) -> Tuple[bool, str]:
        if value >= self.minimum:
            message = f"[PASS] Yield Strength value is {value}, meets the minimum limit {self.minimum} {self.unit}."
            print(message)
            return True, message
        else:
            message = f"[FAIL] Yield Strength value is {value}, violates the minimum limit {self.minimum} {self.unit}."
            print(message)
            return False, message


class TensileStrengthLimit:

    def __init__(self, minimum: int, maximum: int, limit_type: LimitType = LimitType.RANGE, unit: str = 'MPa'):
        self.minimum = minimum
        self.maximum = maximum
        self.limit_type = limit_type
        self.unit = unit

    def verify(self, value: int) -> Tuple[bool, str]:
        if self.minimum <= value <= self.maximum:
            message = (
                f"[PASS] Tensile Strength value is {value}, meets the valid range {self.minimum} - {self.maximum} "
                f"{self.unit}."
            )
            print(message)
            return True, message
        else:
            message = (
                f"[FAIL] Tensile Strength value is {value}, violates the valid range {self.minimum} - {self.maximum} "
                f"{self.unit}."
            )
            print(message)
            return False, message


class ElongationLimit:

    def __init__(self, minimum: int, limit_type: LimitType = LimitType.MINIMUM, unit: str = '%'):
        self.minimum = minimum
        self.limit_type = limit_type
        self.unit = unit

    def verify(self, value: int) -> Tuple[bool, str]:
        if value >= self.minimum:
            message = f"[PASS] Elongation value is {value}, meets the minimum limit {self.minimum} {self.unit}."
            print(message)
            return True, message
        else:
            message = f"[FAIL] Elongation value is {value}, violates the minimum limit {self.minimum} {self.unit}."
            print(message)
            return False, message


class TemperatureLimit:

    def __init__(self, unique_value: int, limit_type: LimitType = LimitType.UNIQUE, unit: str = 'Degrees Celsius'):
        self.unique_value = unique_value
        self.limit_type = limit_type
        self.unit = unit

    def verify(self, value: int) -> Tuple[bool, str]:
        if value == self.unique_value:
            message = f"[PASS] Temperature value is {value}, meets the valid value {self.unique_value} {self.unit}."
            print(message)
            return True, message
        else:
            message = f"[FAIL] Temperature value is {value}, violates the valid value {self.unique_value} {self.unit}."
            print(message)
            return False, message


@unique
class Direction(Enum):
    TRANSVERSE = 'Transverse'  # 横向
    LONGITUDINAL = 'Longitudinal'  # 纵向


class ImpactEnergyLimit:

    def __init__(
        self,
        # thickness_range: Tuple[int, int],
        # direction: Direction,
        minimum: int,
        limit_type: LimitType = LimitType.MINIMUM,
        unit: str = 'J'
    ):
        # self.thickness_range = thickness_range
        # self.direction = direction
        self.minimum = minimum
        self.limit_type = limit_type
        self.unit = unit

    def verify(self, value: int) -> Tuple[bool, str]:
        if value >= self.minimum:
            message = (
                f"[PASS] Impact Energy value is {value}, meets the "
                f"minimum limit {self.minimum} {self.unit}."
            )
            print(message)
            return True, message
        else:
            message = (
                f"[FAIL] Impact Energy value is {value}, meets the "
                f"minimum limit {self.minimum} {self.unit}."
            )
            print(message)
            return False, message


class ImpactEnergyLimits:  # The impact energy limits belong to the same grade

    def __init__(self):
        self.thickness_direction_map: Dict[Tuple[int, int], Dict[Direction, Union[ImpactEnergyLimit, None]]] = {
            (0, 50): {
                Direction.TRANSVERSE: None,
                Direction.LONGITUDINAL: None
            },
            (50, 70): {
                Direction.TRANSVERSE: None,
                Direction.LONGITUDINAL: None
            },
            (70, 150): {
                Direction.TRANSVERSE: None,
                Direction.LONGITUDINAL: None
            }
        }

    def set_limit(
        self,
        thickness_range: Tuple[int, int],
        direction: Direction,
        impact_energy_limit: ImpactEnergyLimit
    ):
        self.thickness_direction_map[thickness_range][direction] = impact_energy_limit

    def get_limit(self, thickness: Union[float, int], direction: Direction) -> ImpactEnergyLimit:
        # limit = None
        if 0 <= thickness <= 50:
            limit = self.thickness_direction_map[(0, 50)][direction]
        elif 50 < thickness <= 70:
            limit = self.thickness_direction_map[(50, 70)][direction]
        elif 70 < thickness <= 150:
            limit = self.thickness_direction_map[(70, 150)][direction]
        else:
            raise ValueError(
                f"The thickness value {thickness} is out of the predefined acceptable range 0 - 150 mm."
            )
        if limit is None:
            raise ValueError(
                f"Could not impact energy limit for thickness {thickness}, direction {direction}."
            )
        else:
            return limit


class MechanicalLimit:

    def __init__(self, grade: str):
        self.grade = grade
        self.yield_strength_limit: Union[YieldStrengthLimit, None] = None
        self.tensile_strength_limit: Union[TensileStrengthLimit, None] = None
        self.elongation_limit: Union[ElongationLimit, None] = None
        self.temperature_limit: Union[TemperatureLimit, None] = None
        self.impact_energy_limits: Union[ImpactEnergyLimits, None] = None


class MechanicalLimits:

    # ################################ Singleton ################################ #
    _singleton = None

    @classmethod
    def get_singleton(cls):
        if not isinstance(cls._singleton, cls):
            cls._singleton = cls()
        return cls._singleton
    # ################################ Singleton ################################ #

    def __init__(self):
        self.grade_mechanical_limits_map = dict()
        self.grade_clusters = [
            [
                'VL A27S',
                'VL D27S',
                'VL E27S',
                'VL F27S'
            ],
            [
                'VL A32',
                'VL D32',
                'VL E32',
                'VL F32'
            ],
            [
                'VL A36',
                'VL D36',
                'VL E36',
                'VL F36'
            ],
            [
                'VL A40',
                'VL D40',
                'VL E40',
                'VL F40'
            ]
        ]
        for cluster in self.grade_clusters:
            for grade in cluster:
                self.grade_mechanical_limits_map[grade] = MechanicalLimit(grade)
        self.compose_limits()

    def compose_limits(self):
        # VL A27S, VL D27S, VL E27S, VL F27S
        for grade in self.grade_clusters[0]:
            self.grade_mechanical_limits_map[grade].yield_strength_limit = YieldStrengthLimit(minimum=265)
            self.grade_mechanical_limits_map[grade].tensile_strength_limit = TensileStrengthLimit(minimum=400,
                                                                                                  maximum=530)
            self.grade_mechanical_limits_map[grade].elongation_limit = ElongationLimit(minimum=22)
            impact_energy_limits = ImpactEnergyLimits()
            impact_energy_limits.set_limit(
                thickness_range=(0, 50),
                direction=Direction.LONGITUDINAL,
                impact_energy_limit=ImpactEnergyLimit(minimum=27)
            )
            impact_energy_limits.set_limit(
                thickness_range=(0, 50),
                direction=Direction.TRANSVERSE,
                impact_energy_limit=ImpactEnergyLimit(minimum=20)
            )
            impact_energy_limits.set_limit(
                thickness_range=(50, 70),
                direction=Direction.LONGITUDINAL,
                impact_energy_limit=ImpactEnergyLimit(minimum=34)
            )
            impact_energy_limits.set_limit(
                thickness_range=(50, 70),
                direction=Direction.TRANSVERSE,
                impact_energy_limit=ImpactEnergyLimit(minimum=24)
            )
            impact_energy_limits.set_limit(
                thickness_range=(70, 150),
                direction=Direction.LONGITUDINAL,
                impact_energy_limit=ImpactEnergyLimit(minimum=41)
            )
            impact_energy_limits.set_limit(
                thickness_range=(70, 150),
                direction=Direction.TRANSVERSE,
                impact_energy_limit=ImpactEnergyLimit(minimum=27)
            )
            self.grade_mechanical_limits_map[grade].impact_energy_limits = impact_energy_limits

        # VL A32, VL D32, VL E32, VL F32
        for grade in self.grade_clusters[1]:
            self.grade_mechanical_limits_map[grade].yield_strength_limit = YieldStrengthLimit(minimum=315)
            self.grade_mechanical_limits_map[grade].tensile_strength_limit = TensileStrengthLimit(minimum=440,
                                                                                                  maximum=570)
            self.grade_mechanical_limits_map[grade].elongation_limit = ElongationLimit(minimum=22)
            impact_energy_limits = ImpactEnergyLimits()
            impact_energy_limits.set_limit(
                thickness_range=(0, 50),
                direction=Direction.LONGITUDINAL,
                impact_energy_limit=ImpactEnergyLimit(minimum=31)
            )
            impact_energy_limits.set_limit(
                thickness_range=(0, 50),
                direction=Direction.TRANSVERSE,
                impact_energy_limit=ImpactEnergyLimit(minimum=22)
            )
            impact_energy_limits.set_limit(
                thickness_range=(50, 70),
                direction=Direction.LONGITUDINAL,
                impact_energy_limit=ImpactEnergyLimit(minimum=38)
            )
            impact_energy_limits.set_limit(
                thickness_range=(50, 70),
                direction=Direction.TRANSVERSE,
                impact_energy_limit=ImpactEnergyLimit(minimum=26)
            )
            impact_energy_limits.set_limit(
                thickness_range=(70, 150),
                direction=Direction.LONGITUDINAL,
                impact_energy_limit=ImpactEnergyLimit(minimum=46)
            )
            impact_energy_limits.set_limit(
                thickness_range=(70, 150),
                direction=Direction.TRANSVERSE,
                impact_energy_limit=ImpactEnergyLimit(minimum=31)
            )
            self.grade_mechanical_limits_map[grade].impact_energy_limits = impact_energy_limits

        # VL A36, VL D36, VL E36, VL F36
        for grade in self.grade_clusters[2]:
            self.grade_mechanical_limits_map[grade].yield_strength_limit = YieldStrengthLimit(minimum=355)
            self.grade_mechanical_limits_map[grade].tensile_strength_limit = TensileStrengthLimit(minimum=490,
                                                                                                  maximum=630)
            self.grade_mechanical_limits_map[grade].elongation_limit = ElongationLimit(minimum=21)
            impact_energy_limits = ImpactEnergyLimits()
            impact_energy_limits.set_limit(
                thickness_range=(0, 50),
                direction=Direction.LONGITUDINAL,
                impact_energy_limit=ImpactEnergyLimit(minimum=34)
            )
            impact_energy_limits.set_limit(
                thickness_range=(0, 50),
                direction=Direction.TRANSVERSE,
                impact_energy_limit=ImpactEnergyLimit(minimum=24)
            )
            impact_energy_limits.set_limit(
                thickness_range=(50, 70),
                direction=Direction.LONGITUDINAL,
                impact_energy_limit=ImpactEnergyLimit(minimum=41)
            )
            impact_energy_limits.set_limit(
                thickness_range=(50, 70),
                direction=Direction.TRANSVERSE,
                impact_energy_limit=ImpactEnergyLimit(minimum=27)
            )
            impact_energy_limits.set_limit(
                thickness_range=(70, 150),
                direction=Direction.LONGITUDINAL,
                impact_energy_limit=ImpactEnergyLimit(minimum=50)
            )
            impact_energy_limits.set_limit(
                thickness_range=(70, 150),
                direction=Direction.TRANSVERSE,
                impact_energy_limit=ImpactEnergyLimit(minimum=34)
            )
            self.grade_mechanical_limits_map[grade].impact_energy_limits = impact_energy_limits

        # VL A27S, VL D27S, VL E27S, VL F27S
        for grade in self.grade_clusters[3]:
            self.grade_mechanical_limits_map[grade].yield_strength_limit = YieldStrengthLimit(minimum=390)
            self.grade_mechanical_limits_map[grade].tensile_strength_limit = TensileStrengthLimit(minimum=510,
                                                                                                  maximum=660)
            self.grade_mechanical_limits_map[grade].elongation_limit = ElongationLimit(minimum=20)
            impact_energy_limits = ImpactEnergyLimits()
            impact_energy_limits.set_limit(
                thickness_range=(0, 50),
                direction=Direction.LONGITUDINAL,
                impact_energy_limit=ImpactEnergyLimit(minimum=39)
            )
            impact_energy_limits.set_limit(
                thickness_range=(0, 50),
                direction=Direction.TRANSVERSE,
                impact_energy_limit=ImpactEnergyLimit(minimum=26)
            )
            impact_energy_limits.set_limit(
                thickness_range=(50, 70),
                direction=Direction.LONGITUDINAL,
                impact_energy_limit=ImpactEnergyLimit(minimum=46)
            )
            impact_energy_limits.set_limit(
                thickness_range=(50, 70),
                direction=Direction.TRANSVERSE,
                impact_energy_limit=ImpactEnergyLimit(minimum=31)
            )
            impact_energy_limits.set_limit(
                thickness_range=(70, 150),
                direction=Direction.LONGITUDINAL,
                impact_energy_limit=ImpactEnergyLimit(minimum=55)
            )
            impact_energy_limits.set_limit(
                thickness_range=(70, 150),
                direction=Direction.TRANSVERSE,
                impact_energy_limit=ImpactEnergyLimit(minimum=37)
            )
            self.grade_mechanical_limits_map[grade].impact_energy_limits = impact_energy_limits

        # Temperature limits
        for cluster in self.grade_clusters:
            for grade in cluster:
                if grade.startswith('VL A'):
                    self.grade_mechanical_limits_map[grade].temperature_limit = TemperatureLimit(unique_value=0)
                elif grade.startswith('VL D'):
                    self.grade_mechanical_limits_map[grade].temperature_limit = TemperatureLimit(unique_value=-20)
                elif grade.startswith('VL E'):
                    self.grade_mechanical_limits_map[grade].temperature_limit = TemperatureLimit(unique_value=-40)
                elif grade.startswith('VL F'):
                    self.grade_mechanical_limits_map[grade].temperature_limit = TemperatureLimit(unique_value=-60)
                else:
                    raise ValueError(
                        f"The grade value {grade} hasn't been registered as a grade for high strength steel."
                    )

    def verify(
        self,
        grade: str,
        thickness: Union[float, int],
        direction: Direction,
        yield_strength: YieldStrength,
        tensile_strength: TensileStrength,
        elongation: Elongation,
        temperature: Temperature,
        impact_energy_list: List[ImpactEnergy]
    ) -> bool:
        all_pass_flag = True
        mechanical_limit = self.grade_mechanical_limits_map[grade]
        # verify yield strength
        yield_strength.valid_flag, yield_strength.message = mechanical_limit.yield_strength_limit.verify(
            yield_strength.value)
        all_pass_flag = all_pass_flag and yield_strength.valid_flag
        # verify tensile strength
        tensile_strength.valid_flag, tensile_strength.message = mechanical_limit.tensile_strength_limit.verify(
            tensile_strength.value
        )
        all_pass_flag = all_pass_flag and tensile_strength.valid_flag
        # verify elongation
        elongation.valid_flag, elongation.message = mechanical_limit.elongation_limit.verify(
            elongation.value
        )
        all_pass_flag = all_pass_flag and elongation.valid_flag
        # verify temperature
        temperature.valid_flag, temperature.message = mechanical_limit.temperature_limit.verify(
            temperature.value
        )
        all_pass_flag = all_pass_flag and temperature.valid_flag
        # verify impact energy
        impact_energy_limit = mechanical_limit.impact_energy_limits.get_limit(thickness=thickness, direction=direction)
        for impact_energy in impact_energy_list:
            impact_energy.valid_flag, impact_energy.message = impact_energy_limit.verify(impact_energy.value)
            all_pass_flag = all_pass_flag and impact_energy.valid_flag

        return all_pass_flag


# class CertificateVerification:
#

#
#     # chemical composition limits for high strength steel
#     chemical_composition_limits_for_high_strength_steel = {
#         0: {
#             'normal': {
#                 'C': {
#                     'type': 'maximum',
#                     'limit': 0.18
#                 },
#                 'Si': {
#                     'type': 'maximum',
#                     'limit': 0.50
#                 },
#                 'Mn': {
#                     'type': 'range',
#                     'minimum': 0.70,
#                     'maximum': 1.60
#                 }
#             }
#         },
#         1: {
#             'normal': {
#                 'C': {
#                     'type': 'maximum',
#                     'limit': 0.18
#                 },
#                 'Si': {
#                     'type': 'maximum',
#                     'limit': 0.50
#                 },
#                 'Mn': {
#                     'type': 'range',
#                     'minimum': 0.90,
#                     'maximum': 1.60
#                 },
#                 'P': {
#                     'type': 'maximum',
#                     'limit': 0.035
#                 },
#                 'S': {
#                     'type': 'maximum',
#                     'limit': 0.035
#                 },
#                 'Cr': {
#                     'type': 'maximum',
#                     'limit': 0.20
#                 },
#                 'Mo': {
#                     'type': 'maximum',
#                     'limit': 0.08
#                 },
#                 'Ni': {
#                     'type': 'maximum',
#                     'limit': 0.40
#                 }
#             },
#             'special': {
#                 'Cu': {
#                     'type': 'maximum',
#                     'limit': 0.35
#                 },
#                 'Al': {
#                     'type': 'minimum',
#                     'limit': 0.020
#                 },
#                 'Nb': {
#                     'type': 'range',
#                     'minimum': 0.02,
#                     'maximum': 0.05
#                 },
#                 'V': {
#                     'type': 'range',
#                     'minimum': 0.05,
#                     'maximum': 0.10
#                 },
#                 'Ti': {
#                     'type': 'range',
#                     'minimum': 0.007,
#                     'maximum': 0.02
#                 }
#             }
#         }
#     }
#
#     grade_chemical_limits_map = {
#         'VL A36': chemical_composition_limits_for_high_strength_steel[1],
#         'VL D32': chemical_composition_limits_for_high_strength_steel[1]
#     }
#
#     steel_plant_specific_rules = {
#         0: {
#
#         },
#         1: {
#             'TM': {
#                 'thickness': {
#                     'type': 'maximum',
#                     'limit': 80,
#                     'unit': 'mm'
#                 },
#                 'fine_grain_elements': ['Al', 'Nb', 'Ti']
#             },
#             'NR': {
#                 'thickness': {
#                     'type': 'maximum',
#                     'limit': 40,
#                     'unit': 'mm'
#                 },
#                 'fine_grain_elements': ['Al', 'Nb', 'Ti']
#             },
#             'N': {
#                 'thickness': {
#                     'type': 'maximum',
#                     'limit': 80,
#                     'unit': 'mm'
#                 },
#                 'fine_grain_elements': ['Al', 'Nb', 'Ti'],
#                 'alternative': {
#                     'thickness': {
#                         'type': 'maximum',
#                         'limit': 30,
#                         'unit': 'mm'
#                     },
#                     'fine_grain_elements': ['Al', 'Ti'],
#                 }
#             },
#             'AR': {
#                 'thickness': {
#                     'type': 'maximum',
#                     'limit': 20,
#                     'unit': 'mm'
#                 },
#                 'fine_grain_elements': ['Al', 'Ti']
#             }
#         },
#         2: {
#             'TM': {
#                 'thickness': {
#                     'type': 'maximum',
#                     'limit': 80,
#                     'unit': 'mm'
#                 },
#                 'fine_grain_elements': ['Al', 'Nb', 'Ti']
#             },
#             'NR': {
#                 'thickness': {
#                     'type': 'maximum',
#                     'limit': 40,
#                     'unit': 'mm'
#                 },
#                 'fine_grain_elements': ['Al', 'Nb', 'Ti'],
#                 'alternative': {
#                     'thickness': {
#                         'type': 'maximum',
#                         'limit': 30,
#                         'unit': 'mm'
#                     },
#                     'fine_grain_elements': ['Al', 'Ti']
#                 }
#             },
#             'N': {
#                 'thickness': {
#                     'type': 'maximum',
#                     'limit': 80,
#                     'unit': 'mm'
#                 },
#                 'fine_grain_elements': ['Al', 'Nb', 'Ti']
#             },
#             'AR': {
#                 'thickness': {
#                     'type': 'maximum',
#                     'limit': 20,
#                     'unit': 'mm'
#                 },
#                 'fine_grain_elements': ['Al', 'Ti']
#             }
#         }
#     }
#
#     plant_grade_specific_rule_map = {
#         'BAOSHAN IRON & STEEL CO., LTD.': {
#             'VL D27S': steel_plant_specific_rules[1],
#             'VL D32': steel_plant_specific_rules[1],
#             'VL A36': steel_plant_specific_rules[2]
#         }
#     }
#
#     TM_Ceq_limits = {
#         'VL D32': {
#
#         }
#     }
