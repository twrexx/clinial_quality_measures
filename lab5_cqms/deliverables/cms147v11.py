from datetime import datetime
from typing import Any

import arrow
from util.helpers import (
    date_is_within_date_range,
    get_datediff_in_years,
    get_reference_id_from_resource,
    nested_get,
)
from util.runner import BaseRunner


class CMS147v11Runner(BaseRunner):
    """
    CMS147v11 - Preventive Care and Screening: Influenza Immunization

    Reference: https://ecqi.healthit.gov/ecqm/ec/2022/cms147v11

    Each function docstring will specify additional exceptions + cases to focus on for the purpose of this lab.
    """

    def __init__(
        self,
        start_period: datetime,
        end_period: datetime,
        patient_list: list[dict[str, Any]],
        encounter_list: list[dict[str, Any]],
        immunization_list: list[dict[str, Any]],
    ):
        super().__init__(start_period, end_period)
        self.patient_list = patient_list
        self.encounter_list = encounter_list
        self.immunization_list = immunization_list

    def initial_population(self) -> set[str]:
        """
        Criteria:
        - Patient has an Encounter during the measurement period
            - The Patient has an age of >= 0.5 at the start of the encounter
        """
        # Implement code for the calculating the Initial Population here.
        # FIXME
        res = set()
        for encounter in self.encounter_list:
            pid = get_reference_id_from_resource(encounter)
            encounterDate = nested_get(encounter, 'period.start')
            if date_is_within_date_range(encounterDate, self.start_period, self.end_period):
                for patient in self.patient_list:
                    if patient.get('id') == pid:
                        age = get_datediff_in_years(patient.get('birthDate'), encounterDate)
                        if age >= 0.5:
                            res.add(pid)
        return res

    def denominator(self) -> set[str]:
        """
        Criteria:
        - Patient is in the initial population
        - Patient has an Encounter within the date range and the date
          is between the months of October and March
        """
        # Implement code for calculating the Denominator here.
        # FIXME
        res = set()
        initial_pop = self.initial_population()
        for encounter in self.encounter_list:
            patient = encounter.get('subject')
            pid = patient.get('reference')[8:]          # get patient id from encounter
            # print(pid)
            if pid in initial_pop:                      # if the patient id is in the initial population
                start = nested_get(encounter, "period.start")
                end = nested_get(encounter, "period.end")
                startMonth = int(start.split('-')[1])
                endMonth = int(end.split('-')[1])
                if (date_is_within_date_range(start, self.start_period, self.end_period) and (startMonth <= 3 or startMonth >= 10) or (date_is_within_date_range(end, self.start_period, self.end_period) and (endMonth <= 3 or endMonth >= 10))):
                    res.add(pid)
            
        return res

    def denominator_exclusions(self) -> set[str] | None:
        """
        None
        """
        return None

    def numerator(self) -> set[str]:
        """
        Criteria:
        - Patient is in the denominator
        - Patient has a completed Immunization for influenza that occurred within the measurement period
            - Influenza CVX code: 140. You can also use the text description in the CodableConcept.
            - Note that "140" == 140 evaluates to False in Python, since one is a `str` and the other is an `int`.
              Ensure that you are comparing string to string.
        """
        # Implement code for calculating the Numerator here.
        # FIXME
        res = set()
        denom = self.denominator()
        for immunization in self.immunization_list:
            pid = immunization.get('patient').get('reference')[8:]
            if pid in denom:
                code = nested_get(immunization, "vaccineCode.coding")[0].get('code')
                date = immunization.get('occurrenceDateTime')
                status = immunization.get('status')
                if code == '140' and date_is_within_date_range(date, self.start_period, self.end_period) and status == 'completed':
                    res.add(pid)
        return res

    def numerator_exclusions(self) -> set[str] | None:
        """
        N/A
        """
        return None

    def denominator_exceptions(self) -> set[str] | None:
        """
        Students Not Required to Implement
        """
        return None
