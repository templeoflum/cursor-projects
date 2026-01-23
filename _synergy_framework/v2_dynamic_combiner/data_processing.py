# Data Processing
def resolve_seed(dynamic_attributes, law_data, dyn_data):
    unified_seed = dyn_data.get("seed", None)
    use_unified_seed = dyn_data.get("use_unified_seed", False)
    if use_unified_seed and unified_seed is not None:
        return unified_seed, "Inherited from Unified Seed"
    specific_seed = dynamic_attributes.get("seed", law_data.get("seed", 0.35))
    return specific_seed, "Explicitly Defined"

def process_dynamic_combination(file_data_layers, fluctuation_factor=1.2):
    foundation_files, application_files, implementation_files, execution_files, design_files = file_data_layers
    dynamic_attributes = {}
    for file_data in foundation_files:
        for key, value in file_data.get("attributes", {}).items():
            dynamic_attributes.setdefault(key, value)
    law_data = foundation_files[0]
    dyn_data = foundation_files[1]
    effective_seed, seed_source = resolve_seed(dynamic_attributes, law_data, dyn_data)
    dynamic_attributes["seed"] = effective_seed
    dynamic_attributes["seed_source"] = seed_source
    for layer_files in [application_files, implementation_files, execution_files, design_files]:
        for file_data in layer_files:
            for attr, attr_data in file_data.get("dynamic_attributes", {}).items():
                if attr in dynamic_attributes:
                    process_tuned_values(attr_data, dynamic_attributes[attr], effective_seed, fluctuation_factor)
    return dynamic_attributes

def process_tuned_values(attr_data, dynamic_attr, effective_seed, fluctuation_factor):
    range_min, range_max = map(float, attr_data.get("fluctuation_range", "0 to 0").split(" to "))
    offset_min, offset_max = map(float, attr_data.get("offset_range", "0 to 0").split(" to "))
    fluctuation = calculate_fluctuation(effective_seed) * fluctuation_factor
    offset = (offset_max - offset_min) * fluctuation + (offset_min + offset_max) / 2
    modulated_value = (fluctuation * (range_max - range_min) / 2) + ((range_min + range_max) / 2) + offset
    dynamic_attr["tuned_value"] = round(normalize_value(modulated_value, range_min, range_max), 4)
