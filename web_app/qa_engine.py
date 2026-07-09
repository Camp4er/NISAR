import json
from pathlib import Path

# Load deformation stats
STATS_PATH = Path(r"C:\Users\saxen\OneDrive\Desktop\NISAR_Project\data\processed\deformation_stats.json")

def load_stats():
    try:
        with open(STATS_PATH) as f:
            return json.load(f)
    except:
        return {}

KNOWLEDGE_BASE = [
    {
        "keywords": ["nisar", "what is nisar", "about nisar"],
        "answer": "NISAR (NASA-ISRO Synthetic Aperture Radar) is a joint Earth observation satellite mission between NASA and ISRO. Launched in 2024, it uses L-band and S-band SAR to measure surface deformation with millimeter-level precision. It is the first radar imaging satellite jointly developed by two different space agencies."
    },
    {
        "keywords": ["sar", "synthetic aperture radar", "how does sar work"],
        "answer": "Synthetic Aperture Radar (SAR) is a radar system that emits microwave pulses toward Earth and measures the reflected signals. Unlike optical satellites, SAR works through clouds, smoke, and at night. NISAR uses L-band SAR (wavelength ~23.8 cm) which can even penetrate vegetation to detect ground movement beneath."
    },
    {
        "keywords": ["insar", "interferometry", "how does insar work"],
        "answer": "InSAR (Interferometric SAR) compares two SAR images taken at different times over the same area. By measuring the phase difference between the two images, scientists can detect surface deformation as small as a few millimeters. This is how we produced the displacement map of the Shillong Plateau."
    },
    {
        "keywords": ["shillong", "shillong plateau", "meghalaya", "study area"],
        "answer": "The Shillong Plateau in Northeast India is one of the most seismically active regions in the world. It sits on the Oldham Fault, responsible for the catastrophic 1897 Great Assam Earthquake (M8.1). The plateau is a rigid crustal block that creates intense stress accumulation at its boundaries, making it critical to monitor for earthquake hazard assessment."
    },
    {
        "keywords": ["oldham fault", "fault", "fault line"],
        "answer": "The Oldham Fault is a major east-west trending reverse fault located along the southern edge of the Shillong Plateau. It was responsible for the 1897 Great Assam Earthquake (M8.1), one of the largest earthquakes ever recorded. The fault remains locked and accumulates stress, posing significant future earthquake risk to the region."
    },
    {
        "keywords": ["1897", "great assam earthquake", "historical earthquake"],
        "answer": "The 1897 Great Assam Earthquake (M8.1) was one of the most powerful earthquakes in recorded history. It struck the Shillong Plateau along the Oldham Fault and caused widespread destruction across Assam and Bengal. The earthquake uplifted the Shillong Plateau by several meters — one of the largest measured coseismic uplifts ever recorded."
    },
    {
        "keywords": ["displacement", "deformation", "ground movement", "results", "findings"],
        "answer": None  # Will be filled dynamically from stats
    },
    {
        "keywords": ["sentinel", "sentinel-1", "previous satellite", "before nisar"],
        "answer": "Sentinel-1 is a C-band SAR satellite operated by ESA. Before NISAR, it was the primary satellite used for InSAR analysis in India. However, Sentinel-1's C-band has limited penetration through dense vegetation and has a 12-day revisit time. NISAR's L-band penetrates vegetation far better and will eventually achieve 12-day or shorter revisit, making it far superior for monitoring regions like the Shillong Plateau."
    },
    {
        "keywords": ["nisar vs sentinel", "nisar better", "advantage of nisar", "improvement"],
        "answer": "NISAR improves upon Sentinel-1 in several key ways for the Shillong Plateau: (1) L-band vs C-band — better penetration through dense Northeast Indian vegetation; (2) Dual frequency — both L and S band give complementary information; (3) Higher spatial resolution; (4) Specifically designed for land deformation monitoring. For remote, forested regions like Meghalaya, NISAR is a transformational improvement."
    },
    {
        "keywords": ["earthquake risk", "hazard", "danger", "future earthquake"],
        "answer": "The Shillong Plateau region faces significant earthquake risk. The Oldham Fault remains seismically active and stress is continuously accumulating. The region also sits near the Indo-Burma subduction zone and the Main Frontal Thrust. Continuous monitoring using NISAR's InSAR data can help detect inter-seismic strain build-up, giving scientists better tools to assess earthquake hazard and potentially provide earlier warnings."
    },
    {
        "keywords": ["los", "line of sight", "los displacement"],
        "answer": "Line-of-Sight (LOS) displacement is the component of ground movement measured along the direction from the satellite to the ground. Positive LOS displacement means the ground is moving toward the satellite (typically uplift), while negative means movement away (subsidence or downward). LOS measurements are then decomposed into vertical and horizontal components using multiple satellite passes."
    },
    {
        "keywords": ["coherence", "what is coherence"],
        "answer": "Coherence in InSAR is a measure of signal quality between two SAR images, ranging from 0 (no correlation) to 1 (perfect correlation). Low coherence occurs over water, dense vegetation, or areas that changed significantly between the two image acquisitions. In our analysis, pixels with coherence below 0.5 were masked out to ensure only reliable displacement measurements are shown."
    },
    {
        "keywords": ["how was this made", "how did you make this", "methodology", "how it works"],
        "answer": "This project downloads ARIA S1 GUNW interferometric products from the ASF DAAC (Alaska Satellite Facility). These are pre-processed InSAR products containing unwrapped phase and coherence layers. We extract these layers using h5py, apply a coherence mask to remove unreliable pixels, then convert the unwrapped phase to Line-of-Sight displacement in centimeters using the Sentinel-1 C-band wavelength (5.5 cm). The results are visualized as displacement maps over the Shillong Plateau."
    },
    {
        "keywords": ["risk", "risk level", "current risk", "danger level"],
        "answer": "The risk level is calculated based on the deformation velocity across multiple InSAR acquisitions. We compare the rate of ground movement against the historical baseline for the Shillong Plateau. Elevated velocity suggests accelerating strain accumulation on the Oldham Fault, which increases the probability of a seismic event."
    },
    {
        "keywords": ["time series", "velocity", "deformation rate", "how fast"],
        "answer": "Deformation velocity is calculated by comparing displacement measurements across multiple InSAR pairs over time. We divide the total displacement by the time interval between acquisitions to get cm/year. Accelerating velocity is one of the key precursor signals monitored in earthquake hazard assessment."
    },
    {
        "keywords": ["magnitude", "how big", "earthquake size", "richter"],
        "answer": "Potential earthquake magnitude is estimated using the Wells & Coppersmith (1994) empirical relationship: M = 4.07 + 0.98 × log(Rupture Area in km²). The rupture area is estimated from the spatial extent of anomalous deformation detected in the InSAR data. This gives a probabilistic magnitude range, not a precise prediction."
    },
    {
        "keywords": ["alert", "warning", "evacuation", "what to do"],
        "answer": "When the risk monitor detects anomalous deformation velocity exceeding the threshold, an alert is issued with three levels: ELEVATED (1.5x baseline) recommends increased monitoring and preparedness; HIGH RISK (2x baseline) recommends authorities be notified and evacuation plans activated; CRITICAL (3x baseline) recommends immediate evacuation of high-risk zones near the fault trace."
    },
    {
        "keywords": ["population", "affected", "how many people", "impact"],
        "answer": "The Shillong Plateau and surrounding regions have a population of approximately 3.5 million people. The Guwahati metropolitan area alone has over 1 million residents within 100km of the Oldham Fault. A major rupture (M7+) on the Oldham Fault could affect 10-15 million people across Assam, Meghalaya, and Bangladesh."
    },
]

def get_answer(question: str) -> str:
    question = question.lower().strip()
    stats = load_stats()

    # Check each knowledge base entry
    for entry in KNOWLEDGE_BASE:
        for keyword in entry["keywords"]:
            if keyword in question:
                # Dynamic answer for displacement/results
                if entry["answer"] is None and stats:
                    return (
                        f"Our InSAR analysis of the Shillong Plateau detected surface displacement "
                        f"ranging from {stats.get('max_subsidence_cm', 'N/A'):.1f} cm (subsidence) to "
                        f"+{stats.get('max_uplift_cm', 'N/A'):.1f} cm (uplift), with a mean displacement "
                        f"of {stats.get('mean_displacement_cm', 'N/A'):.2f} cm. "
                        f"A total of {stats.get('valid_pixels', 'N/A'):,} pixels were analyzed after "
                        f"coherence masking. The uplift pattern is consistent with inter-seismic strain "
                        f"accumulation along the Oldham Fault system."
                    )
                elif entry["answer"]:
                    return entry["answer"]

    # Default response
    return (
        "I can answer questions about NISAR, InSAR, the Shillong Plateau, the Oldham Fault, "
        "earthquake history in Northeast India, our displacement findings, satellite comparison "
        "(NISAR vs Sentinel-1), and our methodology. Try asking about any of these topics!"
    )