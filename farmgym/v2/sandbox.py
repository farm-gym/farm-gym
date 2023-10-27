# def get_concat_h(im1, im2):
#     dst = Image.new('RGB', (im1.width + im2.width, im1.height))
#     dst.paste(im1, (0, 0))
#     dst.paste(im2, (im1.width, 0))
#     return dst


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


# import datetime as dt

# # import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# import matplotlib.gridspec as gridspec


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


#
# def convertImage(imgRGB):
#     imgRGBA = imgRGB.convert("RGBA")
#     datas = imgRGBA.getdata()
#
#     newData = []
#     for item in datas:
#         if item[0] == 255 and item[1] == 255 and item[2] == 255:
#             newData.append((255, 255, 255, 0))
#         else:
#             newData.append(item)
#
#     imgRGBA.putdata(newData)
#     return imgRGB


#
#
# x = {'p1': [0,3,5], 'p2': [(1,1),(4,5)]}
# for i in it.product(    x['p1'], x['p2']):
#  print(i)
#
# print('\n\n')
# for i in it.product(  *list(x[k] for k in x) ):
#  print(i)
#
# print('\n\n')
# for i in it.product(    range(1, 3), range(5, 8)):
#     print(i)
#
#     #((x, y) for x in A for y in B)
