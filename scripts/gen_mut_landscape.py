#!/usr/bin/python2
import json, os, copy

from utilities.parse_avida_output import inst_list_extract, genome_from_genfile
from utilities.utilities import mkdir_p

"""
This script takes as organism genomes and generates all N-step (1 to start) mutational neighbors.
"""

def stringize_genome(genome, description = ""):
    """
    Given list representation of genome (list of instructions) and a description,
     return a string that contains the content for a genome file that could be saved and read by Avida in analyze mode.
    """
    description = "# %s \n" % description
    genome = "\n".join(genome)
    return description + "\n" + genome

def main():
    """
    Generates all N-Step mutational neighbors given settings defined in specified parameter file.
    Process:
     1) Get list of organisms to generate a mutational landscape for
     2) Extract list of all possible 'site bases' (all possible instructions)
     3) For each organism:
        a) Extract organism ID, genome
    """
    settings = None
    with open("param/mutational_landscape_settings.json", "r") as fp:
        settings = json.load(fp)
    # Grab some important locations
    src_dir = settings["organism_source_dir"]
    dest_dir = settings["mutant_dest_dir"]
    inst_cfg = settings["instruction_list"]
    # Extract instruction list from specified configuration file.
    inst_list = None
    try:
        with open(inst_cfg, "r") as fp: inst_list = inst_list_extract(fp)
    except:
        print("Failed to extract instuction list from specified file.")
        exit(-1)
    # Find all of the organisms we'll be landscaping today.
    orgs_to_landscape = [o for o in os.listdir(src_dir) if ".gen" in o]
    print "Landscaping: %s" % str(orgs_to_landscape)
    print "Flowers: %s" % str(inst_list)
    for org in orgs_to_landscape:
        # Extract genome
        org_path = os.path.join(src_dir, org)
        genome = None
        with open(org_path, "r") as fp: genome = genome_from_genfile(fp)
        # Find/setup where we're dumping things
        org_dest = os.path.join(dest_dir, org.split(".")[0])
        mkdir_p(org_dest)
        # Save out original genome
        with open(os.path.join(org_dest, "original.gen"), "w") as fp: fp.write(stringize_genome(genome, "original organism genome"))
        for site in xrange(0, len(genome)):
            for inst in inst_list:
                if inst == genome[site]: continue
                mutant = copy.deepcopy(genome)
                mutant[site] = inst
                desc = "@N %d: %s => %s" % (site, genome[site], mutant[site])
                mut_name = "N%d_%s.gen" % (site, mutant[site])
                with open(os.path.join(org_dest, mut_name), "w") as fp: fp.write(stringize_genome(mutant, desc))
    print "DONE"

if __name__ == "__main__":
    main()
