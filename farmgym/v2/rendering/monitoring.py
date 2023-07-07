import datetime
import os
import re

import matplotlib.pyplot as plt

# http://mpld3.github.io/quickstart.html
import numpy as np
from PIL import Image


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


class MonitorTensorBoard:
    def __init__(self, farm, list_of_variables_to_monitor, logdir="logs", run_name=None, matview=True):
        """
        :param farm:
        :param list_of_variables_to_monitor: list of fi_key,entity_key,var_key,function,name_to_display
        :param logdir: directory to store the TensorBoard logs
        :param matview: disable to remove images from tensorboard

        #TODO:
        [ ] Test monitoring on bigger farms
        [X] Check if matrix view is working
        [ ] Add legends to Tensorboard
        [X] Add option to switch to Plt
        """
        import tensorflow as tf
        from tensorboard import program
        
        self.farm = farm
        self.variables = list_of_variables_to_monitor
        self.logdir = logdir
        self.run_name = run_name if run_name is not None else datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.images = {}
        self.matview = matview
        self.tf = tf

        self.history_variables = {}
        for v in self.variables:
            self.history_variables[v] = ([], [])
        # Start Tensorboard writer
        self.writer = tf.summary.create_file_writer(f"{self.logdir}/{self.run_name}")
        self.writer_closed = False
        # Launch TensorBoard
        tb = program.TensorBoard()
        tb.configure(argv=[None, "--logdir", os.path.join(os.getcwd(), logdir)])
        self.tb_url = tb.launch()
        print(f"Tensorflow listening on {self.tb_url}")

    def update_fig(self):
        with self.writer.as_default():
            for i in range(len(self.variables)):
                v = self.variables[i]
                fi_key, entity_key, var_key, map_v, name_to_display, v_range = v
                day = self.farm.fields[fi_key].entities["Weather-0"].variables["day#int365"].value
                value = map_v(self.farm.fields[fi_key].entities[entity_key].variables[var_key])

                days, values = self.history_variables[v]
                days.append(day)
                values.append(value)

                if isinstance(value, Image.Image):
                    self.history_variables[v] = (days[-2:], values[-2:])
                    img = np.asarray(self.history_variables[v][1][-1])
                    self.tf.summary.image(f"{entity_key}/{name_to_display} ({fi_key}, {entity_key})", img, step=day)
                elif isinstance(value, (float, int, np.integer, float)):
                    self.history_variables[v] = (days[-20:], values[-20:])
                    if v_range != "range_auto":
                        vm, vM = v_range
                        value = self.tf.clip_by_value(value, vm, vM)
                    self.tf.summary.scalar(f"{entity_key}/{name_to_display} ({fi_key}, {entity_key})", value, step=day)
                elif self.matview:  # assumes it is matrix
                    self.history_variables[v] = (days[-2:], values[-2:])
                    if v_range == "range_auto":
                        plt.imshow(
                            self.history_variables[v][1][-1],
                            cmap="hot",
                            interpolation="nearest",
                        )
                        plt.savefig(f"history_variables_{day}")
                        image = Image.open(f"history_variables_{day}.png")
                        image = self.tf.expand_dims(image, axis=0)
                        if name_to_display not in self.images:
                            self.images[name_to_display] = [(fi_key, entity_key, image, day)]
                        else:
                            self.images[name_to_display].append((fi_key, entity_key, image, day))

                        os.remove(f"history_variables_{day}.png")

                    else:
                        vm, vM = v_range
                        img = np.asarray(self.history_variables[v][1][-1])
                        img = np.clip(img, vm, vM)
                        img = (img - vm) / (vM - vm)  # scale to [0, 1] for visualization
                        plt.imshow(
                            img,
                            cmap="hot",
                            interpolation="nearest",
                        )
                        plt.savefig(f"history_variables_{day}")
                        image = Image.open(f"history_variables_{day}.png")
                        image = self.tf.expand_dims(image, axis=0)
                        if name_to_display not in self.images:
                            self.images[name_to_display] = [(fi_key, entity_key, image, day)]
                        else:
                            self.images[name_to_display].append((fi_key, entity_key, image, day))
                        os.remove(f"history_variables_{day}.png")
                self.writer.flush()

    def stop(self):
        if not self.writer_closed:
            print("Stopping monitoring ...")
            for name in self.images:
                image_list = []
                for fi_key, entity_key, image, day in self.images[name]:
                    image_data = np.squeeze(image)
                    image_list.append(image_data)
                image_array = np.array(image_list)
                for i, image in enumerate(image_array):
                    # Write the summary image to a TensorBoard log file
                    with self.writer.as_default():
                        self.tf.summary.image(name, np.expand_dims(image, axis=0), step=i)
            check_close = ""
            while check_close.lower() != "exit":
                check_close = input(f"Tensorflow is still listening on {self.tb_url}, type 'exit' to close : ")
            print("Closing writer ...")
            self.writer.close()
            self.writer_closed = True
        else:
            print("Stopping the monitoring is impossible, the writer is already closed")


class MonitorPlt:
    def __init__(self, farm, list_of_variables_to_monitor, filename="monitor.png", matview=False):
        """
        :param farm:
        :param list_of_variables_to_monitor: list of fi_key,entity_key,var_key,function,name_to_display
        """
        self.farm = farm
        self.variables = list_of_variables_to_monitor
        self.filename = filename

        self.history_variables = {}
        for v in self.variables:
            self.history_variables[v] = ([], [])

        self.sizex = (int)(np.ceil(np.sqrt(len(self.variables)) / 1.3))
        self.sizey = (int)(np.ceil(np.sqrt(len(self.variables)) * 1.3))

        self.fig = plt.figure(figsize=(3 * self.sizey, 3 * self.sizex))

    def update_fig(self):
        for i in range(len(self.variables)):
            v = self.variables[i]
            fi_key, entity_key, var_key, map_v, name_to_display, v_range = v
            day = self.farm.fields[fi_key].entities["Weather-0"].variables["day#int365"].value
            value = map_v(self.farm.fields[fi_key].entities[entity_key].variables[var_key])

            days, values = self.history_variables[v]

            # days.append(f'day {day}')
            days.append(day)
            values.append(value)

            # print(v,day,value,self.history_variables[v])
            ax = plt.subplot(self.sizex, self.sizey, 1 + i)
            ax.clear()
            # If real value !
            if isinstance(value, Image.Image):
                self.history_variables[v] = (days[-2:], values[-2:])
                ax.imshow(self.history_variables[v][1][-1])
            elif isinstance(value, (float, int, np.integer, np.float)):
                # print("V", v, value)
                self.history_variables[v] = (days[-20:], values[-20:])
                ax.plot(self.history_variables[v][0], self.history_variables[v][1])
                if v_range != "range_auto":
                    vm, vM = v_range
                    plt.ylim(vm, vM)

            else:  # assumes it is matrix
                # print("TYPE",value,type(value),isinstance(value,float),type(value)==int,v)
                self.history_variables[v] = (days[-2:], values[-2:])
                if v_range == "range_auto":
                    ax.imshow(
                        self.history_variables[v][1][-1],
                        cmap="hot",
                        interpolation="nearest",
                    )
                else:
                    vm, vM = v_range
                    ax.imshow(
                        self.history_variables[v][1][-1],
                        cmap="gray",
                        vmin=vm,
                        vmax=vM,
                        interpolation="nearest",
                    )

            # plt.xticks(rotation=45, ha='right')
            plt.subplots_adjust(bottom=0.30, wspace=0.8, hspace=0.8)
            plt.title(f"{fi_key}, {entity_key}\n {name_to_display}")
            plt.ylabel(f"{name_to_display}")
            plt.xlabel("day")
            plt.show(block=False)
        plt.pause(0.1)

    def stop(self):
        plt.savefig(self.filename)


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
