from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="telegrampy",
    version="0.1.0",
    author="TelegramPy Team",
    author_email="info@telegrampy.dev",
    description="A modern, asynchronous Python framework for building Telegram bots",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/telegrampy",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/telegrampy/issues",
        "Documentation": "https://telegrampy.readthedocs.io/",
        "Source Code": "https://github.com/yourusername/telegrampy",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "telegrampy=telegrampy.cli:main",
        ],
    },
    include_package_data=True,
    keywords="telegram bot api async framework",
) 