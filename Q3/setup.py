import setuptools

with open("README.md") as fp:
    long_description = fp.read()

setuptools.setup(
    name="url_shortener",
    version="0.0.1",
    description="URL Shortener",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Typing :: Typed",
    ],
)
