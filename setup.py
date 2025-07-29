from setuptools import setup, find_packages

setup(
    name="bajaj-finserv",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "python-multipart==0.0.6",
        "pydantic==2.5.0",
        "PyPDF2==3.0.1",
    ],
    python_requires=">=3.8",
)
