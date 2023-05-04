import matplotlib.pyplot as plt, mpld3

# http://mpld3.github.io/quickstart.html
import numpy as np

from PIL import Image, ImageDraw, ImageFont
import re
import time

import tensorflow as tf
import datetime


def sum_value(value_array):
    sum = 0
    it = np.nditer(value_array, flags=["multi_index", "refs_ok"])
    for x in it:
        sum += value_array[it.multi_index].value
    return sum


def mat2d_value(value_array):
    X, Y = value_array.shape
    mat = np.zeros((X, Y))
    for x in range(X):
        for y in range(Y):
            mat[x, y] = value_array[x, y].value
    return mat


def dict_select(x, vars):
    # print("D:",x,vars)
    y = x
    for v in vars:
        y = y[v]
    return y


def image_value(stages, entity):
    X, Y = np.shape(stages)
    im_width, im_height = 64, 64
    image = Image.new("RGBA", (im_width * X, im_height * Y), (255, 255, 255, 0))
    for x in range(X):
        for y in range(Y):
            image.paste(
                entity.images[stages[x, y].value],
                (im_width * x, im_height * y),
                mask=entity.images[stages[x, y].value],
            )
    return image


def sname_to_name(text):
    sen = re.findall("[0-9]", text)
    varen = ""
    for s in sen:
        varen = varen + s
    if varen != "":
        s2en = (text.split(varen))[0]
        return s2en[0].upper() + s2en[1:] + "-" + varen
    else:
        return text[0].upper() + text[1:] + "-0"

class Monitor:
    def __init__(self, farm, list_of_variables_to_monitor, logdir="logs", run_name=None):
        """
        :param farm:
        :param list_of_variables_to_monitor: list of fi_key,entity_key,var_key,function,name_to_display
        :param logdir: directory to store the TensorBoard logs
        """
        self.farm = farm
        self.variables = list_of_variables_to_monitor
        self.logdir = logdir
        self.run_name = run_name if run_name is not None else datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        
        self.history_variables = {}
        for v in self.variables:
            self.history_variables[v] = ([], [])

        self.writer = tf.summary.create_file_writer(f"{self.logdir}/{self.run_name}")
        print("Monitor CREATED")


    def update_fig(self):
        with self.writer.as_default():
            for i in range(len(self.variables)):
                v = self.variables[i]
                fi_key, entity_key, var_key, map_v, name_to_display, v_range = v
                day = self.farm.fields[fi_key].entities["Weather-0"].variables["day#int365"].value
                value = map_v(self.farm.fields[fi_key].entities[entity_key].variables[var_key])

                days, values = self.history_variables[v]

                # days.append(f'day {day}')
                days.append(day)
                values.append(value)

                if isinstance(value, Image.Image):
                    self.history_variables[v] = (days[-2:], values[-2:])
                    img = np.asarray(self.history_variables[v][1][-1])
                    tf.summary.image(f"{name_to_display} ({fi_key}, {entity_key})", img, step=day)
                elif isinstance(value, (float, int, np.integer, float)):
                    self.history_variables[v] = (days[-20:], values[-20:])
                    if v_range != "range_auto":
                        vm, vM = v_range
                        value = tf.clip_by_value(value, vm, vM)
                    tf.summary.scalar(f"{name_to_display} ({fi_key}, {entity_key})", value, step=day)
                else:  # assumes it is matrix
                    self.history_variables[v] = (days[-2:], values[-2:])
                    if v_range == "range_auto":
                        image_np = np.array(self.history_variables[v][1][-1])
                        image_np = np.reshape(image_np, (1, image_np.shape[0], image_np.shape[1], -1))
                        image_tensor = tf.convert_to_tensor(image_np)
                        tf.summary.image(f"{name_to_display} ({fi_key}, {entity_key})", image_tensor, step=day)

                    else:
                        vm, vM = v_range
                        img = np.asarray(self.history_variables[v][1][-1])
                        img = np.clip(img, vm, vM)
                        img = (img - vm) / (vM - vm)  # scale to [0, 1] for visualization
                        image_np = np.array(img)
                        image_np = np.reshape(image_np, (1, image_np.shape[0], image_np.shape[1], -1))
                        image_tensor = tf.convert_to_tensor(image_np)
                        tf.summary.image(f"{name_to_display} ({fi_key}, {entity_key})", image_tensor, step=day)

                self.writer.flush()

    def stop(self):
        self.writer.close()


def make_variables_to_be_monitored(variables):
    """
    Input exemple:
    variables= ["f0.soil.available_Water#L", "f0.weeds.flowers#nb","f0.weeds.flowers#nb.mat","f1.fertilizer.amount#kg"]
    Output:
    list of variables var ready to be used in farm.add_monitoring(var)
    """

    myfunc = {"sum": sum_value, "mat": mat2d_value}
    var = []
    for v in variables:

        v_parts = v.split(".")
        fi = v_parts[0]
        en = v_parts[1]
        va = v_parts[2]
        if len(v_parts) > 3:
            # print("PARTS", v_parts)
            me = myfunc[v_parts[3]]
        else:
            me = myfunc["sum"]

        # Field:
        sfi = fi.split("f")
        var_fi = "Field-" + sfi[1]

        # Entity:
        var_en = sname_to_name(en)

        # Title:
        sva = va.split("#")
        ssva = sva[0].split("_")
        tva = ""
        for s in ssva:
            tva += s[0].upper() + s[1:] + " "
        if len(sva) > 1:
            tva += "(" + sva[1] + ")"
        else:
            tva = tva[:-1]

        # Selector:
        vas = va.split("[")
        va0 = vas[0]
        # Uses convention "f0.pests.onplant_population#nb[plant].mat"
        if len(vas) > 1:
            # print("VAS",vas)
            myv = []
            for v in vas[1:]:
                s = v[:-1]
                # print("v",s,sname_to_name(s))
                myv.append(sname_to_name(v[:-1]))
            # print("[Monitor]VARS", myv)
            mee = lambda x: me(dict_select(x, myv))

            var.append((var_fi, var_en, va0, mee, tva, "range_auto"))
        else:
            var.append((var_fi, var_en, va0, me, tva, "range_auto"))
        # should become "Field-0, Pests-0, onplant_population#nb["Plant-0"]" or onplant_population#nb, lambda x: sum_value(x["Plant-0"])?
    return var
