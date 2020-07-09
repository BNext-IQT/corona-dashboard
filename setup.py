from setuptools import setup, find_packages

setup(
    name='corona-dashboard',
    version='0.0.1',
    description='Dashboards to analyze the spread of the novel coronavirus.',
    long_description=open("README.rst").read(),
    keywords='machine_learning artificial_intelligence dashboard forecasting',
    author='JJ Ben-Joseph',
    author_email='jbenjoseph@iqt.org',
    python_requires='>=3.8',
    url='https://www.github.com/bnext-iqt/corona-dashboard',
    license='Apache',
    classifiers=[
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Scientific/Engineering :: Visualization',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent'
    ],
    packages=find_packages(),
    install_requires=['dash', 'plotly', 'pandas', 'numpy',
                      'pmdarima', 'fire', 'tqdm'],
    extras_require={
        'full': ['uwsgi', 'sigopt']
    },
    entry_points={
        'console_scripts': [
            'corona-dashboard = corona_dashboard.__main__:main',
        ],
    },
)
