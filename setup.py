from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read()

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
    python_requires=">=3.7",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=requirements,
    extras_requires={':python_version < "3.8"': ["importlib-metadata"]},
)
