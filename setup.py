# ============================================================
#  setup.py — RamKleener v2.0
#  pip-installable package configuration
# ============================================================

from setuptools import setup, find_packages
from pathlib import Path

# Safely read README for long description (prevents crash if file is missing)
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else "RamKleener v2.0"

setup(
    name="ramkleener",
    version="2.0.0",
    author="Pushkar",
    description="Scans system processes, filters using a safe tiered model, and terminates known memory-heavy background tasks with user confirmation — all from the terminal.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pushkarthisside/RamKleener",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "psutil>=5.9.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            # FIX: Spelled 'ramkleener' correctly in the module path!
            "ramkleener=ramkleener.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
)