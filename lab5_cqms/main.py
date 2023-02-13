import json
import pathlib

import arrow
from deliverables import CMS125v11Runner, CMS147v11Runner, CMS165v11Runner

# NOTE: Set this to True to use the test_subset locally.
#       Set this to False to run on the full data.
#       NOTE that this should be False when submitting to Gradescope!

USE_TEST_SUBSET = False


DATA_DIR = f"{pathlib.Path(__file__).parent.parent.absolute()}/data"
OUTPUT_DIR = f"{pathlib.Path(__file__).parent.absolute()}/output"

if USE_TEST_SUBSET:
    TEST_SUBSET_DIR = f"{pathlib.Path(__file__).parent.parent.absolute()}/test_subset"
    DATA_DIR = f"{TEST_SUBSET_DIR}/data"
    OUTPUT_DIR = f"{TEST_SUBSET_DIR}/output"

MEASUREMENT_PERIOD_START_DATETIME = arrow.get(
    "2018-01-01"
).datetime  # 2018-01-01 00:00:00+00:00
MEASUREMENT_PERIOD_END_DATETIME = arrow.get(
    "2022-01-01"
).datetime  # 2022-01-01 00:00:00+00:00


if __name__ == "__main__":
    # Local helper function
    def load_ndjson_file(filepath: str) -> list[dict]:
        with open(filepath, "r") as file:
            return [dict(json.loads(line)) for line in file]

    # Initiate lists
    patient_list = load_ndjson_file(f"{DATA_DIR}/Patient.ndjson")
    observation_list = load_ndjson_file(f"{DATA_DIR}/Observation.ndjson")
    condition_list = load_ndjson_file(f"{DATA_DIR}/Condition.ndjson")
    encounter_list = load_ndjson_file(f"{DATA_DIR}/Encounter.ndjson")
    immunization_list = load_ndjson_file(f"{DATA_DIR}/Immunization.ndjson")
    procedure_list = load_ndjson_file(f"{DATA_DIR}/Procedure.ndjson")

    # Run each eCQM
    runners = [
        CMS125v11Runner(
            MEASUREMENT_PERIOD_START_DATETIME,
            MEASUREMENT_PERIOD_END_DATETIME,
            patient_list=patient_list,
            encounter_list=encounter_list,
            procedure_list=procedure_list,
        ),
        CMS147v11Runner(
            MEASUREMENT_PERIOD_START_DATETIME,
            MEASUREMENT_PERIOD_END_DATETIME,
            patient_list=patient_list,
            encounter_list=encounter_list,
            immunization_list=immunization_list,
        ),
        CMS165v11Runner(
            MEASUREMENT_PERIOD_START_DATETIME,
            MEASUREMENT_PERIOD_END_DATETIME,
            patient_list=patient_list,
            condition_list=condition_list,
            observation_list=observation_list,
        ),
    ]
    for runner in runners:
        result_dict = runner.run_all(print_counts=True, save_to_dir=OUTPUT_DIR)
