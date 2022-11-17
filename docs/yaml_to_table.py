"""
Adapted from https://github.com/ishswar/yaml-to-table
"""

import sys
from pathlib import Path
import oyaml as yaml
from prettytable import PrettyTable, MARKDOWN


def get_sentences(a, b):
    return " "


SPACE_CHAR = "~"


def listToString(inList):
    """Convert list to String"""
    ret = ""
    for line in inList:
        ret = ret + line
    return ret


def printDic(inDictionary, inPTable, indent):
    """
    Iterate over Dictionary
       If needed call same function again (recursively) until we key : value dictionary
       Add key , value , isItRequired , description to pretty table object (inPTable)
    """
    global SPACE_CHAR  # No space character that will be replaced when we print this table to text/html

    # Go ver dictionary
    for item in inDictionary:
        if isinstance(
            item, dict
        ):  # If it again dictionary call same function with this new dictionary
            inPTable.add_row([SPACE_CHAR, SPACE_CHAR])
            printDic(item, inPTable, indent)
        else:
            # Two way to get next item based on input type
            if isinstance(inDictionary, dict):
                moreStuff = inDictionary.get(item)
            elif isinstance(inDictionary, list):
                # If it simple array/list we just print all it's value and we are done
                for _item in inDictionary:
                    inPTable.add_row([indent + _item, SPACE_CHAR + SPACE_CHAR])
                break

            # if it is dictionary or list process them accordingly
            if isinstance(moreStuff, dict):
                inPTable.add_row([indent + item, SPACE_CHAR + SPACE_CHAR])
                printDic(moreStuff, inPTable, SPACE_CHAR + SPACE_CHAR + indent)
            elif isinstance(moreStuff, list):

                # If we are not in nested call (as indent is empty string) we add one extra row in table (for clarity)
                if indent == "":
                    inPTable.add_row([SPACE_CHAR, SPACE_CHAR])
                #
                inPTable.add_row([indent + item, ""])
                for dicInDic in moreStuff:
                    if dicInDic is not None:
                        if isinstance(dicInDic, dict):
                            printDic(
                                dicInDic,
                                inPTable,
                                SPACE_CHAR
                                + SPACE_CHAR
                                + SPACE_CHAR
                                + SPACE_CHAR
                                + indent,
                            )
            else:
                # Most of the call will end-up eventually here -
                # this will print - key,value,isItRequired, Lorem ipsum (description)
                inPTable.add_row([indent + item, inDictionary[item]])


def parse_yaml(in_file):
    final_str = ""
    with open(in_file) as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        yaml_file_object = yaml.load(file, Loader=yaml.FullLoader)

        i = 0
        for key in yaml_file_object:
            body_st = []
            prettyTable = PrettyTable()
            prettyTable.set_style(MARKDOWN)

            prettyTable.field_names = ["Field", "Value"]

            prettyTable.align["Field"] = "l"
            prettyTable.align["Value"] = "l"

            if isinstance(yaml_file_object, list):
                dic = yaml_file_object[i]
                i += 1
            elif isinstance(yaml_file_object, dict):
                dic = yaml_file_object.get(key)

            if isinstance(dic, dict) or isinstance(dic, list):
                printDic(dic, prettyTable, "")
                if isinstance(yaml_file_object, dict):
                    yaml_snippet = yaml.dump({key: dic})
                else:
                    yaml_snippet = yaml.dump(dic)

            else:
                prettyTable.add_row([key, dic])
                yaml_snippet = yaml.dump({key: dic})

            if isinstance(yaml_file_object, dict):
                final_str += "\n ## " + key + "\n"

            final_str += str(prettyTable).replace(SPACE_CHAR, "&ensp;")
        return final_str


if __name__ == "__main__":

    in_file = Path(sys.argv[1])
    final_str = parse_yaml(in_file)
    print(final_str)
