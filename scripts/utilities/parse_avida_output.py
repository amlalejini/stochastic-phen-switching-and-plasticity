#!/usr/bin/python2

"""
Contains a collection of functions to extract various things from Avida-related files.
"""

def detail_file_extract(detail_fp):
    """
    Given file pointer to detail file, extract information into form below:
    return [{"detail":value, "detail":value, ...}, ...]
    """
    ######################
    # Step 1) Build Legend
    ###
    # Travel to the legend.
    for line in detail_fp:
        if line == "# Legend:\n": break
    # Consume the legend.
    details = []
    for line in detail_fp:
        if line == "\n": break
        details.append(line.split(":")[-1].strip())
    ######################
    # Step 2) Consume Organisms
    ###
    orgs = {}
    org_cnt = 0
    for line in detail_fp:
        org_dets = line.strip().split(" ")
        org = {details[i]:org_dets[i] for i in range(0, len(org_dets))}
        org_id = -1
        if "Genotype ID" in org:
            org_id = org["Genotype ID"]
        else:
            org_id = org_cnt
        orgs[org_id] = org
        org_cnt += 1
    return orgs

def inst_list_extract(inst_list_fp):
    """
    Given a file pointer to an instruciton list config file, return list of defined instructions.
    """
    return list(set([line.split(" ")[1].strip() for line in inst_list_fp if line[0:5] == "INST "]))

def genome_from_genfile(gen_fp):
    """
    Given a file pointer to a .gen (from avida analyze mode), return the genome as a list of instructions.
    """
    return [line.strip() for line in gen_fp if (line.strip() != "") and (not "#" in line)]
