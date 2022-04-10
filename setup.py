from setuptools import setup
from Cython.Build import cythonize

setup(
    name = 'Morris Game Tournament',
    ext_modules = cythonize(
        "Tournament/TournamentTrainer.pyx",
        compiler_directives = {
            'language_level': 3,
            'boundscheck': False,
            'wraparound': False,
            'c_api_binop_methods': True
        }
    )
)