"""
Minimal setup.py file.
"""
import setuptools

setuptools.setup(
    ext_modules=[
        setuptools.Extension(
            name='venv',
            sources=[]
        )
    ]
)

