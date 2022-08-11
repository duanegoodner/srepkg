"""
Minimal setup.py file.
"""
import setuptools

# try:
#     from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
#
#
#     class bdist_wheel(_bdist_wheel):
#         def finalize_options(self):
#             _bdist_wheel.finalize_options(self)
#             self.root_is_pure = False
# except ImportError:
#     bdist_wheel = None
#
# setuptools.setup(cmdclass={'bdist_wheel': bdist_wheel})

setuptools.setup(
    ext_modules=[
        setuptools.Extension(
            name='venv',
            sources=[]
        )
    ]
)


# setuptools.setup()
