import os
import matplotlib.pyplot as plt

def savefigure(cfg, path_figures, fig, namefig, folder, save):
    path_figmodel = os.path.join(path_figures, folder)
    if not os.path.exists(path_figmodel):
        os.makedirs(path_figmodel)
    if save:
        figfile = os.path.join(path_figmodel, namefig) + '.' + cfg['plot']['figformat']
        fig.savefig(figfile, format=cfg['plot']['figformat'])
        plt.close()
