#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <limits.h>
#include <fcntl.h>
#include <unistd.h>

#include "core_allvars.h"
#include "core_save.h"
#include "core_utils.h"
#include "model_misc.h"

#include "io/save_gals_binary.h"

#ifdef HDF5
#include "io/save_gals_hdf5.h"
#endif

/* #define TREE_MUL_FAC        (1000000000LL) */
/* #define THISTASK_MUL_FAC      (1000000000000000LL) */

// Local Proto-Types //

int32_t generate_galaxy_indices(const struct halo_data *halos, const struct halo_aux_data *haloaux,
                                struct GALAXY *halogal, const int64_t numgals,
                                const int64_t treenr, const int32_t filenr,
                                const int64_t filenr_mulfac, const int64_t forestnr_mulfac);

// Externally Visible Functions //

// Open up all the required output files and remember their file handles.  These are placed into
// `save_info` for access later.
int32_t initialize_galaxy_files(const int rank, const struct forest_info *forest_info, struct save_info *save_info, const struct params *run_params)
{
    int32_t status;

    if(run_params->NOUT > ABSOLUTEMAXSNAPS) {
        fprintf(stderr,"Error: Attempting to write snapshot = '%d' will exceed allocated memory space for '%d' snapshots\n",
                run_params->NOUT, ABSOLUTEMAXSNAPS);
        fprintf(stderr,"To fix this error, simply increase the value of `ABSOLUTEMAXSNAPS` and recompile\n");
        return INVALID_OPTION_IN_PARAMS;
    }

    switch(run_params->OutputFormat) {

    case(sage_binary):
      status = initialize_binary_galaxy_files(rank, forest_info, save_info, run_params);
      break;

#ifdef HDF5
    case(sage_hdf5):
      status = initialize_hdf5_galaxy_files(rank, save_info, run_params);
      break;
#endif

    default:
      fprintf(stderr, "Error: Unknown OutputFormat in `initialize_galaxy_files()`.\n");
      status = INVALID_OPTION_IN_PARAMS;
      break;

    }

    return status;
}


// Write all the galaxy properties to file.
int32_t save_galaxies(const int64_t task_forestnr, const int numgals, struct halo_data *halos,
                      struct forest_info *forest_info,
                      struct halo_aux_data *haloaux, struct GALAXY *halogal,
                      struct save_info *save_info, const struct params *run_params)
{
    int32_t status = EXIT_FAILURE;

    // Reset the output galaxy count.
    int32_t OutputGalCount[run_params->MAXSNAPS];
    for(int32_t snap_idx = 0; snap_idx < run_params->MAXSNAPS; snap_idx++) {
        OutputGalCount[snap_idx] = 0;
    }

    // Track the order in which galaxies are written.
    int32_t *OutputGalOrder = calloc(numgals, sizeof(*(OutputGalOrder)));
    if(OutputGalOrder == NULL) {
        fprintf(stderr,"Error: Could not allocate memory for %d int elements in array `OutputGalOrder`\n", numgals);
        return MALLOC_FAILURE;
    }

    for(int32_t gal_idx = 0; gal_idx < numgals; gal_idx++) {
        OutputGalOrder[gal_idx] = -1;
        haloaux[gal_idx].output_snap_n = -1;
    }

    // First update mergeIntoID to point to the correct galaxy in the output.
    for(int32_t snap_idx = 0; snap_idx < run_params->NOUT; snap_idx++) {
        for(int32_t gal_idx  = 0; gal_idx < numgals; gal_idx++) {
            if(halogal[gal_idx].SnapNum == run_params->ListOutputSnaps[snap_idx]) {
                OutputGalOrder[gal_idx] = OutputGalCount[snap_idx];
                OutputGalCount[snap_idx]++;
                haloaux[gal_idx].output_snap_n = snap_idx;
            }
        }
    }

    for(int32_t gal_idx = 0; gal_idx < numgals; gal_idx++) {
        if(halogal[gal_idx].mergeIntoID > -1) {
            halogal[gal_idx].mergeIntoID = OutputGalOrder[halogal[gal_idx].mergeIntoID];
        }
    }

    // Generate a unique GalaxyIndex for each galaxy.  To do this, we need to know a) the tree
    // number **from the original file** and b) the file number the tree is from.  Note: The tree
    // number we need is different from the ``forestnr`` parameter being used to process the forest
    // within SAGE; that ``forestnr`` is **task local** and potentially does **NOT** correspond to
    // the tree number in the original simulation file.

    // When we allocated the trees to each task, we stored the correct tree and file numbers in
    // arrays indexed by the ``forestnr`` parameter.  Furthermore, since all galaxies being
    // processed belong to a single tree (by definition) and because trees cannot be split over
    // multiple files, we can access the tree + fiel number once and use it for all galaxies being
    // saved.
    int64_t original_treenr = forest_info->original_treenr[task_forestnr];
    int32_t original_filenr = forest_info->FileNr[task_forestnr];

    status = generate_galaxy_indices(halos, haloaux, halogal, numgals,
                                     original_treenr, original_filenr,
                                     run_params->FileNr_Mulfac, run_params->ForestNr_Mulfac);
    if(status != EXIT_SUCCESS) {
        return EXIT_FAILURE;
    }

    // All of the tracking arrays set up, time to perform the actual writing.
    switch(run_params->OutputFormat) {

    case(sage_binary):
        status = save_binary_galaxies(task_forestnr, numgals, OutputGalCount, forest_info,
                                      halos, haloaux, halogal, save_info, run_params);
        break;

#ifdef HDF5
    case(sage_hdf5):
        status = save_hdf5_galaxies(task_forestnr, numgals, forest_info, halos, haloaux, halogal, save_info, run_params);
        break;
#endif

    default:
        fprintf(stderr, "Uknown OutputFormat in `save_galaxies()`.\n");
        status = INVALID_OPTION_IN_PARAMS;

    }

    free(OutputGalOrder);

    return status;
}


// Write any remaining attributes or header information, close all the open files and free all the
// relevant dataspaces.
int32_t finalize_galaxy_files(const struct forest_info *forest_info, struct save_info *save_info, const struct params *run_params)
{

    int32_t status = EXIT_FAILURE;

    switch(run_params->OutputFormat) {

    case(sage_binary):
        status = finalize_binary_galaxy_files(forest_info, save_info, run_params);
        break;

#ifdef HDF5
    case(sage_hdf5):
        status = finalize_hdf5_galaxy_files(forest_info, save_info, run_params);
        break;
#endif

    default:
        fprintf(stderr, "Error: Unknown OutputFormat in `finalize_galaxy_files()`.\n");
        status = INVALID_OPTION_IN_PARAMS;
        break;
    }

    return status;
}

// Local Functions //

/* #define TREE_MUL_FAC        (1000000000LL) */
/* #define THISTASK_MUL_FAC      (1000000000000000LL) */


// Generate a unique GalaxyIndex for each galaxy based on the file number, the file-local
// tree number and the tree-local galaxy number.  NOTE: Both the file number and the tree number are
// based on the **original simulation files**.  These may be different from the ``forestnr``
// parameter being used to process the forest within SAGE; that ``forestnr`` is **task local** and
// potentially does **NOT** correspond to the tree number in the original simulation file.
int32_t generate_galaxy_indices(const struct halo_data *halos, const struct halo_aux_data *haloaux,
                                struct GALAXY *halogal, const int64_t numgals,
                                const int64_t forestnr, const int32_t filenr,
                                const int64_t filenr_mulfac, const int64_t forestnr_mulfac)
{

    // Now generate the unique index for each galaxy.
    for(int64_t gal_idx = 0; gal_idx < numgals; ++gal_idx) {
        struct GALAXY *this_gal = &halogal[gal_idx];

        uint32_t GalaxyNr = this_gal->GalaxyNr;
        uint32_t CentralGalaxyNr = halogal[haloaux[halos[this_gal->HaloNr].FirstHaloInFOFgroup].FirstGalaxy].GalaxyNr;

        /*MS: check that the mechanism would produce unique galaxyindex within this run (across all tasks and all forests)*/
        if(GalaxyNr > forestnr_mulfac || (filenr_mulfac > 0 && forestnr*forestnr_mulfac > filenr_mulfac)) {
            fprintf(stderr, "When determining a unique Galaxy Number, we assume that the number of trees are less than %"PRId64". "
                    "This assumption has been broken.\n"
                    "Simulation trees file number %d\tOriginal tree number %"PRId64"\tGalaxy Number %d "
                    "forestnr_mulfac = %"PRId64" forestnr*forestnr_mulfac = %"PRId64"\n",
                    filenr_mulfac, filenr, forestnr, GalaxyNr, forestnr_mulfac, forestnr*forestnr_mulfac);
          return EXIT_FAILURE;
        }

        /*MS: 23/9/2019 Check if the multiplication will overflow 64-bit integer */
        if((forestnr > 0 && ((uint64_t) forestnr > (0xFFFFFFFFFFFFFFFFULL/(uint64_t) forestnr_mulfac))) ||
           (filenr > 0 && ((uint64_t) filenr > (0xFFFFFFFFFFFFFFFFULL/(uint64_t) filenr_mulfac)))) {
            fprintf(stderr,"Error: While generating an unique Galaxy Index. The multiplication required to "
                    "generate the ID will overflow 64-bit\n"
                    "forestnr = %"PRId64" forestnr_mulfac = %"PRId64" filenr = %d filenr_mulfac = %"PRId64"\n",
                    forestnr, forestnr_mulfac, filenr, filenr_mulfac);
            
            return EXIT_FAILURE;
        }

        const uint64_t id_from_forestnr = forestnr_mulfac * forestnr;
        const uint64_t id_from_filenr = filenr_mulfac * filenr;

        if(id_from_forestnr > (0xFFFFFFFFFFFFFFFFULL - id_from_filenr)) {
            fprintf(stderr,"Error: While generating an unique Galaxy Index. The addition required to generate the ID will overflow 64-bits \n");
            fprintf(stderr,"id_from_forestnr = %"PRIu64 "id_from_filenr = %"PRIu64"\n", id_from_forestnr, id_from_filenr);
            return EXIT_FAILURE;
        }
        
        const uint64_t id_from_forest_and_file = id_from_forestnr + id_from_filenr;
        if((GalaxyNr > (0xFFFFFFFFFFFFFFFFULL - id_from_forest_and_file)) ||
           (CentralGalaxyNr > (0xFFFFFFFFFFFFFFFFULL - id_from_forest_and_file))) {
            fprintf(stderr,"Error: While generating an unique Galaxy Index. The addition required to generate the ID will overflow 64-bits \n");
            fprintf(stderr,"id_from_forest_and_file = %"PRIu64" GalaxyNr = %u CentralGalaxyNr = %u\n", id_from_forest_and_file, GalaxyNr, CentralGalaxyNr);
            return EXIT_FAILURE;
        }
                
        // Everything is good, generate the index.
        this_gal->GalaxyIndex = GalaxyNr + id_from_forest_and_file;
        this_gal->CentralGalaxyIndex= CentralGalaxyNr + id_from_forest_and_file;
    }

    return EXIT_SUCCESS;

}

