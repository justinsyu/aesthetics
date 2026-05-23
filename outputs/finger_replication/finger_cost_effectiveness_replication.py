#!/usr/bin/env python3
"""Best-effort replication of Wimo et al. FINGER cost-effectiveness model.

This script uses only numeric inputs available in the two user-supplied
markdown files. It does not tune or calibrate any parameter to the paper's
published results.

Key approximations forced by the supplied files:
- Mortality inputs were updated from Statistics Sweden's 2016 single-year
  life table by sex and age.
- Cost inputs are available as rounded 5-year figure-readout values, not the
  original annual cost GLM coefficients.
- Dementia incidence is calculated from the supplied Poisson coefficients and
  converted from a rate to a 1-year probability.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, log
from typing import Dict, Iterable, Mapping


StateCounts = Dict[str, float]

STATES = ("at_risk", "mild", "moderate", "severe")
AGE_POINTS = (50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100)
ANNUAL_AGE_POINTS = tuple(range(50, 101))


@dataclass(frozen=True)
class ModelConfig:
    cohort_size: float = 100_000
    start_age: int = 70
    cycles: int = 30
    discount_rate: float = 0.03
    intervention_cost: float = 5_490
    intervention_relative_risk: float = 0.9356
    base_risk_multiplier: float = 2.0
    willingness_to_pay: float = 600_000


INCIDENCE_AGE_COEF = 0.138517
INCIDENCE_INTERCEPT = -14.9949

DEMENTIA_TRANSITIONS: Mapping[str, Mapping[str, float]] = {
    "mild": {"mild": 0.75, "moderate": 0.25, "severe": 0.00},
    # Moderate and severe rows sum to 1.01 in the rounded supplemental table.
    # The transition function normalizes each row before applying it.
    "moderate": {"mild": 0.09, "moderate": 0.83, "severe": 0.09},
    "severe": {"mild": 0.03, "moderate": 0.13, "severe": 0.85},
}

# Source: Statistics Sweden, "Life table by sex and age. Year 1960-2025",
# matrix BE0101AW, observations "Probability of dying (per mille)" and
# "Number living at age", 2016. Downloaded via PxWeb API:
# https://api.scb.se/OV0104/v1/doris/en/ssd/START/BE/BE0101/BE0101I/LivslangdEttariga
SCB_LIFE_TABLE_QX_PER_MILLE_2016: Mapping[str, Iterable[float]] = {
    "men": (2.16, 2.47, 2.39, 2.86, 3.76, 3.82, 4.31, 4.19, 4.85, 5.37, 6.37, 7.62, 8.35, 8.21, 9.72, 10.25, 12.09, 13.21, 13.64, 15.48, 16.88, 19.06, 20.59, 24.49, 24.43, 27.62, 33.47, 35.74, 41.92, 45.34, 53.16, 59.70, 65.67, 72.59, 87.11, 98.12, 109.92, 125.14, 131.48, 150.62, 173.99, 197.53, 217.17, 238.90, 260.83, 285.29, 310.19, 336.43, 363.95, 392.70, 422.64),
    "women": (1.63, 1.61, 1.80, 1.96, 1.85, 2.79, 2.93, 2.73, 3.24, 3.98, 4.44, 4.64, 5.43, 5.83, 6.10, 6.94, 8.01, 8.27, 9.33, 9.47, 11.09, 13.14, 15.30, 16.37, 16.65, 17.98, 22.16, 23.88, 27.33, 32.21, 36.66, 40.28, 47.17, 53.56, 60.20, 72.57, 80.87, 91.85, 99.45, 123.19, 140.55, 162.62, 167.34, 194.56, 221.05, 234.19, 255.81, 278.76, 303.03, 328.58, 355.39),
}

SCB_LIFE_TABLE_LX_2016: Mapping[str, Iterable[float]] = {
    "men": (96680, 96471, 96233, 96003, 95729, 95369, 95005, 94595, 94199, 93742, 93239, 92645, 91939, 91171, 90423, 89544, 88626, 87554, 86397, 85218, 83899, 82483, 80911, 79245, 77305, 75417, 73334, 70880, 68347, 65482, 62513, 59190, 55657, 52002, 48227, 44026, 39706, 35342, 30919, 26854, 22809, 18840, 15118, 11835, 9008, 6658, 4759, 3283, 2179, 1386, 842),
    "women": (98054, 97894, 97736, 97560, 97369, 97188, 96917, 96633, 96369, 96057, 95675, 95250, 94808, 94294, 93744, 93173, 92526, 91785, 91026, 90177, 89323, 88333, 87172, 85839, 84434, 83028, 81535, 79728, 77824, 75697, 73259, 70573, 67730, 64535, 61078, 57401, 53236, 48931, 44437, 40018, 35088, 30156, 25252, 21026, 16935, 13192, 10103, 7519, 5423, 3780, 2538),
}

MORTALITY_HAZARD_RATIOS: Mapping[str, float] = {
    "at_risk": 1.0,
    "mild": 1.31,
    "moderate": 2.37,
    "severe": 4.11,
}

COSTS: Mapping[str, Iterable[float]] = {
    "at_risk": (20_000, 30_000, 45_000, 65_000, 90_000, 120_000, 155_000, 195_000, 245_000, 305_000, 375_000),
    "mild": (230_000, 250_000, 275_000, 300_000, 330_000, 360_000, 395_000, 435_000, 480_000, 530_000, 585_000),
    "moderate": (315_000, 340_000, 370_000, 405_000, 445_000, 485_000, 530_000, 580_000, 640_000, 705_000, 780_000),
    "severe": (365_000, 395_000, 430_000, 470_000, 515_000, 565_000, 620_000, 680_000, 750_000, 830_000, 920_000),
}

UTILITIES: Mapping[str, Iterable[float]] = {
    "at_risk": (0.839, 0.827, 0.815, 0.803, 0.790, 0.778, 0.766, 0.753, 0.741, 0.729, 0.716),
    "mild": (0.706, 0.694, 0.681, 0.669, 0.657, 0.644, 0.632, 0.620, 0.607, 0.595, 0.583),
    "moderate": (0.462, 0.450, 0.438, 0.425, 0.413, 0.401, 0.389, 0.376, 0.364, 0.352, 0.339),
    "severe": (0.309, 0.296, 0.284, 0.272, 0.259, 0.247, 0.235, 0.223, 0.210, 0.198, 0.186),
}


def interpolate(age: float, values: Iterable[float]) -> float:
    values = tuple(values)
    if age <= AGE_POINTS[0]:
        return values[0]
    if age >= AGE_POINTS[-1]:
        return values[-1]
    for left_index, left_age in enumerate(AGE_POINTS[:-1]):
        right_age = AGE_POINTS[left_index + 1]
        if left_age <= age <= right_age:
            fraction = (age - left_age) / (right_age - left_age)
            return values[left_index] + fraction * (values[left_index + 1] - values[left_index])
    raise ValueError(f"Age {age} is outside interpolation range")


def interpolate_annual(age: float, values: Iterable[float]) -> float:
    values = tuple(values)
    if age <= ANNUAL_AGE_POINTS[0]:
        return values[0]
    if age >= ANNUAL_AGE_POINTS[-1]:
        return values[-1]
    left_age = int(age)
    right_age = left_age + 1
    fraction = age - left_age
    left_value = values[left_age - ANNUAL_AGE_POINTS[0]]
    right_value = values[right_age - ANNUAL_AGE_POINTS[0]]
    return left_value + fraction * (right_value - left_value)


def mortality_probability(age: float, state: str) -> float:
    male_qx = interpolate_annual(age, SCB_LIFE_TABLE_QX_PER_MILLE_2016["men"]) / 1000
    female_qx = interpolate_annual(age, SCB_LIFE_TABLE_QX_PER_MILLE_2016["women"]) / 1000
    male_lx = interpolate_annual(age, SCB_LIFE_TABLE_LX_2016["men"])
    female_lx = interpolate_annual(age, SCB_LIFE_TABLE_LX_2016["women"])
    male_weight = male_lx / (male_lx + female_lx)
    base_rate = male_weight * -log(1 - male_qx) + (1 - male_weight) * -log(1 - female_qx)
    return 1 - exp(-base_rate * MORTALITY_HAZARD_RATIOS[state])


def dementia_incidence_probability(age: float, strategy: str, config: ModelConfig) -> float:
    rate = exp(INCIDENCE_INTERCEPT + INCIDENCE_AGE_COEF * age)
    rate *= config.base_risk_multiplier
    if strategy == "prevention":
        rate *= config.intervention_relative_risk
    return 1 - exp(-rate)


def transition_one_cycle(counts: StateCounts, age: float, strategy: str, config: ModelConfig) -> tuple[StateCounts, float, float]:
    next_counts = {state: 0.0 for state in STATES}
    deaths = 0.0
    incident_dementia = 0.0

    at_risk = counts["at_risk"]
    at_risk_death_prob = mortality_probability(age, "at_risk")
    incidence_prob = dementia_incidence_probability(age, strategy, config)
    deaths += at_risk * at_risk_death_prob
    at_risk_survivors = at_risk * (1 - at_risk_death_prob)
    incident_dementia = at_risk_survivors * incidence_prob
    next_counts["mild"] += incident_dementia
    next_counts["at_risk"] += at_risk_survivors * (1 - incidence_prob)

    for state in ("mild", "moderate", "severe"):
        state_count = counts[state]
        death_prob = mortality_probability(age, state)
        deaths += state_count * death_prob
        survivors = state_count * (1 - death_prob)
        row_total = sum(DEMENTIA_TRANSITIONS[state].values())
        for next_state, transition_probability in DEMENTIA_TRANSITIONS[state].items():
            next_counts[next_state] += survivors * transition_probability / row_total

    return next_counts, deaths, incident_dementia


def run_model(strategy: str, config: ModelConfig) -> dict[str, object]:
    counts = {state: 0.0 for state in STATES}
    counts["at_risk"] = config.cohort_size

    total_cost = config.intervention_cost * config.cohort_size if strategy == "prevention" else 0.0
    total_qalys = 0.0
    total_deaths = 0.0
    total_incident_dementia = 0.0
    incident_by_year: list[float] = []
    death_by_year: list[float] = []
    person_years = {state: 0.0 for state in STATES}

    for cycle in range(config.cycles):
        age = config.start_age + cycle
        next_counts, deaths, incident_dementia = transition_one_cycle(counts, age, strategy, config)
        discount_factor = 1 / ((1 + config.discount_rate) ** (cycle + 0.5))

        for state in STATES:
            average_count = (counts[state] + next_counts[state]) / 2
            person_years[state] += average_count / config.cohort_size
            total_cost += average_count * interpolate(age, COSTS[state]) * discount_factor
            total_qalys += average_count * interpolate(age, UTILITIES[state]) * discount_factor

        total_deaths += deaths
        total_incident_dementia += incident_dementia
        incident_by_year.append(total_incident_dementia)
        death_by_year.append(total_deaths)
        counts = next_counts

    dementia_years = person_years["mild"] + person_years["moderate"] + person_years["severe"]
    return {
        "cost_per_person": total_cost / config.cohort_size,
        "qaly_per_person": total_qalys / config.cohort_size,
        "incident_dementia": total_incident_dementia,
        "deaths": total_deaths,
        "incident_by_year": incident_by_year,
        "death_by_year": death_by_year,
        "person_years_alive": person_years["at_risk"] + dementia_years,
        "person_years_without_dementia": person_years["at_risk"],
        "person_years_with_dementia": dementia_years,
        "person_years_mild": person_years["mild"],
        "person_years_moderate": person_years["moderate"],
        "person_years_severe": person_years["severe"],
    }


def cumulative_at_horizon(series: list[float], years: int) -> float:
    return series[years - 1]


def format_number(value: float, decimals: int = 0) -> str:
    return f"{value:,.{decimals}f}"


def main() -> None:
    config = ModelConfig()
    usual = run_model("usual_care", config)
    prevention = run_model("prevention", config)

    incremental_cost = prevention["cost_per_person"] - usual["cost_per_person"]
    incremental_qaly = prevention["qaly_per_person"] - usual["qaly_per_person"]
    nmb = incremental_qaly * config.willingness_to_pay - incremental_cost
    nhb = incremental_qaly - incremental_cost / config.willingness_to_pay

    print("Best-effort FINGER cost-effectiveness replication")
    print("No calibration to published results was performed.")
    print()
    print("Base-case cost-utility outputs, SEK 2016 per person")
    print(f"  Usual care cost:     {format_number(usual['cost_per_person'])}")
    print(f"  Prevention cost:     {format_number(prevention['cost_per_person'])}")
    print(f"  Incremental cost:    {format_number(incremental_cost)}")
    print(f"  Usual care QALYs:    {usual['qaly_per_person']:.3f}")
    print(f"  Prevention QALYs:    {prevention['qaly_per_person']:.3f}")
    print(f"  Incremental QALYs:   {incremental_qaly:.3f}")
    print(f"  ICER:                {'dominant' if incremental_cost < 0 and incremental_qaly > 0 else incremental_cost / incremental_qaly:}")
    print(f"  NMB at 600k/QALY:    {format_number(nmb)}")
    print(f"  NHB at 600k/QALY:    {nhb:.3f}")
    print()
    print("Base-case event and person-year outputs, initial cohort of 100,000")
    for years in (10, 20, 30):
        usual_cases = cumulative_at_horizon(usual["incident_by_year"], years)
        prevention_cases = cumulative_at_horizon(prevention["incident_by_year"], years)
        avoided = usual_cases - prevention_cases
        nnt = config.cohort_size / avoided if avoided > 0 else float("inf")
        print(
            f"  Dementia cases after {years:2d} years: "
            f"usual {format_number(usual_cases)}, prevention {format_number(prevention_cases)}, "
            f"avoided {format_number(avoided)}, NNT {nnt:.0f}"
        )
    print(
        "  Deaths after 30 years: "
        f"usual {format_number(usual['deaths'])}, prevention {format_number(prevention['deaths'])}, "
        f"difference {format_number(prevention['deaths'] - usual['deaths'])}"
    )
    print()
    print("Mean undiscounted person-years per person after 30 years")
    for label in (
        "person_years_alive",
        "person_years_without_dementia",
        "person_years_with_dementia",
        "person_years_mild",
        "person_years_moderate",
        "person_years_severe",
    ):
        print(
            f"  {label.replace('_', ' '):31s} "
            f"usual {usual[label]:.2f}, prevention {prevention[label]:.2f}, "
            f"difference {prevention[label] - usual[label]:.2f}"
        )
    print()
    print("Data limitations from supplied files")
    print("  - Mortality now uses exact 2016 Statistics Sweden life-table qx and lx values.")
    print("  - Exact cost GLM coefficients are absent; only rounded 5-year cost readouts are available.")
    print("  - Rounded moderate/severe dementia progression rows sum to 1.01 and were normalized.")
    print("  - Cost and utility values between 5-year points were linearly interpolated.")


if __name__ == "__main__":
    main()
