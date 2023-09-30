import json
from subprocess import run

import matplotlib
import numpy
import sklearn
import pandas
import scipy


class PythonLibs():

    def __init__(self):
        extra_python_libs_for_generated_code = [matplotlib, numpy, sklearn, pandas, scipy]
        extra_libs = {lib.__name__: lib.__version__ for lib in extra_python_libs_for_generated_code}
        print(extra_libs)

    def get_available_libraries_prompt(self, max_characters=0):
        pass

    def get_available_library_versions_prompt(self, max_characters=0):
        result = run(["pip", "list", "--format", "json"], capture_output=True)
        lib_versions = json.loads(result.stdout)
        print(lib_versions)


if __name__ == "__main__":
    PythonLibs().get_available_libraries_prompt()
