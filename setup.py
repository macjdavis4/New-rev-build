"""
Setup configuration for Revenue Builder.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text() if readme_file.exists() else ''

setup(
    name='revenue-builder',
    version='1.0.0',
    description='Comprehensive ML-Powered Revenue Forecasting System',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Revenue Builder Team',
    author_email='info@revenue-builder.com',
    url='https://github.com/yourusername/revenue-builder',
    packages=find_packages(),
    install_requires=[
        'pandas>=2.0.0',
        'numpy>=1.24.0',
        'scikit-learn>=1.3.0',
        'statsmodels>=0.14.0',
        'prophet>=1.1.5',
        'xgboost>=2.0.0',
        'tensorflow>=2.13.0',
        'lifelines>=0.27.0',
        'scipy>=1.11.0',
        'openpyxl>=3.1.0',
        'sqlalchemy>=2.0.0',
        'matplotlib>=3.7.0',
        'seaborn>=0.12.0',
        'flask>=2.3.0',
        'flask-cors>=4.0.0',
        'click>=8.1.0',
        'pyyaml>=6.0',
        'shap>=0.42.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.4.0',
        ],
        'docs': [
            'sphinx>=7.0.0',
            'sphinx-rtd-theme>=1.3.0',
        ],
        'notebooks': [
            'jupyter>=1.0.0',
            'ipywidgets>=8.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'revenue-builder=revenue_builder.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Office/Business :: Financial',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.8',
    include_package_data=True,
    zip_safe=False,
)
