# utils_paths.py

import os

def resolve_path(script_dir: str, use_sample: bool, *parts: str) -> str:
    sample = "../sample" if use_sample else "../"
    return os.path.abspath(os.path.join(script_dir, sample, *parts))
