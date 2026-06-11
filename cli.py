# tidyprot/cli.py
import argparse

def get_args(mode: str = "query"):
    parser = argparse.ArgumentParser(description="tidyprot workflow")
    
    if mode == "query":
        parser.add_argument("--source", required=True, choices=["NCBI", "UniProtKB"])
        parser.add_argument("--query", required=True, type=str)
    
    elif mode == "debug":
        parser.add_argument("--source", choices=["NCBI", "UniProtKB"], default=None)
        parser.add_argument("--query", type=str, default=None)
    
    return parser.parse_args()

