from setuptools import setup

setup(name="PyGamon",
      version="0.0.1-Alpha",
      description="A Pokémon Fan game",
      author="IDarKay",
      packages=["relink", "tests"],
      install_requires=["requests"],
      extras_require={
            "dev": ["requests-mock"],
      }
      )