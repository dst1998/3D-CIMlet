import math

def NoP_hardware_estimation(config, ebit, area_per_lane_28nm, clocking_area, n_lane, num_used_static_chiplet, num_used_semi_static_chiplet, num_used_dynamic_chiplet, n_bits_all_chiplets):
    # area = (area_per_lane * n_lane+clocking_area) * n_chiplet
    area = (area_per_lane_28nm * (math.pow(config.static_chiplet_technode, 2)/math.pow(40,2))) * num_used_static_chiplet + (area_per_lane_28nm * (math.pow(config.static_chiplet_technode, 2)/math.pow(40,2))) * num_used_semi_static_chiplet + (area_per_lane_28nm * (math.pow(config.dynamic_chiplet_technode, 2)/math.pow(40,2))) * num_used_dynamic_chiplet
    energy = ebit*n_bits_all_chiplets
    return area, energy