import re
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version = re.search(
    r'(app_ver     = "(\d.\d.\d)")',
    open("linuxdir2html/linuxdir2html.py").read(),
    re.M
).group(2)

setuptools.setup(
    name="linuxdir2html", # Replace with your own username
    version=version,
    author="Ali Homafar",
    author_email="home.isfar@gmail.com",
    description="HTML directory listing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/homeisfar/LinuxDir2HTML",
    packages=setuptools.find_packages(),
    package_data={
    "linuxdir2html": ["template.html"]
    },
    entry_points={
        "console_scripts": ["linuxdir2html = linuxdir2html.linuxdir2html:main"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
