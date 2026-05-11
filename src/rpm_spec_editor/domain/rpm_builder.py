import subprocess


class RPMBuildResult:
    def __init__(self, success, stdout, stderr):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr


class RPMBuilder:
    def build(self, spec_path):
        try:
            result = subprocess.run(
                [
                    "rpmbuild",
                    "-ba",
                    str(spec_path)
                ],
                capture_output=True,
                text=True
            )
            success = (result.returncode == 0)

            return RPMBuildResult(success, result.stdout, result.stderr)

        except FileNotFoundError:
            return RPMBuildResult(False, "", "rpmbuild не найден")