#!/usr/bin/env python3

import argparse
import pickle
import re
import sys
import time
import urllib.parse
import urllib.request
from io import StringIO
from pathlib import Path

import pandas as pd


BASE_FIELDS = [
    "accession",
    "xref_ensembl",
    "id",
    "reviewed",
    "protein_name",
    "gene_names",
    "length",
    "organism_name",
    "organism_id",
    "xref_pfam",
    "xref_supfam",
]

FEATURE_FIELDS = [
    "ft_var_seq",
    "ft_variant",
    "ft_non_cons",
    "ft_non_std",
    "ft_non_ter",
    "ft_conflict",
    "ft_unsure",
    "ft_act_site",
    "ft_binding",
    "ft_dna_bind",
    "ft_site",
    "ft_mutagen",
    "ft_intramem",
    "ft_topo_dom",
    "ft_transmem",
    "ft_chain",
    "ft_crosslnk",
    "ft_disulfid",
    "ft_carbohyd",
    "ft_init_met",
    "ft_lipid",
    "ft_mod_res",
    "ft_peptide",
    "ft_propep",
    "ft_signal",
    "ft_transit",
    "ft_strand",
    "ft_helix",
    "ft_turn",
    "ft_coiled",
    "ft_compbias",
    "ft_domain",
    "ft_motif",
    "ft_region",
    "ft_repeat",
    "ft_zn_fing",
]

FEATURE_COLUMNS = [
    "alternative_sequence",
    "natural_variant",
    "non_adjacent_residues",
    "non_standard_residue",
    "non_terminal_residue",
    "sequence_conflict",
    "sequence_uncertainty",
    "active_site",
    "binding_site",
    "dna_binding",
    "site",
    "mutagenesis",
    "intramembrane",
    "topological_domain",
    "transmembrane",
    "chain",
    "cross_link",
    "disulfide_bond",
    "glycosylation",
    "initiator_methionine",
    "lipidation",
    "modified_residue",
    "peptide",
    "propeptide",
    "signal_peptide",
    "transit_peptide",
    "beta_strand",
    "helix",
    "turn",
    "coiled_coil",
    "compositional_bias",
    "domain_ft",
    "motif",
    "region",
    "repeat",
    "zinc_finger",
]


def clean_column_names(df):
    """Convert UniProt column names to lower snake_case."""
    df = df.copy()
    df.columns = (
        df.columns
        .str.lower()
        .str.replace(r"[^a-z0-9_]+", "_", regex=True)
        .str.strip("_")
    )
    return df


def clean_anno_value(value):
    """Remove spurious quotes, semicolons and whitespace from parsed annotation values."""
    if pd.isna(value):
        return ""

    value = str(value).strip()

    # Remove repeated outer quotes, semicolons and whitespace.
    value = value.strip()
    value = value.strip(" \t\r\n;\"'")

    # UniProt feature parsing can leave doubled quotes such as:
    # """Phosphoserine""; "
    while value.startswith('"') or value.startswith("'"):
        value = value[1:].strip()
    while value.endswith('"') or value.endswith("'") or value.endswith(";"):
        value = value[:-1].strip()

    value = value.replace('""', '"')
    value = value.strip(" \t\r\n;\"'")

    return value


def clean_anno_frame(df):
    """Clean all parsed annotation text columns."""
    df = df.copy()

    for col in df.columns:
        if col not in {"entry", "origin"}:
            df[col] = df[col].map(clean_anno_value)

    return df


def build_uniprot_url(query, add_fields=None):
    """Build a UniProtKB stream API URL."""
    fields = BASE_FIELDS.copy()

    if add_fields:
        for field in add_fields.split(","):
            field = field.strip()
            if field and field not in fields and field not in FEATURE_FIELDS:
                fields.append(field)

    fields = list(dict.fromkeys(fields + FEATURE_FIELDS))
    fields_query = ",".join(fields)
    encoded_query = urllib.parse.quote(query, safe="")

    return (
        "https://rest.uniprot.org/uniprotkb/stream"
        f"?query={encoded_query}"
        "&format=tsv"
        f"&fields={fields_query}"
    )


def fetch_uniprot_tsv(query, add_fields=None):
    """Fetch UniProtKB data as a dataframe."""
    url = build_uniprot_url(query, add_fields)

    with urllib.request.urlopen(url) as response:
        text = response.read().decode("utf-8")

    if not text.strip():
        return pd.DataFrame()

    return clean_column_names(pd.read_csv(StringIO(text), sep="\t"))


def infer_feature_prefix(series):
    """
    Infer the repeated UniProt feature prefix used in a feature column.

    Example feature string:
      MOD_RES 114; /note="Phosphoserine"; /evidence="ECO:..."
    """
    non_empty = series.replace("", pd.NA).dropna()

    if non_empty.empty:
        return None

    prefixes = (
        non_empty
        .astype(str)
        .str.replace(r" .+$", "", regex=True)
        .dropna()
        .unique()
    )

    prefixes = [prefix for prefix in prefixes if prefix]

    if not prefixes:
        return None

    return prefixes[0]


def parse_feature_column(df, feature_col):
    """Parse one UniProt feature column into a tidy annotation dataframe."""
    if feature_col not in df.columns:
        return pd.DataFrame()

    prefix = infer_feature_prefix(df[feature_col])

    if not prefix:
        return pd.DataFrame()

    parsed = (
        df[["entry", feature_col]]
        .rename(columns={feature_col: "raw_feature"})
        .dropna(subset=["raw_feature"])
        .copy()
    )

    parsed["raw_feature"] = parsed["raw_feature"].astype(str)
    parsed = parsed[parsed["raw_feature"].str.strip() != ""]

    if parsed.empty:
        return pd.DataFrame()

    parsed["raw_feature"] = parsed["raw_feature"].str.split(prefix)
    parsed = parsed.explode("raw_feature", ignore_index=True)
    parsed = parsed[parsed["raw_feature"].notna()]
    parsed = parsed[parsed["raw_feature"].str.strip() != ""]

    if parsed.empty:
        return pd.DataFrame()

    parsed["pos"] = (
        parsed["raw_feature"]
        .str.replace(r";.*$", "", regex=True)
        .str.replace(" ", "", regex=False)
        .str.replace(r"\.\.", "-", regex=True)
        .map(clean_anno_value)
    )

    parsed["raw_feature"] = parsed["raw_feature"].str.split("/")
    parsed = parsed.explode("raw_feature", ignore_index=True)

    parsed = parsed[parsed["raw_feature"].notna()]
    parsed = parsed[parsed["raw_feature"].str.strip() != ""]
    parsed = parsed[parsed["raw_feature"].str.contains("=", na=False)]

    if parsed.empty:
        return pd.DataFrame()

    split_values = parsed["raw_feature"].str.split("=", n=1, expand=True)

    parsed["data_type"] = split_values[0].str.strip()
    parsed["entry_data"] = split_values[1].map(clean_anno_value)

    parsed = (
        parsed[["entry", "pos", "data_type", "entry_data"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    pivot = (
        parsed
        .groupby(["entry", "pos", "data_type"], as_index=False)
        .agg(entry_data=("entry_data", lambda values: ";".join(values)))
        .pivot_table(
            index=["entry", "pos"],
            columns="data_type",
            values="entry_data",
            aggfunc="first",
        )
        .reset_index()
        .fillna("")
    )

    pivot.columns.name = None
    pivot["origin"] = feature_col

    return clean_anno_frame(pivot)


def parse_annotations(df):
    """Parse all UniProt sequence annotation columns."""
    anno = {}

    for feature_col in FEATURE_COLUMNS:
        parsed = parse_feature_column(df, feature_col)

        if not parsed.empty:
            anno[feature_col] = parsed

    return anno


def fetch_uniprot(query, add_fields=None):
    """
    Fetch UniProtKB entries and return a tidy dictionary.

    Returned object:
      {
        "uptable": entry-level dataframe,
        "anno": {
          feature_name: tidy feature annotation dataframe
        }
      }
    """
    df = fetch_uniprot_tsv(query, add_fields)

    if df.empty:
        return {"uptable": pd.DataFrame(), "anno": {}}

    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = ""
        else:
            df[col] = df[col].fillna("")

    anno = parse_annotations(df)
    uptable = df.drop(columns=FEATURE_COLUMNS, errors="ignore")

    return {"uptable": uptable, "anno": anno}


def read_accessions(path):
    """Read one accession per line."""
    with open(path) as handle:
        return [line.strip() for line in handle if line.strip()]


def make_accession_query(accessions):
    """Build a UniProt accession query."""
    return " OR ".join(f"accession:{accession}" for accession in accessions)


def fetch_batches(accessions, batch_size, add_fields=None, verbose=False):
    """Fetch UniProtKB entries in accession batches."""
    all_main = []
    anno_collected = {}

    total = len(accessions)

    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        batch = accessions[start:end]

        if verbose:
            print(f"Fetching accessions {start + 1}-{end} of {total}", file=sys.stderr)

        data = fetch_uniprot(make_accession_query(batch), add_fields)

        if not data["uptable"].empty:
            all_main.append(data["uptable"])

        for feature, feature_df in data["anno"].items():
            if not feature_df.empty:
                anno_collected.setdefault(feature, []).append(feature_df)

    if all_main:
        uptable = pd.concat(all_main, ignore_index=True).drop_duplicates()
    else:
        uptable = pd.DataFrame()

    anno = {}

    for feature, frames in anno_collected.items():
        if frames:
            anno[feature] = pd.concat(frames, ignore_index=True).drop_duplicates()

    return {"uptable": uptable, "anno": anno}


def save_tsv_outputs(data, outdir):
    """Save the main table and annotation tables as TSV files."""
    saved = []

    main_file = outdir / "main_uptable.tsv"
    data["uptable"].to_csv(main_file, sep="\t", index=False)
    saved.append(main_file)

    for feature, feature_df in sorted(data["anno"].items()):
        if feature_df.empty:
            continue

        anno_file = outdir / f"anno_{feature}_uptable.tsv"
        feature_df.to_csv(anno_file, sep="\t", index=False)
        saved.append(anno_file)

    return saved


def save_pickle_output(data, outdir):
    """Save the tidy UniProt dictionary as a pickle."""
    pickle_file = outdir / "upData.pkl"

    with open(pickle_file, "wb") as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return pickle_file


def count_tsv_rows(path):
    """Count data rows in a TSV file."""
    if not path.exists():
        return 0

    return pd.read_csv(path, sep="\t", usecols=[0]).shape[0]


def print_saved_files(paths):
    """Print a short summary of saved files."""
    print("Saved files:")

    for path in paths:
        if path.suffix == ".tsv":
            print(f"  {path}  ({count_tsv_rows(path)} rows)")
        else:
            print(f"  {path}")


def parse_args():
    examples = """
examples:
  # 1. Ad-hoc query
  %(prog)s -q "organism_id:9606 AND reviewed:true"

  # 2. Batch download from a list of accessions
  %(prog)s -i my_ids.txt

  # 3. Add extra UniProt columns and print progress
  %(prog)s -i ids.txt -a "cc_function,cc_subcellular_location" -v

  # 4. Save as pickle only
  %(prog)s -q "organism_id:9606" --output-type pickle
"""

    parser = argparse.ArgumentParser(
        prog="uniprot_query",
        description=(
            "Fetch UniProtKB entries via the UniProt REST API and return a tidy "
            "dictionary with an entry-level table plus parsed sequence annotations."
        ),
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    input_group = parser.add_mutually_exclusive_group(required=True)

    input_group.add_argument(
        "-q",
        "--query",
        metavar="QUERY",
        help='UniProt query, for example: "organism_id:9606 AND reviewed:true"',
    )

    input_group.add_argument(
        "-i",
        "--idfile",
        metavar="FILE",
        help="Text file with one accession per line",
    )

    parser.add_argument(
        "-b",
        "--batch-size",
        type=int,
        default=50,
        help="Number of accessions per request in --idfile mode. Default: 50",
    )

    parser.add_argument(
        "-o",
        "--outdir",
        default="results",
        help="Output folder. Created if missing. Default: results",
    )

    parser.add_argument(
        "-a",
        "--add-fields",
        metavar="F1,F2,...",
        help="Extra UniProt return columns, comma separated",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print progress to stderr",
    )

    parser.add_argument(
        "--output-type",
        choices=["tsv", "pickle", "both"],
        default="both",
        help="Output format: tsv, pickle, or both. Default: both",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    start_time = time.time()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if args.query:
        query = args.query.strip()

        if not query:
            sys.exit("Empty query")

        data = fetch_uniprot(query, args.add_fields)

    else:
        accessions = read_accessions(args.idfile)

        if not accessions:
            sys.exit("No IDs found in idfile")

        data = fetch_batches(
            accessions=accessions,
            batch_size=args.batch_size,
            add_fields=args.add_fields,
            verbose=args.verbose,
        )

    saved_files = []

    if args.output_type in {"tsv", "both"}:
        saved_files.extend(save_tsv_outputs(data, outdir))

    if args.output_type in {"pickle", "both"}:
        saved_files.append(save_pickle_output(data, outdir))

    print_saved_files(saved_files)

    elapsed = time.time() - start_time
    print(f"\nDone in {elapsed:.2f} s.")


if __name__ == "__main__":
    main()



