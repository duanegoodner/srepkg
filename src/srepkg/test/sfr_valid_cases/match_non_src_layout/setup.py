import setuptools

setuptools.setup(
    name='testproj',
    packages=setuptools.find_packages(),
    install_requires=['numpy >= 1.22', 'pandas'],
    entry_points={
        'console_scripts': [
            'my_project = testproj.app:run',
            'my_test = testproj.test:simple_test'
        ]
    }
)
