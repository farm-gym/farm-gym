import yaml
import pandas

import os
from pathlib import Path

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
    # string = CURRENT_DIR / 'specifications'/filename
    string = CURRENT_DIR / filename
    # with open(string, 'r') as file:
    table = pandas.read_csv(string)
    return table


def build_scoreyaml(filepath, fields):
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
    s += "     alpha_bio: 0.\n"
    s += "     alpha_resource: 0.\n"
    s += "     alpha_soil: 0.\n"
    s += "     alpha_harvest: 1.\n"
    s += "     alpha_stage: 0.\n"
    with open(filepath, "w", encoding="utf8") as file:
        print(s, file=file)


import numpy as np
from farmgym.v2.entity_api import Range


def build_inityaml(filepath, fields, mode="default", init_values=None):
    def make(x, indent="", mode="default", value=None):
        s = ""
        if type(x) == dict:
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
                r = x[it.multi_index].default_value()
            elif mode == "random":
                r = x[it.multi_index].random_value()
            else:  # custom
                r = value
            s += str(r) + "\n"
        elif type(x) in [Range]:
            if mode == "default":
                r = x.default_value()
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

    if init_values not in [None, []]:
        s = ""
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
        s = ""
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
    with open(filepath, "w", encoding="utf8") as file:
        print(s, file=file)


def build_actionsyaml(filepath, fields):
    s = "params:\n"
    s += "  max_action_schedule_size: 5\n"

    def make_s(x, indent=""):
        s = ""
        if type(x) == dict:
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
                    is_not_finished = it.iternext()
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
    for fi in fields:
        s += "  " + fi + ":\n"
        for e in fields[fi].entities:
            s += "    " + e + ":\n"
            for v in fields[fi].entities[e].variables:
                if type(fields[fi].entities[e].variables[v]) == np.ndarray:
                    s += (
                        "      "
                        + v
                        + ": "
                        + make_s(fields[fi].entities[e].variables[v], indent="      ")
                    )
                else:
                    s += (
                        "      "
                        + v
                        + ": "
                        + make_s(fields[fi].entities[e].variables[v], indent="      ")
                    )

    def make_a(x, indent):
        s = "\n"
        for k in x:
            s += indent + (k + ": " + str(x[k]) + "\n")
        return s

    s += "interventions:\n"
    for fi in fields:
        s += "  " + fi + ":\n"
        for e in fields[fi].entities:
            ss = ""
            for a in fields[fi].entities[e].actions:
                ss += (
                    "      "
                    + a
                    + ": "
                    + make_a(fields[fi].entities[e].actions[a], indent="        ")
                )
            if ss != "":
                s += ("    " + e + ":\n") + ss

    with open(filepath, "w", encoding="utf8") as file:
        print(s, file=file)
