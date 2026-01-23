# init_data.py
# ----------------------------------------------------------------------------
# Minimal data references for each 6-step module (Potential, Symmetry, Flow,
# Connectivity, Emergence, Recursion), plus default synergy seeds and thresholds.
# Paste this into your environment to serve as a test harness for balancing the system.
# ----------------------------------------------------------------------------

init_data = {
    "global": {
        "default_seed": 0.5,               # The universal baseline
        "epsilon_cyclic": 0.03,            # Allowed drift from synergy measure
        "law_file": "dflt.law",            # Default law if needed globally
        "dyn_file": "dflt.dyn"          # Default dynamic attributes referencing 0.5
    },
    "steps": {
        "Potential": {
            "law_file": "dflt.law",        # Could override or remain same as global
            "dyn_file": "default.dyn",     # Baseline dynamic config
            "reso_file": "01_Potential/potential_seed.law",  # e.g. a .reso or .law
            "tune_file": None,            # If you want a special tuning config
            "notes": "Seeds synergy from 0.5, exploring expansions"
        },
        "Symmetry": {
            "reso_file": "02_Symmetry/symmetrical_constraints.reso",
            "tune_file": "02_Symmetry/harmony_rules.tune",
            "notes": "Enforces balanced constraints around synergy ~0.5"
        },
        "Flow": {
            "dyn_file": "03_Flow/expansion_logic.dyn",
            "rule_file": "03_Flow/real_time_transform.rule",
            "notes": "Handles velocity expansions, referencing synergy offsets"
        },
        "Connectivity": {
            "rule_file": "04_Connectivity/bridging_module.rule",
            "style_file": "04_Connectivity/cross_domain.style",
            "notes": "Links expansions across domains, merges synergy states"
        },
        "Emergence": {
            "sheet_file": "05_Emergence/integrative_sheet.sheet",
            "design_file": "05_Emergence/synergy_design.design",
            "notes": "Realizes new synergy patterns, pivoting around 0.5 baseline"
        },
        "Recursion": {
            "rule_file": "06_Recursion/feedback_loop.rule",
            "reso_file": "06_Recursion/final_resoforms.reso",
            "notes": "Feeds synergy results back into Potential if outside cycic threshold"
        }
    }
}

# Example usage snippet (pseudo-code):
if __name__ == "__main__":
    # Suppose you have a synergy engine or combiner that expects data references
    # You can pass init_data to it for testing:
    from synergy_engine import combine_synergy

    synergy_result = combine_synergy(init_data)
    print("Synergy Test Result:", synergy_result)
