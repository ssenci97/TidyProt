# tidyprot/cli.py
import argparse

UNIPROTKB_RETURN_FIELDS = [
    "accession", "id", "gene_names", "gene_primary", "gene_synonym",
    "gene_oln", "gene_orf", "organism_name", "organism_id", "protein_name",
    "xref_proteomes", "lineage", "lineage_ids", "virus_hosts",
    "cc_alternative_products", "ft_var_seq", "cc_sc_epred", "fragment",
    "encoded_in", "length", "mass", "cc_mass_spectrometry", "ft_variant",
    "ft_non_cons", "ft_non_std", "ft_non_ter", "cc_polymorphism",
    "cc_rna_editing", "sequence", "cc_sequence_caution", "ft_conflict",
    "ft_unsure", "sequence_version", "absorption", "ft_act_site",
    "cc_activity_regulation", "ft_binding", "cc_catalytic_activity",
    "cc_cofactor", "ft_dna_bind", "ec", "cc_function", "kinetics",
    "cc_pathway", "ph_dependence", "redox_potential", "rhea", "ft_site",
    "temp_dependence", "annotation_score", "cc_caution", "comment_count",
    "feature_count", "keywordid", "keyword", "cc_miscellaneous",
    "protein_existence", "reviewed", "tools", "uniparc_id", "cc_interaction",
    "cc_subunit", "cc_developmental_stage", "cc_induction",
    "cc_tissue_specificity", "go_p", "go_c", "go", "go_f", "go_id",
    "cc_allergen", "cc_biotechnology", "cc_disruption_phenotype",
    "cc_disease", "ft_mutagen", "cc_pharmaceutical", "cc_toxic_dose",
    "ft_intramem", "cc_subcellular_location", "ft_topo_dom", "ft_transmem",
    "ft_chain", "ft_crosslnk", "ft_disulfid", "ft_carbohyd", "ft_init_met",
    "ft_lipid", "ft_mod_res", "ft_peptide", "cc_ptm", "ft_propep",
    "ft_signal", "ft_transit", "structure_3d", "ft_strand", "ft_helix",
    "ft_turn", "lit_pubmed_id", "date_created", "date_modified",
    "date_sequence_modified", "version", "ft_coiled", "ft_compbias",
    "cc_domain", "ft_domain", "ft_motif", "protein_families", "ft_region",
    "ft_repeat", "ft_zn_fing", "xref_ccds", "xref_embl", "xref_generif",
    "xref_pir", "xref_refseq", "xref_alphafolddb", "xref_bmrb",
    "xref_emdb", "xref_pcddb", "xref_pdb", "xref_pdbsum", "xref_sasbdb",
    "xref_smr", "xref_biogrid", "xref_corum", "xref_complexportal",
    "xref_dip", "xref_elm", "xref_funcoup", "xref_intact", "xref_mint",
    "xref_ndex", "xref_string", "xref_bindingdb", "xref_chebi",
    "xref_chembl", "xref_drugbank", "xref_drugcentral",
    "xref_guidetopharmacology", "xref_swisslipids", "xref_allergome",
    "xref_card", "xref_cazy", "xref_esther", "xref_imgt_gene-db",
    "xref_merops", "xref_moondb", "xref_moonprot", "xref_peroxibase",
    "xref_rebase", "xref_tcdb", "xref_unilectin", "xref_carbonyldb",
    "xref_depod", "xref_glyconnect", "xref_glycosmos", "xref_glygen",
    "xref_metosite", "xref_phosphositeplus", "xref_swisspalm",
    "xref_unicarbkb", "xref_iptmnet", "xref_alzforum", "xref_biomuta",
    "xref_dmdm", "xref_dbsnp", "xref_ogp", "xref_reproduction-2dpage",
    "xref_cptac", "xref_massive", "xref_pride", "xref_paxdb",
    "xref_peptideatlas", "xref_promex", "xref_proteomicsdb", "xref_pumba",
    "xref_topdownproteomics", "xref_jpost", "xref_abcd",
    "xref_antibodypedia", "xref_cptc", "xref_dnasu", "xref_ycharos",
    "xref_ensembl", "xref_ensemblbacteria", "xref_ensemblfungi",
    "xref_ensemblmetazoa", "xref_ensemblplants", "xref_ensemblprotists",
    "xref_geneid", "xref_gramene", "xref_kegg", "xref_mane-select",
    "xref_patric", "xref_ucsc", "xref_vectorbase", "xref_wbparasite",
    "xref_agr", "xref_arachnoserver", "xref_araport", "xref_cgd",
    "xref_civic", "xref_ctd", "xref_clinpgx", "xref_conoserver",
    "xref_disgenet", "xref_echobase", "xref_flybase", "xref_genecards",
    "xref_genereviews", "xref_hgnc", "xref_hpa", "xref_ic4r",
    "xref_japonicusdb", "xref_legiolist", "xref_leproma", "xref_mgi",
    "xref_mim", "xref_maizegdb", "xref_malacards", "xref_niagads",
    "xref_opentargets", "xref_orphanet", "xref_pombase", "xref_pseudocap",
    "xref_rgd", "xref_sgd", "xref_tair", "xref_tuberculist",
    "xref_veupathdb", "xref_vgnc", "xref_wormbase", "xref_xenbase",
    "xref_zfin", "xref_dictybase", "xref_euhcvdb", "xref_genetree",
    "xref_hogenom", "xref_inparanoid", "xref_oma", "xref_orthodb",
    "xref_pan-go", "xref_phylomedb", "xref_eggnog", "xref_brenda",
    "xref_biocyc", "xref_pathwaycommons", "xref_plantreactome",
    "xref_reactome", "xref_sabio-rk", "xref_signor", "xref_strenda-db",
    "xref_signalink", "xref_unipathway", "xref_agora", "xref_biogrid-orcs",
    "xref_cd-code", "xref_chitars", "xref_evolutionarytrace",
    "xref_genewiki", "xref_genomernai", "xref_orcid", "xref_pgenn",
    "xref_phi-base", "xref_pro", "xref_pharos", "xref_pubtator",
    "xref_rnact", "xref_emind", "xref_abasyatlas", "xref_bgee",
    "xref_cleanex", "xref_collectf", "xref_expressionatlas",
    "xref_antifam", "xref_cdd", "xref_disprot", "xref_funfam",
    "xref_gene3d", "xref_hamap", "xref_ideal", "xref_interpro",
    "xref_ncbifam", "xref_panther", "xref_pirsf", "xref_prints",
    "xref_prosite", "xref_pfam", "xref_sfld", "xref_smart", "xref_supfam",
]

default_fields = ["accession", "id", "protein_name", "gene_names", "organism_name", "organism_id", "length"]

def get_args(mode: str = "query"):
    parser = argparse.ArgumentParser(description="tidyprot workflow")

    if mode == "query":
        parser.add_argument("--source", required=True, choices=["NCBI", "UniProtKB"])
        parser.add_argument("--query", required=True, type=str)
    elif mode == "debug":
        parser.add_argument("--source", choices=["NCBI", "UniProtKB"], default=None)
        parser.add_argument("--query", type=str, default=None)

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--UniProtKB_fields",
        type=str,
        default=",".join(default_fields),
        help="Comma-separated UniProtKB return fields"
    )
    group.add_argument(
        "--NCBI_fields",
        type=str,
        default="gp",
        help="Comma-separated NCBI return fields"
    )

    args = parser.parse_args()

    args.UniProtKB_fields = [f.strip() for f in args.UniProtKB_fields.split(",")]
    args.NCBI_fields = [f.strip() for f in args.NCBI_fields.split(",")]

    if args.source == "UniProtKB" or (mode == "debug" and args.source is None):
        invalid = [f for f in args.UniProtKB_fields if f not in UNIPROTKB_RETURN_FIELDS]
        if invalid:
            parser.error(f"Invalid UniProtKB return fields: {', '.join(invalid)}")

    return args

