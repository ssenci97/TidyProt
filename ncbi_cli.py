import argparse


def get_args(mode: str = "query"):
    parser = argparse.ArgumentParser(description="tidyprot NCBI workflow")

    if mode == "query":
        parser.add_argument("--query", required=True, type=str)
    elif mode == "debug":
        parser.add_argument("--query", type=str, default=None)

    parser.add_argument(
        "--NCBI_fields",
        type=str,
        default="gp",
        help="Comma-separated NCBI return fields"
    )

    args = parser.parse_args()

    args.NCBI_fields = [f.strip() for f in args.NCBI_fields.split(",")]

    return args


