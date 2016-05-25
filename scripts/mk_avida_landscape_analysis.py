#!/usr/bin/python2
import json, os

"""
This script takes bank of mutants and generates avida analyze file that will phenotype all found mutants.
"""

def main():
    """
    """
    # Load mutation landscape settings
    settings = None
    with open("param/mutational_landscape_settings.json", "r") as fp:
        settings = json.load(fp)
    # Grab some important locations
    mutant_src_dir = settings["mutant_dest_dir"]
    analysis_script_content = ""
    # Each directory in the mutant src directory is an organism's mutational landscape
    org_landscapes = [d for d in os.listdir(mutant_src_dir)]
    for org in org_landscapes:
        org_dir = os.path.join(mutant_src_dir, org)
        # Get list of mutants in landscape
        mutants = [m for m in os.listdir(org_dir) if ".gen" in m]
        for mutant in mutants:
            mutant_name = mutant.split(".")[0]
            org_to_load = os.path.join(org_dir, mutant)
            # Build analysis code for this mutant
            mutant_analysis = '''###### %s ######
PURGE_BATCH 0
PURGE_BATCH 1
SET_BATCH 0
LOAD_ORGANISM %s
DUPLICATE 0 1
## nand+not- tests ##
SET_BATCH 0
SET v nand+not-
SetReactionValue NOT -1.0
SetReactionValue NAND 1.0
RECALC
DETAIL landscape_analysis/%s/%s/$v/mutant.dat update_born depth parent_dist viable fitness length sequence total_cpus num_cpus gest_time efficiency task.0 task.1
## nand-not+ tests ##
SET_BATCH 1
SET v nand-not+
SetReactionValue NOT 1.0
SetReactionValue NAND -1.0
RECALC
DETAIL landscape_analysis/%s/%s/$v/mutant.dat update_born depth parent_dist viable fitness length sequence total_cpus num_cpus gest_time efficiency task.0 task.1
''' % (mutant, org_to_load, org, mutant_name, org, mutant_name)
            analysis_script_content += mutant_analysis
    with open("landscape_analyze.cfg", "w") as fp:
        fp.write(analysis_script_content)

if __name__ == "__main__":
    main()
