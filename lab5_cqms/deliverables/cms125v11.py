from datetime import datetime
from typing import Any

import arrow
from util.helpers import (
    date_is_within_date_range,
    get_datediff_in_years,
    get_reference_id_from_resource,
    get_resource_sublist,
    nested_get,
)
from util.runner import BaseRunner


class CMS125v11Runner(BaseRunner):
    """
    CMS125v11 - Breast Cancer Screening

    Reference: https://ecqi.healthit.gov/ecqm/ec/2023/cms125v11

    Each function docstring will specify additional exceptions + cases to focus on for the purpose of this lab.
    """

    def __init__(
        self,
        start_period: datetime,
        end_period: datetime,
        patient_list: list[dict[str, Any]],
        encounter_list: list[dict[str, Any]],
        procedure_list: list[dict[str, Any]],
    ):
        """
        Use the provided lists
        """
        super().__init__(start_period, end_period)
        self.patient_list = patient_list
        self.encounter_list = encounter_list
        self.procedure_list = procedure_list

    def initial_population(self) -> set[str]:
        """
        Criteria:
        - Patient's gender is Female
        - Patient's calculated age at end period is between (52, 74)
        - Patient has at least 1 Encounter within the measurement period
        """
        res = set()
        for patient in self.patient_list:
            if patient.get("gender") == "female":
                birthdate = patient.get("birthDate")
                age = get_datediff_in_years(birthdate, self.end_period)
                if 52.0 <= age <= 74.0:
                    pid = patient.get("id")
                    # There are more efficient ways to do this, though this is the simplest
                    encounter_list = get_resource_sublist(self.encounter_list, {pid})

                    if (
                        len(
                            [
                                e
                                for e in encounter_list
                                if date_is_within_date_range(
                                    nested_get(e, "period.start"),
                                    self.start_period,
                                    self.end_period,
                                )
                            ]
                        )
                        > 0
                    ):
                        res.add(pid)
        return res

    def denominator(self) -> set[str]:
        """
        Criteria:
        - Same as the initial_population
        """
        return self.initial_population()

    def denominator_exclusions(self) -> set[str] | None:
        """
        Students Not Required to Implement
        """
        return None

    def numerator(self) -> set[str]:
        """
        Criteria:
        - Patient is in the denominator
        - Patient has at least one completed mammogram (Procedure) whose start date is within
          the date range of October two years prior to the start period year to the end period
            - Mammogram ICD10 Code: 71651007. You can assume all Procedure codings are ICD10 codes,
              and plaintext descriptions are available on the CodableConcept (consider case-sensitivity).
        """
        res = set()
        denom_set = self.denominator()
        # Shift two years earlier and set to october
        earliest_datetime = (
            arrow.get(self.start_period).shift(years=-2).replace(month=10).datetime
        )
        for procedure in self.procedure_list:
            # NOTE: Ok to assume start date is sufficient
            pid = get_reference_id_from_resource(procedure)
            if pid in denom_set:
                # Check within range
                procedure_start = nested_get(procedure, "performedPeriod.start")
                if date_is_within_date_range(
                    procedure_start, earliest_datetime, self.end_period
                ):
                    # Check if completed Mammogram
                    status = procedure.get("status")
                    # NOTE: can assume it's ICD10
                    procedure_code = nested_get(procedure, "code.coding[0].code")
                    if status == "completed" and str(procedure_code) == "71651007":
                        res.add(pid)
        return res

    def numerator_exclusions(self) -> set[str] | None:
        """
        N/A
        """
        return None

    def denominator_exceptions(self) -> set[str] | None:
        """
        N/A
        """
        return None
