#!/usr/bin/env python
"""
Example script for plotting the data from the Mini-Millennium simulation.

To add your own data format, create a subclass module (e.g., ``sage_binary.py``).
This subclass module needs methods ``set_cosmology()``, ``determine_num_gals()``
and  ``read_gals()``.

To calculate and plot extra properties, first add the name of your new plot to the
``plot_toggles`` dictionary. Then you will need to create a new module (i.e., a new
``.py`` file) to house all of your calculation and plotting functions. These two modules
should be specified as the ``module_name`` values for the ``generate_function_dict``
functions.

Then, for each new property, create a new function to calculate your properties. We
recommend naming this ``calc_<Naome of your plot toggle>``. To plot your new property,
create a new function with the suggested name ``plot_<Name of your plot toggle>``.  WHILE
THE PREFIX OF THESE CAN CHANGE, THEY MUST ALWAYS BE ``<prefix><Name of your plot
toggle>``.  THESE FUNCTIONS MUST HAVE THE FUNCTION SIGNATURE ``func(Model Class, gals)``.
Refer to the ``calc_`` and ``plot_`` functions in ``model.py`` and ``plots.py``
respectively.

For example, to generate and plot data for the ``SMF`` plot, we have methods ``calc_SMF()``
and ``plot_SMF()``.

Refer to the documentation inside the ``model.py`` and ``plot.py`` modules for more
details.

Author: Jacob Seiler.
"""

import sage_analysis.model
import sage_analysis.plots

# Import the subclasses that handle the different SAGE output formats.
from sage_analysis.sage_binary import SageBinaryData

try:
    from sage_analysis.sage_hdf5 import SageHdf5Data
except ImportError:
    print("h5py not found.  If you're reading in HDF5 output from SAGE, please install "
          "this package.")

import numpy as np

# Sometimes we divide a galaxy that has zero mass (e.g., no cold gas). Ignore these
# warnings as they spam stdout.
old_error_settings = np.seterr()
np.seterr(all="ignore")

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


def generate_func_dict(plot_toggles, module_name, function_prefix):
    """
    Generates a dictionary where the keys are the function name and the value is the
    function itself.  Functions are only generated when the ``plot_toggles`` value is
    specified.

    Functions are required to be named ``<module_prefix><function_prefix><plot_toggle_key>``
    For example, the default calculation function are kept in the ``model.py`` module and
    are named ``calc_<toggle>``.  E.g., ``sage_analysis.model.calc_SMF()``,
    ``sage_analysis.model.calc_BTF()``, ``sage_analysis.model.calc_sSFR()`` etc.

    Parameters
    ----------

    plot_toggles : dictionary
        Dictionary specifying the name of each property/plot and whether the values
        will be generated + plotted. A value of 1 denotes plotting, whilst a value of
        0 denotes not plotting.  Entries with a value of 1 will be added to the function
        dictionary.

        Example
        -------

        plot_toggles = {"SMF" : 0,
                        "BTF" : 1,
                        "sSFR" : 1}

    module_prefix : string
        Name of the module where the functions are located. If the functions are located
        in this module, pass an empty string "".

        Example
        -------

        module_prefix = "sage_analysis.model"

    function_prefix : string
        Prefix that is added to the start of each function.

        Example
        -------

        function_prefix = "calc_"
    """

    # If the functions are defined in this module, then `module_name` is empty. Need to
    # treat this differently.
    import sys
    if module_name == "":

        # Get the name of this module.
        module = sys.modules[__name__]

    else:

        # Otherwise, check if the specified module is present.
        try:
            module = sys.modules[module_name]
        except KeyError:
            msg = "Module {0} has not been imported.\nPerhaps you need to create an empty " \
                  "`__init__.py` file to ensure your package can be imported.".format(module_name)
            raise KeyError(msg)

    # Only populate those methods that have been marked in the `plot_toggles`
    # dictionary.
    func_dict = {}
    for toggle in plot_toggles.keys():
        if plot_toggles[toggle]:

            func_name = "{0}{1}".format(function_prefix, toggle)

            # Be careful.  Maybe the func for a specified `plot_toggle` value wasn't
            # added to the module.
            try:
                func = getattr(module, func_name)
            except AttributeError:
                msg = "Tried to get the func named '{0}' corresponding to " \
                      "'plot_toggle' value '{1}'.  However, no func named '{0}' " \
                      "could be found in '{2}' module.".format(func_name,
                      toggle, module_prefix)
                raise AttributeError(msg)

            func_dict[func_name] = func

    return func_dict


if __name__ == "__main__":

    import os

    # We support the plotting of an arbitrary number of models. To do so, simply add the
    # extra variables specifying the path to the model directory and other variables.
    # E.g., 'model1_sage_output_format = ...", "model1_dir_name = ...".
    # `first_file`, `last_file`, `simulation` and `num_tree_files` only need to be
    # specified if using binary output. HDF5 will automatically detect these.
    # `hdf5_snapshot` is only nedded if using HDF5 output.

    model0_snapshot = 63
    model0_IMF = "Chabrier"  # Chabrier or Salpeter.
    model0_model_label = "Mini-Millennium"  # Goes on the axis.
    model0_sage_file = "../input/millennium.par"

    # Then extend each of these lists for all the models that you want to plot.
    # E.g., 'dir_names = [model0_dir_name, model1_dir_name, ..., modelN_dir_name]
    IMFs = [model0_IMF]
    labels = [model0_model_label]
    snapshots = [model0_snapshot]
    sage_files = [model0_sage_file]

    # A couple of extra variables...
    plot_output_format    = ".png"
    plot_output_path = "./plots"  # Will be created if path doesn't exist.

    # These toggles specify which plots you want to be made.
    plot_toggles = {"SMF"             : 1,  # Stellar mass function.
                    "BMF"             : 1,  # Baryonic mass function.
                    "GMF"             : 1,  # Gas mass function (cold gas).
                    "BTF"             : 1,  # Baryonic Tully-Fisher.
                    "sSFR"            : 1,  # Specific star formation rate.
                    "gas_frac"        : 1,  # Fraction of galaxy that is cold gas.
                    "metallicity"     : 1,  # Metallicity scatter plot.
                    "bh_bulge"        : 1,  # Black hole-bulge relationship.
                    "quiescent"       : 1,  # Fraction of galaxies that are quiescent.
                    "bulge_fraction"  : 1,  # Fraction of galaxies that are bulge/disc dominated.
                    "baryon_fraction" : 1,  # Fraction of baryons in galaxy/reservoir.
                    "reservoirs"      : 1,  # Mass in each reservoir.
                    "spatial"         : 1}  # Spatial distribution of galaxies.

    ############## DO NOT TOUCH BELOW #############
    ### IF NOT ADDING EXTRA PROPERTIES OR PLOTS ###
    ############## DO NOT TOUCH BELOW #############

    # Generate directory for output plots.
    if not os.path.exists(plot_output_path):
        os.makedirs(plot_output_path)

    # Generate a dictionary for each model containing the required information.
    # We store these in `model_dicts` which will be a list of dictionaries.
    model_dicts = []
    for IMF, model_label, snapshot, sage_file in zip(IMFs, labels, snapshots, sage_files):
        this_model_dict = {"IMF": IMF,
                           "model_label": model_label,
                           "snapshot": snapshot,
                           "sage_file": sage_file}

        model_dicts.append(this_model_dict)

    # Go through each model and calculate all the required properties.
    models = []
    for model_dict in model_dicts:

        my_model = sage_analysis.model.Model(model_dict)

        if my_model.sage_output_format == "sage_binary":
            my_model.data_subclass = SageBinaryData(my_model)
        elif my_model.sage_output_format == "sage_hdf5":
            my_model.data_subclass = SageHdf5Data(my_model)

        my_model.data_subclass.set_cosmology(my_model)
        exit()

        # Some properties require the stellar mass function to normalize their values. For
        # these, the SMF plot toggle is explicitly required.
        try:
            if plot_toggles["SMF"]:
                my_model.calc_SMF = True
            else:
                my_model.calc_SMF = False
        except KeyError:
                my_model.calc_SMF = False

        # Then populate the `calculation_methods` dictionary. This dictionary will control
        # which properties each model will calculate.  The dictionary is populated using
        # the plot_toggles defined above.
        # Our functions are inside the `model.py` module and are named "calc_<toggle>". If
        # your functions are in a different module or different function prefix, change it
        # here.
        # ALL FUNCTIONS MUST HAVE A FUNCTION SIGNATURE `func(Model, gals)`.
        calculation_functions = generate_func_dict(plot_toggles, module_name="sage_analysis.model",
                                                   function_prefix="calc_")

        # Finally, before we calculate the properties, we need to decide how each property
        # is stored. Properties can be binned (e.g., how many galaxies with mass between 10^8.0
        # and 10^8.1), scatter plotted (e.g., for 1000 galaxies plot the specific star
        # formation rate versus stellar mass) or a single number (e.g., the sum
        # of the star formation rate at a snapshot). Properties can be accessed using
        # `Model.properties["property_name"]`; e.g., `Model.properties["SMF"]`.

        # First let's do the properties binned on stellar mass. The bins themselves can be
        # accessed using `Model.bins["bin_name"]`; e.g., `Model.bins["stellar_mass_bins"]
        stellar_properties = ["SMF", "red_SMF", "blue_SMF", "BMF", "GMF",
                              "centrals_MF", "satellites_MF", "quiescent_galaxy_counts",
                              "quiescent_centrals_counts", "quiescent_satellites_counts",
                              "fraction_bulge_sum", "fraction_bulge_var",
                              "fraction_disk_sum", "fraction_disk_var"]
        my_model.init_binned_properties(8.0, 12.0, 0.1, "stellar_mass_bins",
                                        stellar_properties)

        # Properties binned on halo mass.
        halo_properties = ["fof_HMF"]
        component_properties = ["halo_{0}_fraction_sum".format(component) for component in
                               ["baryon", "stars", "cold", "hot", "ejected", "ICS", "bh"]]
        my_model.init_binned_properties(10.0, 14.0, 0.1, "halo_mass_bins",
                                        halo_properties+component_properties)

        # Now properties that will be extended as lists.
        scatter_properties = ["BTF_mass", "BTF_vel", "sSFR_mass", "sSFR_sSFR",
                              "gas_frac_mass", "gas_frac", "metallicity_mass",
                              "metallicity", "bh_mass", "bulge_mass", "reservoir_mvir",
                              "reservoir_stars", "reservoir_cold", "reservoir_hot",
                              "reservoir_ejected", "reservoir_ICS", "x_pos",
                              "y_pos", "z_pos"]
        my_model.init_scatter_properties(scatter_properties)

        # Finally those properties that are stored as a single number.
        single_properties = []
        my_model.init_single_properties(single_properties)

        # To be more memory concious, we calculate the required properties on a
        # file-by-file basis. This ensures we do not keep ALL the galaxy data in memory.
        my_model.calc_properties_all_files(calculation_functions, debug=False)

        models.append(my_model)

    # Similar to the calculation functions, all of the plotting functions are in the
    # `plots.py` module and are labelled `plot_<toggle>`.
    plot_functions = generate_func_dict(plot_toggles, module_name="sage_analysis.plots",
                                        function_prefix="plot_")

    # Now do the plotting.
    for plot_func in plot_functions.values():
        plot_func(models, plot_output_path, plot_output_format)

    # Set the error settings to the previous ones so we don't annoy the user.
    np.seterr(divide=old_error_settings["divide"], over=old_error_settings["over"],
              under=old_error_settings["under"], invalid=old_error_settings["invalid"])
