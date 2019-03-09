#!/usr/bin/env python
import matplotlib
import numpy as np
import pylab as plt

import observations as obs

matplotlib.use("Agg")

np.warnings.filterwarnings("ignore")

matplotlib.rcdefaults()
plt.rc("xtick", labelsize="x-large")
plt.rc("ytick", labelsize="x-large")
plt.rc("lines", linewidth="2.0")
plt.rc("legend", numpoints=1, fontsize="x-large")
plt.rc("text", usetex=True)


def adjust_legend(ax, location="upper right", scatter_plot=0): 
    """
    Adjusts the legend of a specified axis.

    Parameters
    ----------

    ax : ``matplotlib`` axes object
        The axis whose legend we're adjusting

    location : String, default "upper right". See ``matplotlib`` docs for full options
        Location for the legend to be placed.

    scatter_plot : {0, 1}
        For plots involved scattered-plotted data, we adjust the size and alpha of the
        legend points.

    Returns
    -------

    None. The legend is placed directly onto the axis.
    """

    legend = ax.legend(loc=location)
    handles = legend.legendHandles

    legend.draw_frame(False)

    # First adjust the text sizes.
    for t in legend.get_texts():
        t.set_fontsize("medium")

    # For scatter plots, we want to increase the marker size.
    if scatter_plot:
        for handle in handles:
            # We may have lines in the legend which we don't want to touch here.
            if isinstance(handle, matplotlib.collections.PathCollection):
                handle.set_alpha(1.0) 
                handle.set_sizes([10.0])


def plot_SMF(results, plot_sub_populations=0):

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Go through each of the models and plot. 
    for model in results.models:

        model_label = model.model_label

        # If we only have one model, we will split it into red and blue
        # sub-populations.
        if len(results.models) > 1:
            color = model.color
            ls = model.linestyle
        else:
            color = "k"
            ls = "-"

        # Set the x-axis values to be the centre of the bins.
        bin_middles = model.stellar_mass_bins + 0.5 * model.stellar_bin_width

        # The SMF is normalized by the simulation volume which is in Mpc/h. 
        ax.plot(bin_middles[:-1], model.SMF/model.volume*pow(model.hubble_h, 3)/model.stellar_bin_width,
                color=color, ls=ls, label=model_label + " - All")

        # Be careful to not overcrowd the plot. 
        if results.num_models == 1 or plot_sub_populations:
            ax.plot(bin_middles[:-1], model.red_SMF/model.volume*pow(model.hubble_h, 3)/model.stellar_bin_width,
                    "r:", lw=2, label=model_label + " - Red")
            ax.plot(bin_middles[:-1], model.blue_SMF/model.volume*pow(model.hubble_h, 3)/model.stellar_bin_width,
                    "b:", lw=2, label=model_label + " - Blue")

    # For scaling the observational data, we use the values of the zeroth
    # model.
    zeroth_hubble_h = (results.models)[0].hubble_h
    zeroth_IMF = (results.models)[0].IMF
    ax = obs.plot_smf_data(ax, zeroth_hubble_h, zeroth_IMF) 

    ax.set_xlabel(r"$\log_{10} M_{\mathrm{stars}}\ (M_{\odot})$")
    ax.set_ylabel(r"$\phi\ (\mathrm{Mpc}^{-3}\ \mathrm{dex}^{-1})$")

    ax.set_yscale("log", nonposy="clip")

    # Find the models that have the smallest/largest stellar mass bin.
    xlim_min = np.min([model.stellar_mass_bins for model in results.models]) - 0.2
    xlim_max = np.max([model.stellar_mass_bins for model in results.models]) + 0.2
    ax.set_xlim([xlim_min, xlim_max])
    ax.set_ylim([1.0e-6, 1.0e-1])

    ax.xaxis.set_minor_locator(plt.MultipleLocator(0.1))

    adjust_legend(ax, location="lower left", scatter_plot=0)

    output_file = "{0}/1.StellarMassFunction{1}".format(results.plot_output_path,
                                                       results.output_format)
    fig.savefig(output_file)
    print("Saved file to {0}".format(output_file))
    plt.close()


def plot_BMF(results):

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for model in results.models:

        model_label = model.model_label
        color = model.color
        ls = model.linestyle

        # Set the x-axis values to be the centre of the bins.
        bin_middles = model.stellar_mass_bins + 0.5 * model.stellar_bin_width

        # The MF is normalized by the simulation volume which is in Mpc/h. 
        ax.plot(bin_middles[:-1], model.BMF/model.volume*pow(model.hubble_h, 3)/model.stellar_bin_width,
                color=color, ls=ls, label=model_label + " - All")

    # For scaling the observational data, we use the values of the zeroth
    # model.
    zeroth_hubble_h = (results.models)[0].hubble_h
    zeroth_IMF = (results.models)[0].IMF
    ax = obs.plot_bmf_data(ax, zeroth_hubble_h, zeroth_IMF) 

    ax.set_xlabel(r"$\log_{10}\ M_{\mathrm{bar}}\ (M_{\odot})$")
    ax.set_ylabel(r"$\phi\ (\mathrm{Mpc}^{-3}\ \mathrm{dex}^{-1})$")

    ax.set_yscale("log", nonposy="clip")

    # Find the models that have the smallest/largest stellar mass bin.
    xlim_min = np.min([model.stellar_mass_bins for model in results.models]) - 0.2
    xlim_max = np.max([model.stellar_mass_bins for model in results.models]) + 0.2
    ax.set_xlim([xlim_min, xlim_max])
    ax.set_ylim([1.0e-6, 1.0e-1])

    ax.xaxis.set_minor_locator(plt.MultipleLocator(0.1))

    adjust_legend(ax, location="lower left", scatter_plot=0)

    output_file = "{0}/2.BaryonicMassFunction{1}".format(results.plot_output_path, results.output_format) 
    fig.savefig(output_file)
    print("Saved file to {0}".format(output_file))
    plt.close()


def plot_GMF(results):

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for model in results.models:

        model_label = model.model_label
        color = model.color
        ls = model.linestyle

        # Set the x-axis values to be the centre of the bins.
        bin_middles = model.stellar_mass_bins + 0.5 * model.stellar_bin_width

        # The MMF is normalized by the simulation volume which is in Mpc/h. 
        ax.plot(bin_middles[:-1], model.GMF/model.volume*pow(model.hubble_h, 3)/model.stellar_bin_width,
                color=color, ls=ls, label=model_label + " - Cold Gas")

    # For scaling the observational data, we use the values of the zeroth
    # model.
    zeroth_hubble_h = (results.models)[0].hubble_h
    obs.plot_gmf_data(ax, zeroth_hubble_h)

    ax.set_xlabel(r"$\log_{10} M_{\mathrm{X}}\ (M_{\odot})$")
    ax.set_ylabel(r"$\phi\ (\mathrm{Mpc}^{-3}\ \mathrm{dex}^{-1})$")

    ax.set_yscale("log", nonposy="clip")

    # Find the models that have the smallest/largest stellar mass bin.
    xlim_min = np.min([model.stellar_mass_bins for model in results.models]) - 0.2
    xlim_max = np.max([model.stellar_mass_bins for model in results.models]) + 0.2
    ax.set_xlim([xlim_min, xlim_max])
    ax.set_ylim([1.0e-6, 1.0e-1])

    ax.xaxis.set_minor_locator(plt.MultipleLocator(0.1))

    adjust_legend(ax, location="lower left", scatter_plot=0)

    output_file = "{0}/3.GasMassFunction{1}".format(results.plot_output_path, results.output_format) 
    fig.savefig(output_file)  # Save the figure
    print("Saved file to {0}".format(output_file))
    plt.close()


def plot_BTF(results):

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for model in results.models:

        model_label = model.model_label
        color = model.color
        marker = model.marker

        ax.scatter(model.BTF_vel, model.BTF_mass, marker=marker, s=1,
                   color=color, alpha=0.5, label=model_label + " Sb/c galaxies")

    ax.set_xlim([1.4, 2.6])
    ax.set_ylim([8.0, 12.0])

    ax.xaxis.set_minor_locator(plt.MultipleLocator(0.05))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(0.25))

    ax.set_xlabel(r"$\log_{10}V_{max}\ (km/s)$")
    ax.set_ylabel(r"$\log_{10}\ M_{\mathrm{bar}}\ (M_{\odot})$")

    ax = obs.plot_btf_data(ax) 

    adjust_legend(ax, location="upper left", scatter_plot=1)
        
    output_file = "{0}/4.BaryonicTullyFisher{1}".format(results.plot_output_path, results.output_format) 
    fig.savefig(output_file)
    print("Saved file to {0}".format(output_file))
    plt.close()
        

def plot_sSFR(results):

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for model in results.models:

        model_label = model.model_label
        color = model.color
        marker = model.marker

        ax.scatter(model.sSFR_mass, model.sSFR_sSFR, marker=marker, s=1, color=color,
                   alpha=0.5, label=model_label)

    # Overplot a dividing line between passive and SF galaxies. 
    w = np.arange(7.0, 13.0, 1.0)
    min_sSFRcut = np.min([model.sSFRcut for model in results.models]) 
    ax.plot(w, w/w*min_sSFRcut, "b:", lw=2.0)

    ax.set_xlabel(r"$\log_{10} M_{\mathrm{stars}}\ (M_{\odot})$")
    ax.set_ylabel(r"$\log_{10}\ s\mathrm{SFR}\ (\mathrm{yr^{-1}})$")

    ax.set_xlim([8.0, 12.0])
    ax.set_ylim([-16.0, -8.0])

    ax.xaxis.set_minor_locator(plt.MultipleLocator(0.05))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(0.25))

    adjust_legend(ax, scatter_plot=1)

    output_file = "{0}/5.SpecificStarFormationRate{1}".format(results.plot_output_path, results.output_format) 
    fig.savefig(output_file)
    print("Saved file to {0}".format(output_file))
    plt.close()


def plot_gas_frac(results):
    
    fig = plt.figure()
    ax = fig.add_subplot(111)

    for model in results.models:

        model_label = model.model_label
        color = model.color
        marker = model.marker

        ax.scatter(model.gas_frac_mass, model.gas_frac, marker=marker, s=1, color=color,
                   alpha=0.5, label=model_label + " Sb/c galaxies")

    ax.set_xlabel(r"$\log_{10} M_{\mathrm{stars}}\ (M_{\odot})$")
    ax.set_ylabel(r"$\mathrm{Cold\ Mass\ /\ (Cold+Stellar\ Mass)}$")

    ax.set_xlim([8.0, 12.0])
    ax.set_ylim([0.0, 1.0])

    ax.xaxis.set_minor_locator(plt.MultipleLocator(0.05))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(0.25))

    adjust_legend(ax, scatter_plot=1)
       
    output_file = "{0}/6.GasFraction{1}".format(results.plot_output_path, results.output_format) 
    fig.savefig(output_file)
    print("Saved file to {0}".format(output_file))
    plt.close()
        

def plot_metallicity(results):

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for model in results.models:

        model_label = model.model_label
        color = model.color
        marker = model.marker

        ax.scatter(model.metallicity_mass, model.metallicity, marker=marker, s=1, color=color,
                   alpha=0.5, label=model_label + " galaxies")

    # Use the IMF of the zeroth model to scale the observational results.
    zeroth_IMF = (results.models)[0].IMF
    ax = obs.plot_metallicity_data(ax, zeroth_IMF) 

    ax.set_xlabel(r"$\log_{10} M_{\mathrm{stars}}\ (M_{\odot})$")
    ax.set_ylabel(r"$12\ +\ \log_{10}[\mathrm{O/H}]$")

    ax.set_xlim([8.0, 12.0])
    ax.set_ylim([8.0, 9.5])

    ax.xaxis.set_minor_locator(plt.MultipleLocator(0.05))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(0.25))

    adjust_legend(ax, location="upper right", scatter_plot=1)
   
    output_file = "{0}/7.Metallicity{1}".format(results.plot_output_path, results.output_format) 
    fig.savefig(output_file)
    print("Saved file to {0}".format(output_file))
    plt.close()
        

def plot_bh_bulge(results):

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for model in results.models:

        model_label = model.model_label
        color = model.color
        marker = model.marker

        ax.scatter(model.bulge_mass, model.bh_mass, marker=marker, s=1, color=color,
                   alpha=0.5, label=model_label + " galaxies")

    ax = obs.plot_bh_bulge_data(ax) 

    ax.set_xlabel(r"$\log\ M_{\mathrm{bulge}}\ (M_{\odot})$")
    ax.set_ylabel(r"$\log\ M_{\mathrm{BH}}\ (M_{\odot})$")

    ax.set_xlim([8.0, 12.0])
    ax.set_ylim([6.0, 10.0])

    ax.xaxis.set_minor_locator(plt.MultipleLocator(0.05))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(0.25))

    adjust_legend(ax, location="upper right", scatter_plot=1)
        
    output_file = "{0}/8.BlackHoleBulgeRelationship{1}".format(results.plot_output_path, results.output_format) 
    fig.savefig(output_file)
    print("Saved file to {0}".format(output_file))
    plt.close()
        

def plot_quiescent(results, plot_sub_populations=1):

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for model in results.models:

        model_label = model.model_label
        color = model.color
        linestyle = model.linestyle

        # Set the x-axis values to be the centre of the bins.
        bin_middles = model.stellar_mass_bins + 0.5 * model.stellar_bin_width

        # We will keep the colour scheme consistent, but change the line styles.
        ax.plot(bin_middles[:-1], model.quiescent_galaxy_counts / model.SMF,
                label=model_label + " All", color=color, linestyle="-") 

        if results.num_models == 1 or plot_sub_populations:
            ax.plot(bin_middles[:-1], model.quiescent_centrals_counts / model.centrals_MF,
                    label=model_label + " Centrals", color=color, linestyle="--") 

            ax.plot(bin_middles[:-1], model.quiescent_satellites_counts / model.satellites_MF,
                    label=model_label + " Satellites", color=color, linestyle="-.") 

    ax.set_xlabel(r"$\log_{10} M_{\mathrm{stellar}}\ (M_{\odot})$")
    ax.set_ylabel(r"$\mathrm{Quescient\ Fraction}$")

    ax.set_xlim([8.0, 12.0])
    ax.set_ylim([0.0, 1.05])

    ax.xaxis.set_minor_locator(plt.MultipleLocator(0.25))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(0.10))

    adjust_legend(ax, location="upper left", scatter_plot=0)
        
    output_file = "{0}/9.QuiescentFraction{1}".format(results.plot_output_path, results.output_format) 
    fig.savefig(output_file)
    print("Saved file to {0}".format(output_file))
    plt.close()


def plot_bulge_mass_fraction(results, plot_var=1):

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for model in results.models:

        model_label = model.model_label
        color = model.color
        linestyle = model.linestyle

        # Set the x-axis values to be the centre of the bins.
        bin_middles = model.stellar_mass_bins + 0.5 * model.stellar_bin_width

        # Remember we need to average the properties in each bin.
        bulge_mean = model.fraction_bulge_sum / model.SMF
        disk_mean = model.fraction_disk_sum / model.SMF

        # The variance has already been weighted when we calculated it.
        bulge_var = model.fraction_bulge_var
        disk_var = model.fraction_disk_var

        # We will keep the colour scheme consistent, but change the line styles.
        ax.plot(bin_middles[:-1], bulge_mean, label=model_label + " bulge",
                color=color, linestyle="-")
        ax.plot(bin_middles[:-1], disk_mean, label=model_label + " disk",
                color=color, linestyle="--")

        if plot_var:
            ax.fill_between(bin_middles[:-1], bulge_mean+bulge_var, bulge_mean-bulge_var,
                            facecolor=color, alpha=0.25)
            ax.fill_between(bin_middles[:-1], disk_mean+disk_var, disk_mean-disk_var,
                            facecolor=color, alpha=0.25)

    ax.set_xlabel(r"$\log_{10} M_{\mathrm{stars}}\ (M_{\odot})$")
    ax.set_ylabel(r"$\mathrm{Stellar\ Mass\ Fraction}$")

    ax.set_xlim([8.0, 12.0])
    ax.set_ylim([0.0, 1.05])

    ax.xaxis.set_minor_locator(plt.MultipleLocator(0.25))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(0.10))

    adjust_legend(ax, location="upper left", scatter_plot=0)

    output_file = "{0}/10.BulgeMassFraction{1}".format(results.plot_output_path, results.output_format) 
    fig.savefig(output_file)
    print("Saved file to {0}".format(output_file))
    plt.close()


def plot_baryon_fraction(results, plot_sub_populations=1):

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for model in results.models:

        model_label = model.model_label
        color = model.color
        linestyle = model.linestyle

        # Set the x-axis values to be the centre of the bins.
        bin_middles = model.halo_mass_bins + 0.5 * model.halo_bin_width

        # Remember we need to average the properties in each bin.
        baryon_mean = model.halo_baryon_fraction_sum / model.fof_HMF

        # We will keep the linestyle constant but change the color. 
        ax.plot(bin_middles[:-1], baryon_mean, label=model_label + " Total",
                color=color, linestyle=linestyle)

        # If we have multiple models, we want to be careful of overcrowding the plot.
        if results.num_models == 1 or plot_sub_populations:
            attrs = ["stars", "cold", "hot", "ejected", "ICS"]
            labels = ["Stars", "Cold", "Hot", "Ejected", "ICS"]
            colors = ["k", "b", "r", "g", "y"]

            for (attr, label, color) in zip(attrs, labels, colors):
                attrname = "halo_{0}_fraction_sum".format(attr) 
                mean = getattr(model, attrname) / model.fof_HMF

                ax.plot(bin_middles[:-1], mean, label=model_label + " " + label,
                        color=color, linestyle=linestyle)

    ax.set_xlabel(r"$\mathrm{Central}\ \log_{10} M_{\mathrm{vir}}\ (M_{\odot})$")
    ax.set_ylabel(r"$\mathrm{Baryon\ Fraction}$")

    # Find the models that have the smallest/largest stellar mass bin.
    xlim_min = np.min([model.halo_mass_bins for model in results.models]) - 0.2
    xlim_max = np.max([model.halo_mass_bins for model in results.models]) + 0.2
    ax.set_xlim([xlim_min, xlim_max])
    ax.set_ylim([0.0, 0.23])

    ax.xaxis.set_minor_locator(plt.MultipleLocator(0.25))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(0.05))

    adjust_legend(ax, location="upper left", scatter_plot=0)

    output_file = "{0}/11.BaryonFraction{1}".format(results.plot_output_path, results.output_format)
    fig.savefig(output_file)
    print("Saved file to {0}".format(output_file))
    plt.close()


def plot_spin_distribution(results):

    fig = plt.figure()
    ax = fig.add_subplot(111)

    max_counts = -999

    for model in results.models:

        model_label = model.model_label
        color = model.color
        linestyle = model.linestyle

        # Set the x-axis values to be the centre of the bins.
        bin_middles = model.spin_bins + 0.5 * model.spin_bin_width

        # Normalize by number of galaxies; allows better comparison between models.
        norm_counts = model.spin_counts / model.num_gals / model.spin_bin_width
        ax.plot(bin_middles[:-1], norm_counts, label=model_label, color=color, linestyle=linestyle)

        if np.max(norm_counts) > max_counts:
            max_counts = np.max(norm_counts)

    ax.set_xlabel(r"$\mathrm{Spin\ Parameter}$")
    ax.set_ylabel(r"$\mathrm{Normalized\ Count}$")

    ax.set_xlim([-0.02, 0.5])
    ax.set_ylim([0.0, max_counts*1.15])

    adjust_legend(ax, location="upper right", scatter_plot=0)

    output_file = "{0}/12.SpinDistribution{1}".format(results.plot_output_path, results.output_format)
    fig.savefig(output_file)
    print("Saved file to {0}".format(output_file))
    plt.close()


def plot_velocity_distribution(results):

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # First do some junk plotting to get legend correct. We keep the linestyles but
    # use different colours.
    for model in results.models:
        ax.plot(np.nan, np.nan, color="m", linestyle=model.linestyle,
                label=model.model_label)

    for (model_num, model) in enumerate(results.models):

        linestyle = model.linestyle

        # Set the x-axis values to be the centre of the bins.
        bin_middles = model.vel_bins + 0.5 * model.vel_bin_width

        labels = ["los", "x", "y", "z"]
        colors = ["k", "r", "g", "b"]
        vels = [model.los_vel_counts, model.x_vel_counts,
                model.y_vel_counts, model.z_vel_counts]
        normalization = model.vel_bin_width * model.num_gals

        for (vel, label, color) in zip(vels, labels, colors):

            # We only want the labels to be plotted once.
            if model_num == 0:
                label = label
            else:
                label = ""

            ax.plot(bin_middles[:-1], vel / normalization, color=color, label=label,
                    linestyle=linestyle)

    ax.set_xlabel(r"$\mathrm{Velocity / H}_{0}$")
    ax.set_ylabel(r"$\mathrm{Box\ Normalised\ Count}$")

    ax.set_yscale("log", nonposy="clip")

    # Find the models that have the smallest/largest stellar mass bin.
    xlim_min = np.min([model.vel_bins for model in results.models]) - 3
    xlim_max = np.max([model.vel_bins for model in results.models]) + 3
    ax.set_xlim([xlim_min, xlim_max])
    ax.set_ylim([1e-5, 0.5])

    ax.xaxis.set_minor_locator(plt.MultipleLocator(5))

    adjust_legend(ax, location="upper left", scatter_plot=0)

    output_file = "{0}/13.VelocityDistribution{1}".format(results.plot_output_path, results.output_format)
    fig.savefig(output_file)
    print("Saved file to {0}".format(output_file))
    plt.close()


def plot_mass_reservoirs(results):

    # This scatter plot will be messy so we're going to make one for each model.
    for model in results.models:

        fig = plt.figure()
        ax = fig.add_subplot(111)

        model_label = model.model_label
        marker = model.marker

        components = ["StellarMass", "ColdGas", "HotGas", "EjectedMass",
                      "IntraClusterStars"]
        attribute_names = ["stars", "cold", "hot", "ejected", "ICS"]
        labels = ["Stars", "Cold Gas", "Hot Gas", "Ejected Gas", "Intracluster Stars"]
        colors = ["k", "b", "r", "g", "y"]

        for (component, attribute_name, color, label) in zip(components,
                                                             attribute_names, colors,
                                                             labels):

            attr_name = "reservoir_{0}".format(attribute_name)
            ax.scatter(model.reservoir_mvir, getattr(model, attr_name), marker=marker,
                       s=0.3, color=color, label=label)

        ax.set_xlabel(r"$\log\ M_{\mathrm{vir}}\ (M_{\odot})$")
        ax.set_ylabel(r"$\mathrm{Reservoir\ Mass\ (M_{\odot})}$")

        ax.set_xlim([10.0, 14.0])
        ax.set_ylim([7.5, 12.5])

        ax.xaxis.set_minor_locator(plt.MultipleLocator(0.25))
        ax.yaxis.set_minor_locator(plt.MultipleLocator(0.25))

        adjust_legend(ax, location="upper left", scatter_plot=1)

        output_file = "{0}/14.MassReservoirs_{1}{2}".format(results.plot_output_path,
                                                           model_label, results.output_format)
        fig.savefig(output_file)
        print("Saved file to {0}".format(output_file))
        plt.close()


def plot_spatial_distribution(results):

    fig = plt.figure()

    # 4-panel plot.
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)

    for model in results.models:

        model_label = model.model_label
        color = model.color
        linestyle = model.linestyle
        marker = model.marker

        ax1.scatter(model.x_pos, model.y_pos, marker=marker, s=0.3, color=color,
                    alpha=0.5)
        ax2.scatter(model.x_pos, model.z_pos, marker=marker, s=0.3, color=color,
                    alpha=0.5)
        ax3.scatter(model.y_pos, model.z_pos, marker=marker, s=0.3, color=color,
                    alpha=0.5)

        # The bottom right panel will only contain the legend.
        # For some odd reason, plotting `np.nan` causes some legend entries to not
        # appear. Plot junk and we'll adjust the axis to not show it.
        ax4.scatter(-999, -999, marker=marker, color=color, label=model_label)
        ax4.axis("off")

    ax1.set_xlabel(r"$\mathrm{x}\ [\mathrm{Mpc}/h]$")
    ax1.set_ylabel(r"$\mathrm{y}\ [\mathrm{Mpc}/h]$")

    ax2.set_xlabel(r"$\mathrm{x}\ [\mathrm{Mpc}/h]$")
    ax2.set_ylabel(r"$\mathrm{z}\ [\mathrm{Mpc}/h]$")

    ax3.set_xlabel(r"$\mathrm{y}\ [\mathrm{Mpc}/h]$")
    ax3.set_ylabel(r"$\mathrm{z}\ [\mathrm{Mpc}/h]$")

    # Find the model with the largest box. 
    max_box = np.min([model.box_size for model in results.models]) - 0.5
    buffer = max_box*0.05
    for ax in [ax1, ax2, ax3, ax4]:
        ax.set_xlim([0.0-buffer, max_box+buffer])
        ax.set_ylim([0.0-buffer, max_box+buffer])

        ax.xaxis.set_minor_locator(plt.MultipleLocator(5))
        ax.yaxis.set_minor_locator(plt.MultipleLocator(5))

    adjust_legend(ax4, location="upper left", scatter_plot=1)

    # Make sure everything remains nicely layed out.
    fig.tight_layout()

    output_file = "{0}/15.SpatialDistribution{1}".format(results.plot_output_path, results.output_format)
    fig.savefig(output_file)
    print("Saved file to {0}".format(output_file))
    plt.close()


def plot_spatial_3d(gals, output_file, box_size):

    from mpl_toolkits.mplot3d import Axes3D

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    w = sample(list(np.arange(len(gals))), 10000)

    ax.scatter(gals["Pos"][w,0], gals["Pos"][w,1], gals["Pos"][w,2], alpha=0.5)

    ax.set_xlim([0.0, box_size])
    ax.set_ylim([0.0, box_size])
    ax.set_zlim([0.0, box_size])

    ax.set_xlabel(r"$\mathbf{x \: [h^{-1}Mpc]}$")
    ax.set_ylabel(r"$\mathbf{y \: [h^{-1}Mpc]}$")
    ax.set_zlabel(r"$\mathbf{z \: [h^{-1}Mpc]}$")

    fig.savefig(output_file)
    print("Saved file to {0}".format(output_file))
    plt.close()

