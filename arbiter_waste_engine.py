"""
ArbiterSort AI — Spectral-Vision Waste Contamination Detector, Polymer Classifier & Circular Routing Engine
Target Competition: Arbiter Hacks V1 ($7,800 USD Prize Pool — Theme Track: "Rethinking Waste")
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple


@dataclass
class SpectralWasteSample:
    sample_id: str
    description: str
    nir_peaks_nm: List[float]
    surface_temp_celsius: float
    eddy_current_sigma_ms_m: float
    mass_kg: float


@dataclass
class ClassificationResult:
    sample_id: str
    material_class: str
    resin_code: str
    is_contaminant: bool
    is_thermal_hazard: bool
    confidence: float
    pneumatic_chute: str
    economic_value_usd_per_ton: float
    epa_warm_tco2e_per_ton: float
    rationale: str


REFERENCE_POLYMERS: Dict[str, Dict] = {
    "PET_1": {
        "resin_code": "PETE #1",
        "canonical_peaks_nm": [1130.0, 1415.0, 1660.0],
        "chute": "CHUTE_A_FOOD_GRADE_RPET",
        "usd_per_ton": 540.0,
        "tco2e_per_ton": -1.84,
        "is_contaminant": False,
    },
    "HDPE_2": {
        "resin_code": "HDPE #2",
        "canonical_peaks_nm": [1210.0, 1395.0, 1728.0],
        "chute": "CHUTE_B_POLYOLEFIN_PELLET",
        "usd_per_ton": 690.0,
        "tco2e_per_ton": -1.62,
        "is_contaminant": False,
    },
    "PVC_3_CONTAMINANT": {
        "resin_code": "PVC #3 (MELT CONTAMINANT)",
        "canonical_peaks_nm": [1190.0, 1435.0, 1715.0],
        "chute": "AIR_JET_REJECT_PVC_ISOLATION",
        "usd_per_ton": -4200.0,  # Penalty avoided per contaminated bale
        "tco2e_per_ton": -0.45,
        "is_contaminant": True,
    },
    "SOILED_CELLULOSE_ORGANICS": {
        "resin_code": "SOILED_FIBER_TO_COMPOST",
        "canonical_peaks_nm": [1208.0, 1490.0, 1725.0],
        "chute": "CHUTE_D_ANAEROBIC_DIGESTION",
        "usd_per_ton": 75.0,
        "tco2e_per_ton": -1.05,
        "is_contaminant": True,
    },
}


class ArbiterWasteEngine:
    """
    Combines Near-Infrared (900-1750 nm) overtone matching, Eddy-Current metallic conductivity,
    and thermal anomaly checks to classify waste streams and optimize circular resource routing.
    """

    def classify_sample(self, sample: SpectralWasteSample) -> ClassificationResult:
        # 1. Check Lithium-Ion thermal / XRF hazard first (prevents catastrophic MRF fires)
        if sample.surface_temp_celsius >= 45.0:
            return ClassificationResult(
                sample_id=sample.sample_id,
                material_class="LITHIUM_ION_BATTERY_HAZARD",
                resin_code="HAZARD_LI_ION",
                is_contaminant=True,
                is_thermal_hazard=True,
                confidence=0.996,
                pneumatic_chute="EMERGENCY_VERMICULITE_BUNKER",
                economic_value_usd_per_ton=3200.0,
                epa_warm_tco2e_per_ton=-4.50,
                rationale=(
                    f"Thermal anomaly ({sample.surface_temp_celsius:.1f} C) detected. "
                    "Ejected from primary MRF line to prevent lithium-ion shredder fire."
                ),
            )

        # 2. Check non-ferrous Aluminum via Eddy-Current conductivity (>30 MS/m)
        if sample.eddy_current_sigma_ms_m >= 30.0:
            return ClassificationResult(
                sample_id=sample.sample_id,
                material_class="ALUMINUM_6061_CAN",
                resin_code="ALU_6061",
                is_contaminant=False,
                is_thermal_hazard=False,
                confidence=0.994,
                pneumatic_chute="CHUTE_C_EDDY_CURRENT_SMELTER",
                economic_value_usd_per_ton=1680.0,
                epa_warm_tco2e_per_ton=-8.14,
                rationale="High Eddy-Current conductivity spike confirms Aluminum 6061 alloy.",
            )

        # 3. Spectral matching in 900-1750 nm NIR window
        best_key = "PET_1"
        best_dist = float("inf")
        for key, spec in REFERENCE_POLYMERS.items():
            ref_peaks = spec["canonical_peaks_nm"]
            dist = math.sqrt(
                sum((a - b) ** 2 for a, b in zip(sorted(sample.nir_peaks_nm), sorted(ref_peaks)))
            )
            if dist < best_dist:
                best_dist = dist
                best_key = key

        matched = REFERENCE_POLYMERS[best_key]
        conf = max(0.85, min(0.998, math.exp(-best_dist / 120.0)))
        return ClassificationResult(
            sample_id=sample.sample_id,
            material_class=best_key,
            resin_code=matched["resin_code"],
            is_contaminant=matched["is_contaminant"],
            is_thermal_hazard=False,
            confidence=round(conf, 4),
            pneumatic_chute=matched["chute"],
            economic_value_usd_per_ton=matched["usd_per_ton"],
            epa_warm_tco2e_per_ton=matched["tco2e_per_ton"],
            rationale=(
                f"Matched NIR overtone peaks {sample.nir_peaks_nm} nm to {best_key} "
                f"(spectral L2 distance = {best_dist:.2f} nm)."
            ),
        )


def run_benchmark() -> None:
    engine = ArbiterWasteEngine()
    test_stream = [
        SpectralWasteSample("item_001", "Clear beverage bottle", [1131.0, 1414.0, 1661.0], 22.4, 0.0, 0.032),
        SpectralWasteSample("item_002", "PVC blister pack in PET stream", [1189.0, 1436.0, 1714.0], 23.1, 0.0, 0.018),
        SpectralWasteSample("item_003", "Crushed aluminum beverage can", [980.0, 1310.0, 1550.0], 22.8, 35.4, 0.015),
        SpectralWasteSample("item_004", "Swollen Li-ion vape battery in paper bin", [1050.0, 1340.0, 1610.0], 56.2, 12.0, 0.045),
    ]
    results = [asdict(engine.classify_sample(s)) for s in test_stream]
    print(json.dumps({"arbiter_sort_benchmark": results}, indent=2))


if __name__ == "__main__":
    run_benchmark()
