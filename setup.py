# ============================================================
#  setup.py — RamKleener Package Configuration
#  Makes the tool pip-installable and adds `ramkleener` CLI command.
# ============================================================

from setuptools import setup, find_packages

setup(
    name="ramkleener",
    version="0.1.0",
    description="A safe Python CLI tool for killing memory-bloating background processes.",
    author="Pushkar",
    python_requires=">=3.9",
    packages=find_packages(),
    install_requires=[
        "psutil>=5.9.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ramkleener=ramkleener.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)