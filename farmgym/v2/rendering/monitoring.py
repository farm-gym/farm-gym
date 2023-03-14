import matplotlib.pyplot as plt, mpld3

# http://mpld3.github.io/quickstart.html
import numpy as np

from PIL import Image, ImageDraw, ImageFont
import re
import time


# data = []
# plt.plot(data, 'ks-', mec='w', mew=5, ms=20)
# mpld3.show()
# mpld3.save_html()
#
# for i in range(100):
#     x = np.random.randint(0,10)
#     data.append(x)
#
#     plt.plot(data, 'ks-', mec='w', mew=5, ms=20)
#     mpld3.show()
#     time.sleep(0.5)


import datetime as dt

# import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec


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


# def make_images(self):
#     from farmgym.v2.entities.Plant import Plant
#     import os
#     from pathlib import Path
#
#     file_path = Path(os.path.realpath(__file__))
#     CURRENT_DIR = file_path.parent
#     images = {}
#     for stage in Plant.stages:
#         images[stage] = Image.open(CURRENT_DIR / ("../specifications/sprites/" + self.parameters["sprites"][stage]))
#     return images


class Monitor:
    def __init__(self, farm, list_of_variables_to_monitor, filename="monitor.png"):
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
                print("V", v, value)
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

        # represents each monitored value as image, pixel=plot, , pixel-value = value at plot, evolving with time.


# represents each plot as a figure, monotored value = curve, evolving with time.
#
# def base():
#     fig = plt.figure(figsize=(10, 8))
#     outer = gridspec.GridSpec(2, 2, wspace=0.2, hspace=0.2)
#
#     for i in range(4):
#         inner = gridspec.GridSpecFromSubplotSpec(2, 1,
#                         subplot_spec=outer[i], wspace=0.1, hspace=0.1)
#
#         for j in range(2):
#             ax = plt.Subplot(fig, inner[j])
#             t = ax.text(0.5,0.5, 'outer=%d, inner=%d' % (i, j))
#             t.set_ha('center')
#             ax.set_xticks([])
#             ax.set_yticks([])
#             fig.add_subplot(ax)
#
#
#     fig.show()
#     fig.savefig('bla.png')
#
# def demo3():
#     nb_fields = 4
#     nb_plots_in_field = [(2, 2), (3, 2), (1, 1), (2, 1)]
#
#     # Create figure for plotting
#
#     fig = plt.figure(figsize=(nb_fields*5, 8))
#     outer = gridspec.GridSpec(2, nb_fields, wspace=0.2, hspace=0.2)
#
#     for f in range(nb_fields):
#         inner = gridspec.GridSpecFromSubplotSpec(1, 1,
#                         subplot_spec=outer[f], wspace=0.1, hspace=0.1)
#
#         for j in range(1):
#             ax = plt.Subplot(fig, inner[j])
#             ax.set_title(f'Field {f} global', fontsize='small')
#             #t = ax.text(0.5,0.5, 'outer=%d, Global' % f)
#             #t.set_ha('center')
#             ax.set_xticks([])
#             ax.set_yticks([])
#             fig.add_subplot(ax)
#
#
#         nx,ny  =nb_plots_in_field[f]
#         inner = gridspec.GridSpecFromSubplotSpec(nx, ny,
#                         subplot_spec=outer[f+nb_fields], wspace=0.1, hspace=0.1)
#         for j in range(nx*ny):
#             ax = plt.Subplot(fig, inner[j])
#             ax.set_title(f'Field {f} plot {j}', fontsize='small')
#             #t = ax.text(0.5, 0.5, 'outer=%d, inner=%d' % (f, j))
#             #t.set_ha('center')
#             ax.set_xticks([])
#             ax.set_yticks([])
#             fig.add_subplot(ax)
#
#     fig.show()
#     fig.savefig('bla.png')
# #demo3()
#
#
# def demo4():
#     nb_fields = 4
#     nb_plots_in_field = [(2, 2), (3, 2), (1, 1), (2, 1)]
#
#     # Create figure for plotting
#
#
#     for f in range(nb_fields):
#
#         nx, ny = nb_plots_in_field[f]
#         fig = plt.figure(figsize=(nx*2, ny*2),num=f)
#         outer = gridspec.GridSpec(nx, ny, wspace=0.2, hspace=0.2)
#
#         for x in range(nx):
#             for y in range(ny):
#                 ax = plt.subplot(nx,ny,1+ x*ny+y)
#                 ax.set_title(f'Field {f} plot {x}, {y}', fontsize='small')
#                 #t = ax.text(0.5,0.5, 'outer=%d, Global' % f)
#                 #t.set_ha('center')
#                 ax.set_xticks([])
#                 ax.set_yticks([])
#                 fig.add_subplot(ax)
#
#         fig.show()
#         fig.savefig('bla-'+str(f)+'.png')
#
# #demo4()
#
# def demo():
#
#     nb_fields = 4
#     nb_plots_in_field = [(2,2),(3,2),(1,1),(2,1)]
#
#     fig = plt.figure(constrained_layout=True)
#     subfigs = fig.subfigures(2,nb_fields)
#     for f in range(nb_fields):
#
#         subfig = subfigs[f]
#         subfig.suptitle(f'Field {f} global')
#         axs = subfig.subplots(1, 1)
#         ax = axs[0]
#         ax.set_title(f'global', fontsize='small')
#         ax.set_xticks([])
#         ax.set_yticks([])
#
#         subfig = subfigs[f+nb_fields]
#         subfig.suptitle(f'Field {f} local')
#         nx,ny  =nb_plots_in_field[f]
#         axs = subfig.subplots(nx, ny)
#         for innerind, ax in enumerate(axs.flat):
#             ax.set_title(f'outer={f}, inner={innerind}', fontsize='small')
#             ax.set_xticks([])
#             ax.set_yticks([])
#
#     plt.show()
#
#
#
# def demo0():
#     fig = plt.figure(constrained_layout=True)
#     ax_ = []
#
#     subfigs = fig.subfigures(2,1)
#
#     for outerind, subfig in enumerate(subfigs.flat):
#         subfig.suptitle(f'Subfig {outerind}')
#         axs = subfig.subplots(2, 1)
#         for innerind, ax in enumerate(axs.flat):
#             ax.set_title(f'outer={outerind}, inner={innerind}', fontsize='small')
#             ax.set_xticks([])
#             ax.set_yticks([])
#     plt.show()
#
#
#
# def demo1():
#
#     fig = plt.figure()
#     ax = fig.add_subplot(1, 1, 1)
#
#     xs = []
#     ys = []
#
#     # Initialize communication with TMP102
#     #tmp102.init()
#
#     # This function is called periodically from FuncAnimation
#     def animate(i, xs, ys):
#
#         # Read temperature (Celsius) from TMP102
#         temp_c = np.random.randint(0,10)
#
#         # Add x and y to lists
#         xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
#         ys.append(temp_c)
#
#         # Draw x and y lists
#         # Limit x and y lists to 20 items
#         ax.clear()
#         ax.plot(xs[-20:], ys[-20:])
#
#         # Format plot
#         plt.xticks(rotation=45, ha='right')
#         plt.subplots_adjust(bottom=0.30)
#         plt.title('TMP102 Temperature over Time')
#         plt.ylabel('Temperature (deg C)')
#
#     # Set up plot to call animate() function periodically
#     ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=1000)
#    plt.show()


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
        sen = re.findall("[0-9]", en)
        varen = ""
        for s in sen:
            varen = varen + s
        if varen != "":
            s2en = (en.split(varen))[0]
            var_en = s2en[0].upper() + s2en[1:] + "-" + varen
        else:
            var_en = en[0].upper() + en[1:] + "-0"

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

        var.append((var_fi, var_en, va, me, tva, "range_auto"))
    return var
