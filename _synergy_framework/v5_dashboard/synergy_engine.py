# synergy_engine.py
import random

def run_feedback_loop(step_ui_data, seed_value):
    """
    step_ui_data: a list (or dict) of steps, each with:
      {
        'stepName': 'Potential',
        'offset': <float from offset slider>,
        'expansions': <bool from expansions checkbutton>
      }
    seed_value: float from the synergy seed slider

    We'll do a trivial synergy approach:
      synergy_next = synergy_current + offset +/- expansions effect
    """
    synergy_values = {}
    current_synergy = seed_value

    for step_info in step_ui_data:
        step_name = step_info["stepName"]
        offset = step_info["offset"]
        expansions_on = step_info["expansions"]

        # Base synergy is current + offset
        new_synergy = current_synergy + offset

        # If expansions are on, let's add a small random shift 
        # just as a demonstration. 
        # In a real system, you'd integrate expansions from expansions folder.
        if expansions_on:
            # e.g. an additional random offset in [-0.05, 0.05]
            expansions_effect = random.uniform(-0.05, 0.05)
            new_synergy += expansions_effect

        synergy_values[step_name] = new_synergy
        current_synergy = new_synergy

    synergy_values["final"] = current_synergy
    return synergy_values
