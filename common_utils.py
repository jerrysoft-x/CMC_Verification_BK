from typing import List, Tuple, Union
from enum import Enum, unique

from certificate_verification import Direction


@unique
class TableSearchType(Enum):
    SPLIT_LINE_BREAK_END = 1  # split by line break (\n) and check if the last element matches the keyword
    SPLIT_LINE_BREAK_START = 2  # split by line break (\n) and check if the first element matches the keyword
    REMOVE_LINE_BREAK_CONTAIN = 3  # remove all line breaks (\n) and check if contains the keyword
    SPLIT_LINE_BREAK_ALL_DIGIT = 4  # split by line break (\n) and check if all the elements are integer.


class CommonUtils:

    chemical_elements_table = [
        'C', 'Si', 'Mn', 'P', 'S', 'Cr', 'Mo', 'Ni', 'Cu', 'Al', 'Nb', 'V', 'Ti', 'N', 'Ceq', 'Als', 'Alt'
    ]

    @staticmethod
    def search_table(
        table: List[List[Union[str, None]]],
        keyword: Union[str, None],
        search_type: TableSearchType = TableSearchType.SPLIT_LINE_BREAK_END,
        confirmed_row: int = None,
        confirmed_col: int = None
    ) -> Union[Tuple[int, int], None]:

        # Define search methods:
        search_methods = {
            TableSearchType.SPLIT_LINE_BREAK_END:
                lambda table_cell: table_cell is not None and table_cell.split('\n')[-1].strip() == keyword,
            TableSearchType.SPLIT_LINE_BREAK_START:
                lambda table_cell: table_cell is not None and table_cell.split('\n')[0].strip() == keyword,
            TableSearchType.REMOVE_LINE_BREAK_CONTAIN:
                lambda table_cell: table_cell is not None and keyword in table_cell.replace('\n', '').replace(' ', ''),
            TableSearchType.SPLIT_LINE_BREAK_ALL_DIGIT:
                lambda table_cell: table_cell is not None and all(
                    map(lambda x: x.strip().isdigit(), table_cell.split('\n')))
        }

        coordinates = None

        if confirmed_row is None:
            if confirmed_col is None:
                for row_index, row in enumerate(table):
                    if coordinates is not None:
                        break
                    for col_index, cell in enumerate(row):
                        if search_methods[search_type](cell):
                            coordinates = (row_index, col_index)
                            break
            else:
                for row_index, row in enumerate(table):
                    cell = row[confirmed_col]
                    if search_methods[search_type](cell):
                        coordinates = (row_index, confirmed_col)
                        break
        else:
            if confirmed_col is None:
                row = table[confirmed_row]
                for col_index, cell in enumerate(row):
                    if search_methods[search_type](cell):
                        coordinates = (confirmed_row, col_index)
                        break
            else:
                cell = table[confirmed_row][confirmed_col]
                if search_methods[search_type](cell):
                    coordinates = (confirmed_row, confirmed_col)

        return coordinates

    @staticmethod
    def verify_chemical_element_limit(element: str, chemical_composition_limit: dict, element_calculated_value: float):
        if chemical_composition_limit['type'] == 'maximum':
            if element_calculated_value <= chemical_composition_limit['limit']:
                print(
                    f"The value of chemical element {element} is {element_calculated_value}, meets "
                    f"the maximum limit {chemical_composition_limit['limit']}."
                )
            else:
                print(
                    f"The value of chemical element {element} is {element_calculated_value}, violates "
                    f"the maximum limit {chemical_composition_limit['limit']}."
                )
                return False
        elif chemical_composition_limit['type'] == 'minimum':
            if element_calculated_value >= chemical_composition_limit['limit']:
                print(
                    f"The value of chemical element {element} is {element_calculated_value}, meets "
                    f"the minimum limit {chemical_composition_limit['limit']}."
                )
            else:
                print(
                    f"The value of chemical element {element} is {element_calculated_value}, violates "
                    f"the minimum limit {chemical_composition_limit['limit']}."
                )
                return False
        elif chemical_composition_limit['type'] == 'range':
            if chemical_composition_limit['minimum'] <= element_calculated_value <= \
                    chemical_composition_limit['maximum']:
                print(
                    f"The value of chemical element {element} is {element_calculated_value}, meets "
                    f"the valid range [{chemical_composition_limit['minimum']}, "
                    f"{chemical_composition_limit['maximum']}]."
                )
            else:
                print(
                    f"The value of chemical element {element} is {element_calculated_value}, violates "
                    f"the valid range [{chemical_composition_limit['minimum']}, "
                    f"{chemical_composition_limit['maximum']}]."
                )
                return False
        else:
            raise ValueError(
                f"The chemical composition limit type {chemical_composition_limit['type']} of "
                f"chemical element {element} is invalid!"
            )
        return True

    @staticmethod
    def translate_to_vl_direction(position_direction_value: str) -> Direction:
        map_to_vl_direction = {
            'C': Direction.TRANSVERSE,
            'L': Direction.LONGITUDINAL
        }
        c_flag = 'C' in position_direction_value
        l_flag = 'L' in position_direction_value
        if c_flag and not l_flag:
            return map_to_vl_direction['C']
        if l_flag and not c_flag:
            return map_to_vl_direction['L']
        if c_flag and l_flag:
            raise ValueError(
                f"The position direction value {position_direction_value} contains both C (Transverse) and "
                f"L (Longitudinal), it is invalid."
            )
        if not c_flag and not l_flag:
            raise ValueError(
                f"The position direction value {position_direction_value} contains neither C (Transverse) nor "
                f"L (Longitudinal), it is invalid."
            )