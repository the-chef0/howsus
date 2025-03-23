import constants as c
from repo_handler import RepoHandler

import ast
import io
import json
import os
import subprocess

import networkx as nx

class CodeMeter:

    def __init__(self, handler: RepoHandler, py_file_dir: str):
        if py_file_dir is not None:
            self._py_file_path = f"{handler.get_working_dir()}/{handler.get_repo_name()}/{py_file_dir}"
        else:
            self._py_file_path = f"{handler.get_working_dir()}/{handler.get_repo_name()}"

        self._handler = handler

    def _is_abstract_class(self, node: ast.Module):
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "ABC":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "ABC":
                return True
        return False
    
    def _get_class_counts(self, py_file: str) -> (int, int):
        with open(py_file, "r", encoding="utf8") as f:
            tree = ast.parse(f.read(), filename=py_file)

        concrete_classes = 0
        abstract_classes = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if self._is_abstract_class(node):
                    abstract_classes += 1
                else:
                    concrete_classes += 1

        return (concrete_classes, abstract_classes)                

    def get_abstractness(self) -> float:
        concrete_classes = 0
        abstract_classes = 0

        for root, _, files in os.walk(self._py_file_path):
            for file in files:
                if file.endswith(".py"):
                    curr_py_file = os.path.join(root, file)
                    curr_concrete, curr_abstract = self._get_class_counts(curr_py_file)
                    concrete_classes += curr_concrete
                    abstract_classes += curr_abstract

        return abstract_classes / concrete_classes

    def get_instability(self) -> float:
        pydeps_subproc = subprocess.run(
            ["pydeps", "--show-deps", "--no-output", self._py_file_path],
            capture_output=True,
            text=True,
            check=True
        )

        result = json.loads(pydeps_subproc.stdout)
        instabilities_sum = 0

        for _, module_metrics in result.items():
            afferent_coupling = 0
            efferent_coupling = 0

            if c.IMPORTED_BY in module_metrics.keys():
                afferent_coupling = len(module_metrics[c.IMPORTED_BY])

            if c.IMPORTS in module_metrics.keys():
                efferent_coupling = len(module_metrics[c.IMPORTS])

            if not ((afferent_coupling == 0) and (efferent_coupling == 0)):
                instabilities_sum += efferent_coupling / (afferent_coupling + efferent_coupling)

        if not len(result.keys()) == 0:
            return instabilities_sum / len(result.keys())
        else:
            return 0
