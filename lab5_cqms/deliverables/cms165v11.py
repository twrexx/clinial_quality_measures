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
        res = set()
        for patient in self.patient_list:
            age = get_datediff_in_years(patient.get("birthDate"), self.end_period)
            if 18.0 <= age <= 85.0:
                pid = patient.get("id")
                condition_list = get_resource_sublist(self.condition_list, {pid})
                for c in condition_list:
                    snom = nested_get(c, "code.coding")[0]
                    if snom.get('code') == '59621000':

                        res.add(pid)
        return res

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
        denom = self.denominator()
        res = set()
        temp = set()
        for patient in self.patient_list:
            pid = patient.get('id')
            if pid in denom:
                birthdate = patient.get('birthDate')
                age = get_datediff_in_years(birthdate, self.end_period)
                if 66 <= age <= 80:
                    temp.add(pid)
        
        for condition in self.condition_list:
            pid = get_reference_id_from_resource(condition)
            if pid in temp:
                con = nested_get(condition, 'code.coding')[0].get('display')
                if con in ADVANCED_ILLNESS_SET:
                    res.add(pid)

        return res
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
        denom = self.denominator()
        res = set()
        temp = {}
        for observation in self.observation_list:
            pid = get_reference_id_from_resource(observation)
            if pid in denom:
                effectiveDate = observation.get('effectiveDateTime')
                components = observation.get('component')
                dia = False
                sys = False
                diastolic = 0
                systolic = 0
                if components != None:
                    for c in components:
                        tt = (c.get('code').get('text'))
                        if c.get('code').get('text') == 'Diastolic Blood Pressure':
                            diastolic = c.get('valueQuantity').get('value')
                            dia = True
                            print('dia=', dia)
                        if c.get('code').get('text') == 'Systolic Blood Pressure':
                            systolic = c.get('valueQuantity').get('value')
                            print(type(systolic), systolic)
                            sys = True
                if pid in temp:
                    if temp.get(pid)[0] <= effectiveDate:
                        temp[pid][0] = effectiveDate
                        if diastolic <= 90 and dia and systolic <= 140 and sys:
                            temp[pid][1] = True
                        else:
                            temp[pid][1] = False
                else:
                    if diastolic <= 90 and systolic <= 140:
                        temp[pid] = [effectiveDate, True]
                    else:
                        temp[pid] = [effectiveDate, False]
        print(temp)

        return res

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
