from datetime import datetime
from typing import Any

import arrow
from util.helpers import (
    get_datediff_in_years,
    get_reference_id_from_resource,
    get_resource_sublist,
    nested_get,
)
from util.runner import BaseRunner
from util.static import ADVANCED_ILLNESS_SET


class CMS165v11Runner(BaseRunner):
    """
    CMS165v11 - Controlling High Blood Pressure

    Reference: https://ecqi.healthit.gov/ecqm/ec/2023/cms165v11

    Each function docstring will specify additional exceptions + cases to focus on for the purpose of this lab.
    """

    def __init__(
        self,
        start_period: datetime,
        end_period: datetime,
        patient_list: list[dict[str, Any]],
        condition_list: list[dict[str, Any]],
        observation_list: list[dict[str, Any]],
    ):
        super().__init__(start_period, end_period)
        self.patient_list = patient_list
        self.condition_list = condition_list
        self.observation_list = observation_list

    def initial_population(self) -> set[str]:
        """
        Criteria:
        - Patient age is between 18.0 and 85.0 at the end period
        - Patient has a Condition with a diagnosis of essential hypertension
            - SNOMED Code: 59621000 (display name: "Hypertension")
            - For simplicity, assume the datetime on the Condition is the same as
              the datetime of the associated Encounter.
        """
        # Implement code for the calculating the Initial Population here.
        # FIXME
        ...

    def denominator(self) -> set[str]:
        """
        Equals Initial Population
        """
        return self.initial_population()

    def denominator_exclusions(self) -> set[str] | None:
        """
        Criteria:
        - Patient is in the denominator
        - Patient has an age between (66, 80) relative to the end of the measurement period and has a Condition in the ADVANCED_ILLNESS_SET
            - ADVANCED_ILLNESS_SET contains the exact `display` strings to match on.
        - NOTE: For simplicity, check only for the above criteria
        """
        # Implement code for the calculating the Denominator Exclusions here.
        # FIXME
        ...

    def numerator(self) -> set[str]:
        """
        Criteria:
        - Patient is in the denominator
        - Patient's most recent blood pressure within the measurement period
          is has a Systolic component value <= 140 and Diastolic component value <= 90
            - To get the latest measurement, expect the `effectiveDateTime` field
        """
        # Implement code for the calculating the Numerator here.
        # FIXME
        ...

    def numerator_exclusions(self) -> set[str] | None:
        """
        N/A
        """
        return None

    def denominator_exceptions(self) -> set[str] | None:
        """
        None
        """
        return None
