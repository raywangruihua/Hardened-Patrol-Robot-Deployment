from setuptools import setup, find_packages
import os
from glob import glob

package_name = "secure_patrol"

setup(
    name=package_name,
    version="0.0.1",
    packages=find_packages(),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (
            os.path.join("share", package_name, "launch"), 
            glob(os.path.join("launch", "*launch.py")) 
            + glob(os.path.join("launch", "*.launch.xml"))
        ),
    ],
    install_requires=["setuptools"],
    zip_safe=False,
    maintainer="Ray Wang Rui Hua",
    maintainer_email="raywangruihua@gmail.com",
    description="Privacy filter implementation of Nav2 based navigation with rtabmap-based localization. For demonstration and reference only, not intended for actual use in deployed systems.",
    license="Apache 2.0",
    entry_points={
        "console_scripts": [
            "voice_node = secure_patrol.nodes.voice_node:main",
            "screen_node = secure_patrol.nodes.screen_node:main",
        ],
    }
)