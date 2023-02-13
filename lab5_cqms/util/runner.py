import json
from abc import ABC, abstractmethod
from datetime import datetime
from os import mkdir
from typing import Any


class BaseRunner(ABC):
    def __init__(
        self, start_period: datetime, end_period: datetime, *args: Any, **kwargs: Any
    ):
        self.start_period = start_period
        self.end_period = end_period

    @abstractmethod
    def initial_population(self) -> set[str]:
        """
        Returns the set of patient id values

        Calculate independently of exclusions and exceptions
        """
        ...
        raise NotImplementedError()

    @abstractmethod
    def denominator(self) -> set[str]:
        """
        Returns the set of patient id values

        Calculate independently of exclusions and exceptions
        """
        ...
        raise NotImplementedError()

    @abstractmethod
    def denominator_exclusions(self) -> set[str] | None:
        """
        Returns the set of patient id values (if applicable, else None)

        Ref: https://ecqi.healthit.gov/glossary/denominator-exclusion
        """
        ...
        raise NotImplementedError()

    @abstractmethod
    def numerator(self) -> set[str]:
        """
        Returns the set of patient id values

        Calculate independently of exclusions and exceptions
        """
        ...
        raise NotImplementedError()

    @abstractmethod
    def numerator_exclusions(self) -> set[str] | None:
        """
        Returns the set of patient id values (if applicable, else None)

        Ref: https://ecqi.healthit.gov/glossary/numerator-exclusion
        """
        ...
        raise NotImplementedError()

    @abstractmethod
    def denominator_exceptions(self) -> set[str] | None:
        """
        Returns the set of patient id values (if applicable, else None)

        Ref: https://ecqi.healthit.gov/glossary/denominator-exception
        """
        ...
        raise NotImplementedError()

    def run_all(
        self, print_counts: bool = False, save_to_dir: str | None = None
    ) -> dict[str, set[str] | None]:
        """Runs all of the results and returns as a dict"""
        res = {
            "initial_population": self.initial_population(),
            "denominator": self.denominator(),
            "denominator_exclusions": self.denominator_exclusions(),
            "numerator": self.numerator(),
            "numerator_exclusions": self.numerator_exclusions(),
            "denominator_exceptions": self.denominator_exceptions(),
        }
        if print_counts:
            print(f"🖥️  Printing results for: {type(self).__name__}")
            for k, v in res.items():
                print(f"\t{k}: {len(v) if v else None}")
        if save_to_dir:
            try:
                mkdir(save_to_dir)
            except:
                pass
            for k, v in res.items():
                # Save as sorted list
                cqm_dir = f"{save_to_dir}/{type(self).__name__}"
                try:
                    mkdir(cqm_dir)
                except:
                    pass
                filename = f"{cqm_dir}/{k}.json"
                with open(filename, "w") as file:
                    if v:
                        file.write(json.dumps(sorted(list(v)), indent=2))
                    else:
                        file.write("null")
                    file.write("\n")
        return res
