import os
from pathlib import Path

import pandas
import yaml

file_path = Path(os.path.realpath(__file__))
CURRENT_DIR = file_path.parent
# CURRENT_DIR = file_path
# print(type(CURRENT_DIR))


def load_yaml(spec_file, parameter_string):
    # spec_file=(class_.__class__.__name__).lower()+'_specifications.yaml'
    # string = CURRENT_DIR / 'specifications'/spec_file
    string = CURRENT_DIR / spec_file
    with open(string, "r", encoding="utf8") as file:
        doc_yaml = yaml.safe_load(file)  # Note the safe_load
        return doc_yaml[parameter_string]


def load_weather_table(filename):
    if isinstance(filename, dict):
        tables = []
        alphas = []
        for k in filename.keys():
            string = CURRENT_DIR / k
            # with open(string, 'r') as file:
            tables.append(pandas.read_csv(string))
            alphas.append(filename[k])
        return tables, alphas
    else:
        # string = CURRENT_DIR / 'specifications'/filename
        string = CURRENT_DIR / filename
        # with open(string, 'r') as file:
        table = pandas.read_csv(string)
        return [table], [1]


def build_scoreyaml(filepath, farm):
    fields = farm.fields
    s = "observation-cost" + ":\n"
    for fi in fields:
        s += "  " + fi + ":\n"
        for e in fields[fi].entities:
            s += "    " + e + ":\n"
            for v in fields[fi].entities[e].variables:
                s += "      " + v + ": " + str(1) + "\n"
    s += "intervention-cost" + ":\n"
    for fi in fields:
        s += "  " + fi + ":\n"
        for e in fields[fi].entities:
            ss = ""
            for a in fields[fi].entities[e].actions:
                ss += ("      " + a + ": ") + str(1) + "\n"
            if ss != "":
                s += ("    " + e + ":\n") + ss

    s += "reward-mix:\n"
    s += "     weight_biodiversitycounts: 0.\n"
    s += "     weight_resourceadded: 0.\n"
    s += "     weight_soilmicrolife: 0.\n"
    s += "     weight_harvest: 0.\n"
    s += "     weight_stagecount: 0.\n"
    s += "     weight_stagetransition: 1.\n"

    s += "final-reward-mix:\n"
    s += "     weight_biodiversitycounts: 0.\n"
    s += "     weight_resourceadded: 0.\n"
    s += "     weight_soilmicrolife: 0.\n"
    s += "     weight_harvest: 1.\n"
    s += "     weight_stagecount: 0.\n"
    s += "     weight_stagetransition: 0.\n"
    with open(filepath, "w", encoding="utf8") as file:
        print(s, file=file)


import numpy as np  # noqa: E402

from farmgym.v2.entity_api import Range  # noqa: E402


def build_inityaml(filepath, farm, mode="default", init_values=None):
    fields = farm.fields

    def make(x, indent="", mode="default", value=None):
        s = ""
        if isinstance(x, dict):
            s += "\n"
            for k in x:
                s += indent + ("  " + k + ": ")
                if mode in ["default", "random"]:
                    s += make(x[k], indent=indent + "  ", mode=mode)
                else:  # custom
                    s += make(x[k], indent=indent + "  ", mode="custom", value=value[k])
        elif type(x) == np.ndarray:
            it = np.nditer(x, flags=["multi_index", "refs_ok"])
            if mode == "default":
                r = x[it.multi_index].get_default_value()
            elif mode == "random":
                r = x[it.multi_index].random_value()
            else:  # custom
                r = value
            s += str(r) + "\n"
        elif type(x) in [Range]:
            if mode == "default":
                # print("x", x, type(x))
                r = x.get_default_value()
            elif mode == "random":
                r = x.random_value()
            else:  # custom
                r = value
            s += str(r) + "\n"
        else:
            s += "???\n"
        return s

    # s= ""
    # for fi in fields:
    #     s+= ("  "+fi+":\n")
    #     for e in fields[fi].entities:
    #         s+= ("    "+e+":\n")
    #         for v in fields[fi].entities[e].variables:
    #             if (init_values not in [None,[]]):
    #                 is_custom=False
    #                 for ifi,ie,iv,value in init_values:
    #                     if (fi,e,v) ==(ifi,ie,iv):
    #                         s += "      " + v + ": " + make(fields[fi].entities[e].variables[v], indent="      ", mode='custom',value=value)
    #                         is_custom=True
    #                         break
    #                  #if (not is_custom):
    #                  #    s+="      " + v + ": " + make(fields[fi].entities[e].variables[v],indent="      ",mode=mode)
    #             else:
    #                 s+="      " + v + ": " + make(fields[fi].entities[e].variables[v],indent="      ",mode=mode)

    s = "Initial:\n"
    if init_values not in [None, []]:
        s += ""
        for fi in fields:
            is_fi = False
            for ifi, ie, iv, value in init_values:
                if fi == ifi:
                    is_fi = True
                    break
            if is_fi:
                s += "  " + fi + ":\n"
                for e in fields[fi].entities:
                    is_e = False
                    for ifi, ie, iv, value in init_values:
                        if (fi, e) == (ifi, ie):
                            is_e = True
                            break
                    if is_e:
                        s += "    " + e + ":\n"
                        for v in fields[fi].entities[e].variables:
                            for ifi, ie, iv, value in init_values:
                                if (fi, e, v) == (ifi, ie, iv):
                                    s += (
                                        "      "
                                        + v
                                        + ": "
                                        + make(
                                            fields[fi].entities[e].variables[v],
                                            indent="      ",
                                            mode="custom",
                                            value=value,
                                        )
                                    )
                                    break

    else:
        s += ""
        for fi in fields:
            s += "  " + fi + ":\n"
            for e in fields[fi].entities:
                s += "    " + e + ":\n"
                for v in fields[fi].entities[e].variables:
                    s += (
                        "      "
                        + v
                        + ": "
                        + make(
                            fields[fi].entities[e].variables[v],
                            indent="      ",
                            mode=mode,
                        )
                    )

    s += "Terminal:\n"
    #    [
    #        [{state_variable: ["Field-0", "Weather-0", "day#int365", []], function: "value", operator: ">=",
    #          ref_value: 360}],
    #        [{state_variable: ["Field-0", "Plant-0", "global_stage", []], function: "value", operator: "==",
    #          ref_value: "dead"}],
    #    ]
    s += "  [\n"
    s += '    [{state_variable: ["Field-0", "Weather-0", "day#int365", []], function: "value", operator: ">=", ref_value: 360}],\n'
    # TODO: This should only be added if Plant-0 is in Field-0: Currently, I added in rules_api a way to ignore the case when Plant-0 does not exist.
    s += '    [{state_variable: ["Field-0", "Plant-0", "global_stage", []], function: "value", operator: "==", ref_value: "dead"}],\n'
    s += "  ]"

    with open(filepath, "w", encoding="utf8") as file:
        print(s, file=file)


def build_actionsyaml(filepath, farm):
    s = "params:\n"
    s += "  max_action_schedule_size: 5\n"
    s += "  number_of_bins_to_discretize_continuous_actions: 11\n"

    fields = farm.fields

    def make_s(x, indent=""):
        s = ""
        if isinstance(x, dict):
            s += "\n"
            s += indent + ("  '*': \n")
            for k in x:
                if type(x[k]) == np.ndarray:
                    s += indent + ("  " + k + ": ")
                else:
                    s += indent + ("  " + k + ": ")
                s += make_s(x[k], indent=indent + "  ")
        elif type(x) == np.ndarray:
            s += "['*',"
            it = np.nditer(x, flags=["multi_index", "refs_ok"])
            # s+= str(len(it))+","+str(x.shape) +","+str(len(x.shape))+","+str(len(x))
            if len(x.shape) > 1:
                s += "'" + str(it.multi_index) + "'"
                it.iternext()
                while not it.finished:
                    s += ", " + "'" + str(it.multi_index) + "'"
                    is_not_finished = it.iternext()  # noqa: F841
                s += "]\n"
            else:
                for i in range(len(x) - 1):
                    s += str(i) + ", "
                s += str(len(x) - 1) + "]\n"

            # r=x[it.multi_index].range
            # s+= str(r) + "\n"
        elif type(x) in [Range]:
            s += "\n"
        else:
            s += "???\n"
        return s

    s += "observations:\n"

    s += "  " * 1 + "Free" + ":\n"
    s += "  " * 2 + "Field-0" + ":\n"
    s += "  " * 3 + "Weather-0" + ":\n"
    s += "  " * 4 + "day#int365" + ": \n"
    s += "  " * 4 + "air_temperature" + ": \n"
    s += "  " * 5 + "'*'" + ":\n"

    for fa in farm.farmers:
        s += "  " * 1 + fa + ":\n"
        for fi in fields:
            s += "  " * 2 + fi + ":\n"
            for e in fields[fi].entities:
                s += "  " * 3 + e + ":\n"
                for v in fields[fi].entities[e].variables:
                    if type(fields[fi].entities[e].variables[v]) == np.ndarray:
                        s += (
                            "  " * 4
                            + v
                            + ": "
                            + make_s(
                                fields[fi].entities[e].variables[v], indent="  " * 5
                            )
                        )
                    else:
                        s += (
                            "  " * 4
                            + v
                            + ": "
                            + make_s(
                                fields[fi].entities[e].variables[v], indent="  " * 5
                            )
                        )

    def make_a(x, indent):
        s = "\n"
        for k in x:
            s += indent + (k + ": " + str(x[k]) + "\n")
        return s

    s += "interventions:\n"
    for fa in farm.farmers:
        s += "  " * 1 + fa + ":\n"
        for fi in fields:
            s += "  " * 2 + fi + ":\n"
            for e in fields[fi].entities:
                ss = ""
                for a in fields[fi].entities[e].actions:
                    ss += (
                        "  " * 4
                        + a
                        + ": "
                        + make_a(fields[fi].entities[e].actions[a], indent="  " * 5)
                    )
                if ss != "":
                    s += ("  " * 3 + e + ":\n") + ss

    with open(filepath, "w", encoding="utf8") as file:
        print(s, file=file)
