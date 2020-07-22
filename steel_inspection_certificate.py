# import fire
import os
import shutil

import pdfplumber
from common_utils import TableSearchType, CommonUtils
from certificate_verification import ChemicalCompositionLimitsForHighStrengthSteel, HullStructureSteelPlateLimits, \
    MechanicalLimits
from certificate_element import SteelPlant, Specification, Thickness, SerialNumber, SteelPlate, ChemicalElement, \
    ChemicalElementValue, DeliveryCondition, YieldStrength, TensileStrength, Elongation, PositionDirectionImpact, \
    Temperature, ImpactEnergy


class SteelInspecitionCertificate:

    def __init__(self, path):
        # Read PDF contents
        self.pdf_path = path
        self.pdf = pdfplumber.open(path)
        self.page = self.pdf.pages[0]  # Always has only one page
        self.tables = self.page.extract_tables()
        self.content = self.page.extract_text()

        self.steel_plant = None
        self.specification = None
        self.thickness = None
        self.serial_numbers = None
        self.plates = None
        self.chemical_elements = None

    def extract_quality_date(self):
        # Extract quality data
        self.steel_plant = self.extract_steel_plant()
        self.specification = self.extract_specification()
        self.thickness = self.extract_thickness()
        self.serial_numbers = self.extract_serial_numbers()
        self.plates = []
        for serial_number in self.serial_numbers.value:
            self.plates.append(SteelPlate(serial_number))
        self.chemical_elements = None
        self.extract_chemical_composition()
        self.extract_delivery_condition()
        self.extract_yield_strength()
        self.extract_tensile_strength()
        self.extract_elongation()
        self.extract_position_direction_impact()
        self.extract_temperature()
        self.extract_impact_energy()

    def __del__(self):
        self.pdf.close()

    def close_pdf(self):
        self.pdf.close()

    # def page_info(self):
    #     print(self.page.page_number)
    #     print(self.page.width)
    #     print(self.page.height)

    def extract_steel_plant(self):
        if "No.885 Fujin ROAD, BAOSHAN DISTRICT".replace(" ", "").upper() in self.content.replace(" ", "").upper():
            return SteelPlant('BAOSHAN IRON & STEEL CO., LTD.')

    def extract_specification(self):
        # Hardcode here, the specification information is always in the first table:
        table_index = 0
        table = self.tables[table_index]
        # 遍历这张表格
        coordinates = CommonUtils.search_table(table, 'SPECIFICATION')
        if coordinates is None:
            raise ValueError(
                f"Could not find text 'SPECIFICATION' in the given PDF {self.pdf_path}."
            )

        # specification的value一般应该在title右边一格
        x_coordinate = coordinates[0]
        y_coordinate = coordinates[1] + 1
        specification_value = table[x_coordinate][y_coordinate]
        if specification_value is None:
            # 如果标准值不在对应格子里，则可能是都挤在同列的第一行，用\n分隔
            specification_value = table[0][coordinates[1] + 1].split('\n')[
                coordinates[0]].strip()
        if specification_value is None:
            raise ValueError(
                f"The value of 'SPECIFICATION' could not be found in the given PDF {self.pdf_path}."
            )
        if specification_value.startswith('DNV GL'):
            pass
        else:
            raise ValueError(
                f"The specification value should start with 'DNV GL', but the value {specification_value} extracted "
                f"from the given PDF {self.pdf_path} doesn't."
            )
        # Verify the specification_value by searching the same value in extracted text
        if specification_value in self.content:
            pass
        else:
            raise ValueError(
                f"The specification value {specification_value} extracted from table could not be found in the "
                f"extracted text, might be wrong."
            )
        # Tailor the value to meet the standard specification type
        specification_value = specification_value.replace('DNV GL', '').strip()
        return Specification(
            table_index=table_index,
            x_coordinate=x_coordinate,
            y_coordinate=y_coordinate,
            value=specification_value
        )

    def extract_serial_numbers(self):
        # Hard code: the number is always in the second table
        table_index = 1
        table = self.tables[table_index]
        # 通常NO.都应该在[0, 0]的位置上
        coordinates = CommonUtils.search_table(table, 'NO.', confirmed_row=0, confirmed_col=0)
        if coordinates is None:
            raise ValueError(
                f"Text 'NO.' could not be found in the given PDF {self.pdf_path}."
            )
        # 序号一般都在同一列，但是行数不确定需要遍历
        coordinates = CommonUtils.search_table(table, keyword=None, confirmed_col=0,
                                               search_type=TableSearchType.SPLIT_LINE_BREAK_ALL_DIGIT)
        if coordinates is None:
            raise ValueError(
                f"Could not find NO. value in the given PDF {self.pdf_path}."
            )
        x_coordinate = coordinates[0]
        y_coordinate = coordinates[1]
        serial_numbers = [number.strip() for number in
                          table[x_coordinate][y_coordinate].split('\n')]
        return SerialNumber(table_index=table_index, x_coordinate=x_coordinate, y_coordinate=y_coordinate,
                            value=serial_numbers)

    def extract_thickness(self):
        # Hard code: the number is always in the second table
        table_index = 1
        table = self.tables[table_index]
        # To get the value of thickness we need to find the cell startswith THICKNESS
        coordinates = CommonUtils.search_table(table, 'THICKNESS', search_type=TableSearchType.SPLIT_LINE_BREAK_START)
        if coordinates is None:
            raise ValueError(
                f"Text 'THICKNESS' could not be found in the given PDF {self.pdf_path}."
            )
        x_coordinate = coordinates[0]
        y_coordinate = coordinates[1]
        thickness_value = table[x_coordinate][y_coordinate].split('\n')[1].strip()
        if len(thickness_value) == 0:
            raise ValueError(
                f"Thickness value could not be found in the Thickness cell."
            )
        try:
            thickness_value = float(thickness_value)
        except ValueError:
            raise ValueError(
                f"The extracted thickness value {thickness_value} could not be converted to a float number."
            )
        return Thickness(
            table_index=table_index,
            x_coordinate=x_coordinate,
            y_coordinate=y_coordinate,
            value=thickness_value
        )

    def extract_chemical_composition(self):
        # HARD CODE: the information of chemical compositions is always in the second table.
        table_index = 1
        table = self.tables[table_index]

        # To locate the positions of the chemical composition cells, we need to find the row with both Notes *1 and *3
        # The chemical composition area starts at that row for 4 rows, and the columns are between the two notes.

        # Search Note '*1'
        coordinates = CommonUtils.search_table(table, '*1')
        if coordinates is None:
            raise ValueError(
                f"Could not find text '*1' in the given PDF {self.pdf_path}"
            )
        # If *1 is found, we can determine the index of the first row, and the columns start from the next column.
        start_row_index = coordinates[0]
        start_col_index = coordinates[1] + 1
        # If *1 is found, we need to check if *3 is at the same row,
        # so that we can determine the right boundary of the columns.
        coordinates = CommonUtils.search_table(table, '*3', confirmed_row=start_row_index)
        if coordinates is None:
            raise ValueError(
                f"Could not find text '*3' in the given PDF {self.pdf_path}"
            )
        # Now we find '*3' at the same row, we can determine the right boundary of the columns.
        end_col_index = coordinates[1]

        # There are two rows of chemical element names
        chemical_composition_name_area = [
            table[start_row_index][start_col_index: end_col_index],
            table[start_row_index + 2][start_col_index: end_col_index]
        ]
        chemical_composition_precision_area = [
            table[start_row_index + 1][start_col_index: end_col_index],
            table[start_row_index + 3][start_col_index: end_col_index]
        ]

        chemical_elements = dict()
        col_counter = dict()
        for row_index, element_seq in enumerate(chemical_composition_name_area):
            for col_index, cell in enumerate(element_seq):
                if cell is not None and cell.strip() in CommonUtils.chemical_elements_table:
                    chemical_element_name = cell.strip()
                    # get the corresponding precision value
                    chemical_element_precision = chemical_composition_precision_area[row_index][col_index]
                    if chemical_element_precision is None:
                        raise ValueError(
                            f"The corresponding precision value for chemical element {chemical_element_name} could not "
                            f"be found in the given PDF {self.pdf_path}"
                        )
                    else:
                        chemical_element_precision = chemical_element_precision.strip()
                        if chemical_element_precision.isdigit():
                            chemical_element_precision = int(chemical_element_precision)
                        else:
                            raise ValueError(
                                f"The extracted precision value {chemical_element_precision} for chemical element "
                                f"{chemical_element_name} is not a digit. The given PDF is {self.pdf_path}"
                            )
                    x_coordinate = start_row_index + row_index * 2
                    y_coordinate = start_col_index + col_index
                    chemical_elements[chemical_element_name] = ChemicalElement(
                        table_index=table_index,
                        x_coordinate=x_coordinate,
                        y_coordinate=y_coordinate,
                        row_index=row_index,
                        value=chemical_element_name,
                        precision=chemical_element_precision
                    )
                    if start_col_index + col_index in col_counter:
                        col_counter[start_col_index + col_index] += 1
                    else:
                        col_counter[start_col_index + col_index] = 1

        self.chemical_elements = chemical_elements

        # Start extracting the chemical composition values for each plate
        for plate_index in range(self.serial_numbers.length):
            # Extract value for each chemical element
            for _element in self.chemical_elements:
                # To locate the cell containing the value for the element, we need to get its x-coordinate
                # which is the x-coordinate of the numbers
                x_coordinate = self.serial_numbers.x_coordinate
                # y-coordinate is the same of the chemical element name.
                y_coordinate = self.chemical_elements[_element].y_coordinate
                cell = table[x_coordinate][y_coordinate]
                # then we need to locate the index of the digit inside the cell
                idx = self.chemical_elements[_element].row_index + plate_index * col_counter[y_coordinate]
                chemical_element_value = cell.split('\n')[idx].strip()
                if chemical_element_value.isdigit():
                    chemical_element_value = int(chemical_element_value)
                else:
                    raise ValueError(
                        f"The value {chemical_element_value} extracted for chemical element {_element} is not a digit! "
                        f"The given PDF is {self.pdf_path}"
                    )
                self.plates[plate_index].chemical_compositions[_element] = ChemicalElementValue(
                    table_index=table_index,
                    x_coordinate=x_coordinate,
                    y_coordinate=y_coordinate,
                    value=chemical_element_value,
                    index=idx,
                    element=_element,
                    precision=self.chemical_elements[_element].precision
                )

    def extract_delivery_condition(self):
        # To extract the delivery condition value, we need its coordinates. The row index is easy to get, because
        # it is the same with the entity. The col index is the same with the delivery condition (with Note *9) title.

        # HARD CODE: the information of delivery condition is always in the second table.
        table_index = 1
        table = self.tables[table_index]

        # Search *9 to get the col index
        coordinates = CommonUtils.search_table(table, '*9')
        if coordinates is None:
            raise ValueError(
                f"Could not find delivery condition (plus *9) title in the given PDF {self.pdf_path}."
            )

        y_coordinate = coordinates[1]
        x_coordinate = self.serial_numbers.x_coordinate

        cell = table[x_coordinate][y_coordinate]

        if cell is None or len(cell.strip()) == 0:
            raise ValueError(
                f"Could not find delivery condition value in the given PDF {self.pdf_path}."
            )

        cell_line_count = len(cell.split('\n'))
        if cell_line_count == self.serial_numbers.length:
            pass
        else:
            raise ValueError(
                f"There are {cell_line_count} lines in the delivery condition cell, but there are "
                f"{self.serial_numbers.length} plates in the given PDF {self.pdf_path}"
            )
        delivery_condition_cell_lines = cell.split('\n')

        # Start extracting the delivery condition value for each plate
        for plate_index in range(self.serial_numbers.length):
            delivery_condition_value = delivery_condition_cell_lines[plate_index]
            if delivery_condition_value is not None and len(delivery_condition_value.strip()) > 0:
                delivery_condition_value = delivery_condition_value.strip()
            else:
                raise ValueError(
                    f"Could not find the delivery condition value for plate No. "
                    f"{self.serial_numbers.value[plate_index]} in the given PDF {self.pdf_path}"
                )
            if delivery_condition_value.isalpha():
                pass
            else:
                raise ValueError(
                    f"The delivery condition value {delivery_condition_value} extracted for plate No. "
                    f"{self.serial_numbers.value[plate_index]} is not purely composed of alphabets in the given "
                    f"PDF {self.pdf_path}"
                )
            # print(
            #     f"delivery condition value: {delivery_condition_value} for plate No. "
            #     f"{self.numbers['numbers'][plate_index]}."
            # )
            self.plates[plate_index].delivery_condition = DeliveryCondition(
                table_index=table_index,
                x_coordinate=x_coordinate,
                y_coordinate=y_coordinate,
                index=plate_index,
                value=delivery_condition_value
            )

    def extract_yield_strength(self):
        # Firstly, hardcode that yield strength data is always in the second table
        table_index = 1
        table = self.tables[table_index]

        # Search the title Y.S. to locate the y coordinate
        coordinates = CommonUtils.search_table(table, 'Y.S.')
        if coordinates is None:
            raise ValueError(
                f"Could not find Y.S. (Yield Strength) title in the given PDF {self.pdf_path}."
            )
        y_coordinate = coordinates[1]
        # x coordinate is the same of the serial numbers
        x_coordinate = self.serial_numbers.x_coordinate

        cell = table[x_coordinate][y_coordinate]

        cell_line_count = len(cell.split('\n'))
        if cell_line_count >= self.serial_numbers.length:
            pass
        else:
            raise ValueError(
                f"There are {cell_line_count} lines in the delivery condition cell, less than the serial numbers count "
                f"{self.serial_numbers.length} plates in the given PDF {self.pdf_path}"
            )
        yield_strength_cell_lines = cell.split('\n')

        # Start extracting the yield strength value for each plate
        for plate_index in range(self.serial_numbers.length):
            yield_strength_value = yield_strength_cell_lines[plate_index]
            if yield_strength_value is not None and len(yield_strength_value.strip()) > 0:
                yield_strength_value = yield_strength_value.strip()
            else:
                raise ValueError(
                    f"Could not find the yield strength value for plate No. "
                    f"{self.serial_numbers.value[plate_index]} in the given PDF {self.pdf_path}"
                )
            if yield_strength_value.isdigit():
                yield_strength_value = int(yield_strength_value)
                pass
            else:
                raise ValueError(
                    f"The yield strength value {yield_strength_value} extracted for plate No. "
                    f"{self.serial_numbers.value[plate_index]} is not a number in the given "
                    f"PDF {self.pdf_path}"
                )
            self.plates[plate_index].yield_strength = YieldStrength(
                table_index=table_index,
                x_coordinate=x_coordinate,
                y_coordinate=y_coordinate,
                index=plate_index,
                value=yield_strength_value
            )

    def extract_tensile_strength(self):
        # Firstly, hardcode that tensile strength data is always in the second table
        table_index = 1
        table = self.tables[table_index]

        # Search the title T.S. to locate the y coordinate
        coordinates = CommonUtils.search_table(table, 'T.S.')
        if coordinates is None:
            raise ValueError(
                f"Could not find T.S. (Tensile Strength) title in the given PDF {self.pdf_path}."
            )
        y_coordinate = coordinates[1]
        # x coordinate is the same of the serial numbers
        x_coordinate = self.serial_numbers.x_coordinate

        cell = table[x_coordinate][y_coordinate]

        cell_line_count = len(cell.split('\n'))
        if cell_line_count >= self.serial_numbers.length:
            pass
        else:
            raise ValueError(
                f"There are {cell_line_count} lines in the tensile strength cell, less than the serial numbers count "
                f"{self.serial_numbers.length} plates in the given PDF {self.pdf_path}"
            )
        tensile_strength_cell_lines = cell.split('\n')

        # Start extracting the tensile strength value for each plate
        for plate_index in range(self.serial_numbers.length):
            tensile_strength_value = tensile_strength_cell_lines[plate_index]
            if tensile_strength_value is not None and len(tensile_strength_value.strip()) > 0:
                tensile_strength_value = tensile_strength_value.strip()
            else:
                raise ValueError(
                    f"Could not find the tensile strength value for plate No. "
                    f"{self.serial_numbers.value[plate_index]} in the given PDF {self.pdf_path}"
                )
            if tensile_strength_value.isdigit():
                tensile_strength_value = int(tensile_strength_value)
                pass
            else:
                raise ValueError(
                    f"The tensile strength value {tensile_strength_value} extracted for plate No. "
                    f"{self.serial_numbers.value[plate_index]} is not a number in the given "
                    f"PDF {self.pdf_path}"
                )
            self.plates[plate_index].tensile_strength = TensileStrength(
                table_index=table_index,
                x_coordinate=x_coordinate,
                y_coordinate=y_coordinate,
                index=plate_index,
                value=tensile_strength_value
            )

    def extract_elongation(self):
        # Firstly, hardcode that tensile strength data is always in the second table
        table_index = 1
        table = self.tables[table_index]

        # Search the title EL. to locate the y coordinate
        coordinates = CommonUtils.search_table(table, 'EL')
        if coordinates is None:
            raise ValueError(
                f"Could not find EL (Elongation) title in the given PDF {self.pdf_path}."
            )
        y_coordinate = coordinates[1]
        # x coordinate is the same of the serial numbers
        x_coordinate = self.serial_numbers.x_coordinate

        cell = table[x_coordinate][y_coordinate]

        cell_line_count = len(cell.split('\n'))
        if cell_line_count >= self.serial_numbers.length:
            pass
        else:
            raise ValueError(
                f"There are {cell_line_count} lines in the elongation cell, less than the serial numbers count "
                f"{self.serial_numbers.length} plates in the given PDF {self.pdf_path}"
            )
        elongation_cell_lines = cell.split('\n')

        # Start extracting the elongation value for each plate
        for plate_index in range(self.serial_numbers.length):
            elongation_value = elongation_cell_lines[plate_index]
            if elongation_value is not None and len(elongation_value.strip()) > 0:
                elongation_value = elongation_value.strip()
            else:
                raise ValueError(
                    f"Could not find the elongation value for plate No. "
                    f"{self.serial_numbers.value[plate_index]} in the given PDF {self.pdf_path}"
                )
            if elongation_value.isdigit():
                elongation_value = int(elongation_value)
                pass
            else:
                raise ValueError(
                    f"The elongation value {elongation_value} extracted for plate No. "
                    f"{self.serial_numbers.value[plate_index]} is not a number in the given "
                    f"PDF {self.pdf_path}"
                )
            self.plates[plate_index].elongation = Elongation(
                table_index=table_index,
                x_coordinate=x_coordinate,
                y_coordinate=y_coordinate,
                index=plate_index,
                value=elongation_value
            )

    def extract_position_direction_impact(self):
        # Firstly, hardcode that tensile strength data is always in the second table
        table_index = 1
        table = self.tables[table_index]

        # Search the title IMPACTTEST to locate the y coordinate
        coordinates = CommonUtils.search_table(table, 'IMPACTTEST',
                                               search_type=TableSearchType.REMOVE_LINE_BREAK_CONTAIN)
        if coordinates is None:
            raise ValueError(
                f"Could not find IMPACT TEST title in the given PDF {self.pdf_path}."
            )
        y_coordinate = coordinates[1]
        # x coordinate is the same of the serial numbers
        x_coordinate = self.serial_numbers.x_coordinate

        cell = table[x_coordinate][y_coordinate]

        cell_line_count = len(cell.split('\n'))
        if cell_line_count >= self.serial_numbers.length:
            pass
        else:
            raise ValueError(
                f"There are {cell_line_count} lines in the position direction (impact test) cell, less than "
                f"the serial numbers count {self.serial_numbers.length} plates in the given PDF {self.pdf_path}"
            )
        position_direction_cell_lines = cell.split('\n')

        # Start extracting the elongation value for each plate
        for plate_index in range(self.serial_numbers.length):
            position_direction_value = position_direction_cell_lines[plate_index]
            if position_direction_value is not None and len(position_direction_value.strip()) > 0:
                position_direction_value = position_direction_value.strip()
            else:
                raise ValueError(
                    f"Could not find the position direction (impact test) value for plate No. "
                    f"{self.serial_numbers.value[plate_index]} in the given PDF {self.pdf_path}"
                )
            if position_direction_value.isalnum():
                pass
            else:
                raise ValueError(
                    f"The position direction (impact test) value {position_direction_value} extracted for plate No. "
                    f"{self.serial_numbers.value[plate_index]} contains invalid character other than alphabet and "
                    f"number in the given PDF {self.pdf_path}"
                )
            self.plates[plate_index].position_direction_impact = PositionDirectionImpact(
                table_index=table_index,
                x_coordinate=x_coordinate,
                y_coordinate=y_coordinate,
                index=plate_index,
                value=position_direction_value
            )

    def extract_temperature(self):
        # Firstly, hardcode that tensile strength data is always in the second table
        table_index = 1
        table = self.tables[table_index]

        # Search the title TEMP to locate the y coordinate
        coordinates = CommonUtils.search_table(table, 'TEMP')
        if coordinates is None:
            raise ValueError(
                f"Could not find TEMP (Temperature) title in the given PDF {self.pdf_path}."
            )
        y_coordinate = coordinates[1]
        # x coordinate is the same of the serial numbers
        x_coordinate = self.serial_numbers.x_coordinate

        cell = table[x_coordinate][y_coordinate]

        cell_line_count = len(cell.split('\n'))
        if cell_line_count >= self.serial_numbers.length:
            pass
        else:
            raise ValueError(
                f"There are {cell_line_count} lines in the temperature cell, less than "
                f"the serial numbers count {self.serial_numbers.length} plates in the given PDF {self.pdf_path}"
            )
        temperature_cell_lines = cell.split('\n')

        # Start extracting the elongation value for each plate
        for plate_index in range(self.serial_numbers.length):
            temperature_value = temperature_cell_lines[plate_index]
            if temperature_value is not None and len(temperature_value.strip()) > 0:
                temperature_value = temperature_value.strip()
            else:
                raise ValueError(
                    f"Could not find the temperature value for plate No. "
                    f"{self.serial_numbers.value[plate_index]} in the given PDF {self.pdf_path}"
                )
            value_to_check = temperature_value[1:] if temperature_value.startswith('-') else temperature_value
            if value_to_check.isdigit():
                temperature_value = int(temperature_value)
                pass
            else:
                raise ValueError(
                    f"The temperature value {temperature_value} extracted for plate No. "
                    f"{self.serial_numbers.value[plate_index]} is not a number "
                    f"in the given PDF {self.pdf_path}"
                )
            self.plates[plate_index].temperature = Temperature(
                table_index=table_index,
                x_coordinate=x_coordinate,
                y_coordinate=y_coordinate,
                index=plate_index,
                value=temperature_value
            )

    def extract_impact_energy(self):
        # Firstly, hardcode that tensile strength data is always in the second table
        table_index = 1
        table = self.tables[table_index]

        # Search the title ABSORBED ENERGY to locate the y coordinate
        coordinates = CommonUtils.search_table(table, 'ABSORBEDENERGY',
                                               search_type=TableSearchType.REMOVE_LINE_BREAK_CONTAIN)
        if coordinates is None:
            raise ValueError(
                f"Could not find ABSORBED ENERGY title in the given PDF {self.pdf_path}."
            )
        y_coordinates = [coordinates[1], coordinates[1] + 1, coordinates[1] + 2]
        # x coordinate is the same of the serial numbers
        x_coordinate = self.serial_numbers.x_coordinate

        for impact_energy_index, y_coordinate in enumerate(y_coordinates):

            cell = table[x_coordinate][y_coordinate]

            cell_line_count = len(cell.split('\n'))
            if cell_line_count >= self.serial_numbers.length:
                pass
            else:
                raise ValueError(
                    f"There are {cell_line_count} lines in the impact energy cell, less than "
                    f"the serial numbers count {self.serial_numbers.length} plates in the given PDF {self.pdf_path}"
                )
            impact_energy_cell_lines = cell.split('\n')

            # Start extracting the elongation value for each plate
            for plate_index in range(self.serial_numbers.length):
                impact_energy_value = impact_energy_cell_lines[plate_index]
                if impact_energy_value is not None and len(impact_energy_value.strip()) > 0:
                    impact_energy_value = impact_energy_value.strip()
                else:
                    raise ValueError(
                        f"Could not find the impact energy value for plate No. "
                        f"{self.serial_numbers.value[plate_index]} in the given PDF {self.pdf_path}"
                    )
                if impact_energy_value.isdigit():
                    impact_energy_value = int(impact_energy_value)
                    pass
                else:
                    raise ValueError(
                        f"The impact energy value {impact_energy_value} extracted for plate No. "
                        f"{self.serial_numbers.value[plate_index]} is not a number "
                        f"in the given PDF {self.pdf_path}"
                    )
                self.plates[plate_index].impact_energy_list.append(
                    ImpactEnergy(
                        table_index=table_index,
                        x_coordinate=x_coordinate,
                        y_coordinate=y_coordinate,
                        index=plate_index,
                        test_number=impact_energy_index + 1,
                        value=impact_energy_value
                    )
                )

    def verify(self) -> bool:
        all_pass_flag = True
        _valid_flag = self.verify_mandatory_chemical_limits()
        all_pass_flag = all_pass_flag and _valid_flag
        _valid_flag = self.verify_steel_plant_specific_limits()
        all_pass_flag = all_pass_flag and _valid_flag
        _valid_flag = self.verify_mechanical_limits()
        all_pass_flag = all_pass_flag and _valid_flag
        return all_pass_flag

    def verify_mandatory_chemical_limits(self):
        all_pass_flag = True
        for plate_index in range(self.serial_numbers.length):
            print(
                f"\nVerifying the normal chemical composition limits for plate No. "
                f"{self.serial_numbers.value[plate_index]}...\n"
            )
            _valid_flag = ChemicalCompositionLimitsForHighStrengthSteel.get_singleton().verify(
                specification=self.specification.value,
                thickness=self.thickness.value,
                chemical_compositions=self.plates[plate_index].chemical_compositions,
                pdf_path=self.pdf_path
            )
            all_pass_flag = all_pass_flag and _valid_flag
        return all_pass_flag

    def verify_steel_plant_specific_limits(self):
        hull_structure_steel_plate_limits_for_this_steel_plant = HullStructureSteelPlateLimits.get_singleton().\
            get_limits_by_steel_plant(self.steel_plant.value)
        all_pass_flag = True
        for plate_index in range(self.serial_numbers.length):
            print(
                f"\nVerifying the steel plate limits of {self.steel_plant.value} for plate No. "
                f"{self.serial_numbers.value[plate_index]}...\n"
            )
            _valid_flag = hull_structure_steel_plate_limits_for_this_steel_plant.verify(
                specification=self.specification.value,
                delivery_condition=self.plates[plate_index].delivery_condition.value,
                thickness=self.thickness,
                chemical_compositions=self.plates[plate_index].chemical_compositions,
                pdf_path=self.pdf_path
            )
            all_pass_flag = all_pass_flag and _valid_flag
        return all_pass_flag

    def verify_mechanical_limits(self):
        all_pass_flag = True
        mechanical_limits = MechanicalLimits.get_singleton()
        for plate_index in range(self.serial_numbers.length):
            print(
                f"\nVerifying mechanical limits for plate No. "
                f"{self.serial_numbers.value[plate_index]}...\n"
            )
            _valid_flag = mechanical_limits.verify(
                grade=self.specification.value,
                thickness=self.thickness.value,
                direction=CommonUtils.translate_to_vl_direction(
                    self.plates[plate_index].position_direction_impact.value),
                yield_strength=self.plates[plate_index].yield_strength,
                tensile_strength=self.plates[plate_index].tensile_strength,
                elongation=self.plates[plate_index].elongation,
                temperature=self.plates[plate_index].temperature,
                impact_energy_list=self.plates[plate_index].impact_energy_list
            )
            all_pass_flag = all_pass_flag and _valid_flag
        return all_pass_flag


if __name__ == '__main__':
    # fire.Fire(SteelInspecitionCertificate)
    # file = r"JN3B408421_BGSAJ2005230018600-VL-未签发.pdf"
    # file = 'JN3B409555_BGSAJ2006220014700.pdf'
    # sic = SteelInspecitionCertificate(file)
    # print(sic.steel_plant)
    # print(sic.specification)
    # print(sic.thickness)
    # print(sic.serial_numbers)
    # print(sic.chemical_elements)
    # sic.verify()
    # print(sic.plates)
    # input(f"Click the close button at the top-right corner to finish.")

    # print(os.getcwd())
    # for file in os.listdir():
    #     if file.lower().endswith('.pdf'):
    #         sic = SteelInspecitionCertificate(file)
    #         print(sic.steel_plant)
    #         print(sic.specification)
    #         print(sic.thickness)
    #         print(sic.serial_numbers)
    #         print(sic.chemical_elements)
    #         sic.verify()
    #         print(sic.plates)

    # Print the current working directory
    print(os.getcwd())
    # List the pdf files and subdirectories in the working directory
    pdf_files = []
    subdirectories = []
    with os.scandir() as it:
        for entry in it:
            if entry.is_file() and entry.name.lower().endswith('.pdf'):
                pdf_files.append(entry.name)
            if entry.is_dir():
                subdirectories.append(entry.name)
    # create the destination folders if they don't exist
    if 'PASS' not in subdirectories:
        os.mkdir('PASS')
    if 'FAIL' not in subdirectories:
        os.mkdir('FAIL')
    if 'UNREADABLE' not in subdirectories:
        os.mkdir('UNREADABLE')
    # Iterate the pdf files, read each pdf file and verify, and distribute the files to respective destination folders.
    for file in pdf_files:
        print(f"\n\nProcessing file {file} ...")
        certificate = None
        try:
            certificate = SteelInspecitionCertificate(file)
            certificate.extract_quality_date()
            valid_flag = certificate.verify()
            print(f"\n\nCertificate Content:\n")
            print(certificate.steel_plant)
            print(certificate.specification)
            print(certificate.thickness)
            print(certificate.serial_numbers)
            print(f"Chemical Elements:")
            for element in certificate.chemical_elements:
                print(f"\t{certificate.chemical_elements[element]}")
            print(certificate.plates)
            if valid_flag:
                certificate.close_pdf()
                print(f"Verification Pass!")
                # shutil.copy(file, 'PASS')
                # os.remove is used instead of shutil.move because of compatibility problem with pyinstaller
                # os.remove(file)
            else:
                certificate.close_pdf()
                print(f"Verification Fail!")
                # shutil.copy(file, 'FAIL')
                # os.remove is used instead of shutil.move because of compatibility problem with pyinstaller
                # os.remove(file)
        except ValueError as e:
            print(f"Exception occurred during reading the PDF file!")
            print(e)
            certificate.close_pdf()
            # shutil.copy(file, 'UNREADABLE')
            # os.remove is used instead of shutil.move because of compatibility problem with pyinstaller
            # os.remove(file)
    # input(f"Click enter or close button to finish...")
