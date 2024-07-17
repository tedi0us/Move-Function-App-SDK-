from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="azure-resource-mover",
    version="0.1.0",
    author="Tyco Sedler",
    author_email="tyco@redwoodmaterials.com",
    description="A CLI tool for moving Azure resources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Move-Function-App-SDK-",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "msal",
        "requests",
        "python-dotenv",
        # Add any other dependencies your project needs
    ],
    entry_points={
        "console_scripts": [
            "armover=azure_resource_mover.main:run",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)