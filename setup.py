from pathlib import Path
from shutil import copyfile

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py


class build_py(_build_py):
    """Bundle the checked-in canonical schema in non-editable distributions."""

    def _schema_output(self) -> Path:
        return Path(self.build_lib) / "semiconductor_ai_engineering_toolkit" / "run_record_v0_1.schema.json"

    def run(self) -> None:
        super().run()
        source = Path(__file__).resolve().parent / "schema" / "run_record_v0_1.schema.json"
        target = self._schema_output()
        target.parent.mkdir(parents=True, exist_ok=True)
        copyfile(source, target)

    def get_outputs(self, include_bytecode: bool = True):
        outputs = list(super().get_outputs(include_bytecode=include_bytecode))
        schema_output = str(self._schema_output())
        if schema_output not in outputs:
            outputs.append(schema_output)
        return outputs


setup(cmdclass={"build_py": build_py})
