"""Setup configuration for warehouse capacity planner backend."""
from setuptools import setup, find_packages

setup(
    name='warehouse-capacity-planner',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask>=3.0.0',
        'flask-sqlalchemy>=3.1.1',
        'flask-migrate>=4.0.5',
        'flask-restx>=1.3.0',
        'flask-cors>=4.0.0',
        'flask-caching>=2.1.0',
        'pandas>=2.3.3',
        'openpyxl>=3.1.5',
        'psycopg2-binary>=2.9.10',
        'marshmallow>=3.20.1',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'pytest-flask>=1.2.0',
            'pytest-mock>=3.11.0',
            'faker>=19.0.0',
        ],
    },
    python_requires='>=3.11',
)
