import os
import pytest


@pytest.mark.parametrize(
    "farm",
    [
        "test",
        "montpellier_clay",
        "montpellier_sand",
        "montpellier_clay_bean",
        "montpellier_sand_bean",
    ],
)
def test_cleanup(farm):
    """
    Not actually a test, removes created temp farms created for tests
    """
    # Clean folder
    files = ["_actions.yaml", "_init.yaml", "_score.yaml"]
    files_to_remove = [f"{farm}{file}" for file in files]
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
