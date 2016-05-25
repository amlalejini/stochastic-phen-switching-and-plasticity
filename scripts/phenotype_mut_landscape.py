#!/usr/bin/python2
from utilities.utilities import mkdir_p
from utilities.parse_avida_output import detail_file_extract
import json, os

"""
Using parameters defined in specified .json settings file, loads landscape analysis data
 from each organism described in the landscape analysis directory (produced from running landscape_analysis.cfg through avida analyze mode).

Expected output:

"""

def _encode_phenotype(organism_x_environment, encoding):
    """
    Given org X environment dictionary and an encoding scheme (specified in settings file),
     return the encoded phenotype.
    """
    phenotype = []
    for i in range(0, len(encoding)):
        trait = None
        env = encoding[i]["env"]
        task = encoding[i]["task"]
        trait = int(int(organism_x_environment[env][task]) != 0)
        phenotype.append(trait)
    return phenotype


def main():
    """
    main script functionality
    """
    settings = None
    # Load settings from settings file
    with open("param/mutational_landscape_settings.json", "r") as fp:
        settings = json.load(fp)
    # Pull out general locations of interest
    landscape_src = settings["landscape_analysis_dir"]
    dump = settings["landscape_characterization_dest_dir"]
    # Pull out other relevant things
    envs = settings["mutant_characterization"]["environments"]
    # Grab list of orgs in landscape src directory (each dir reps a single organism's landscape)
    orgs = [o for o in os.listdir(landscape_src)]
    overview_content = "org,phenotype,1steps_viable,proportion_viable,1steps_different,proportion_different\n"
    detailed_content = "org,phenotype,mutant,mutant_phenotype,mutant_different,mutant_viability\n"
    mkdir_p(dump)
    for org in orgs:
        # Below are things we want to know about the organism
        original_length = None
        original_phenotype = None
        n1step_viable = 0
        n1step_different = 0
        # Grab each of this organism's mutants
        org_dir = os.path.join(landscape_src, org)
        mutants = [m for m in os.listdir(org_dir) if not m == "original"]
        # Characterize original organism
        # Build phenotype X environment dictionary for the original organism
        original_x_env = {}
        for env in envs:
            env_orig_loc = os.path.join(org_dir, "original", env, "mutant.dat")
            with open(env_orig_loc, "r") as fp:
                orgs = detail_file_extract(fp)
            original_x_env[env] = orgs[0] # There will only by one mutant per mutant.dat
        original_length = original_x_env[envs[0]]["Genome Length"]
        original_phenotype = "".join(map(str, _encode_phenotype(original_x_env, settings["mutant_characterization"]["phenotype_encoding"])))
        # Characterize mutants
        for mutant in mutants:
            mut_dir = os.path.join(org_dir, mutant)
            # Build phenotype X environment dictionary for this mutant
            phen_x_env = {}
            for env in envs:
                env_mut_loc = os.path.join(mut_dir, env, "mutant.dat")
                with open(env_mut_loc, "r") as fp:
                    orgs = detail_file_extract(fp)
                phen_x_env[env] = orgs[0] # There will only by one mutant per mutant.dat
            # Is the mutant viable in all environments?
            viable = not ("0" in [phen_x_env[e]["Is Viable (0/1)"] for e in phen_x_env])
            # Is the mutant different from the original?
            mut_phenotype = "".join(map(str, _encode_phenotype(phen_x_env, settings["mutant_characterization"]["phenotype_encoding"])))
            different = mut_phenotype != original_phenotype
            if viable: n1step_viable += 1
            if different: n1step_different += 1
            # Update detailed csv with this mutant's info
            detailed_content += "%s,%s,%s,%s,%s,%s\n" % (org, original_phenotype, mutant, mut_phenotype, different, viable)
        # Organism's and its mutants' characterizations complete
        prop_viable = n1step_viable / float(len(mutants))
        prop_different = n1step_different / float(len(mutants))
        overview_content += "%s,%s,%d,%f,%d,%f\n" % (org, original_phenotype, n1step_viable, prop_viable, n1step_different, prop_different)
        with open(os.path.join(dump, "mlandscape_details.csv"), "a") as fp:
            fp.write(detailed_content)
            detailed_content = ""
    # Write out overview content
    with open(os.path.join(dump, "mlandscape_overview.csv"), "w") as fp:
        fp.write(overview_content)


if __name__ == "__main__":
    main()
