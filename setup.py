from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="MaiConverter",
    description="Parse and convert Maimai chart formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="donmai",
    url="https://github.com/donmai-me/MaiConverter",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Other Audience",
        "Topic :: Games/Entertainment :: Arcade",
    ],
    packages=[
        "maiconverter",
        "maiconverter.event",
        "maiconverter.maicrypt",
        "maiconverter.maima2",
        "maiconverter.maisxt",
        "maiconverter.simai",
        "maiconverter.converter",
        "maiconverter.tool",
    ],
    package_data={"": ["*.lark"]},
    entry_points={
        "console_scripts": ["maiconverter=maiconverter.cli:main"],
    },
    python_requires="~=3.8",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=["pycryptodome~=3.9", "lark-parser~=0.11"],
)
