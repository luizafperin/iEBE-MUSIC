#!/usr/bin/env python3
"""
Design point 0 for TRENTo + free-streaming + MUSIC + UrQMD test batch.
"""

# control parameters
control_dict = {
    'initial_state_type': "TRENTo",
    'walltime': "10:00:00",
    'afterburner_type': "UrQMD",
    'save_hydro_surfaces': False,
    'save_UrQMD_files': False,
}

# Shared pre-generated isobar seed file (required).
isobar_seed_file = "shared_seeds/nucleon-seeds_197.hdf"

# isobar-sample
isobars_conf_dict_target = {
    "isobar_samples": {
        "description": "Options for the isobar nucleon-position samples",
        "number_configs": {
            "description": "Number of configurations to be sampled.",
            "value": 1,
        },
        "number_nucleons": {
            "description": "Mass number A of the nuclei.",
            "value": 197,
        },
        "seeds_file": {
            "description": "Input file with list of seeds for nucleon positions.",
            "filename": "nucleon-seeds_197.hdf",
        },
        "output_path": {
            "description": "Output directory where to save",
            "dirname": "nuclei_target",
        },
        "number_of_parallel_processes": {
            "description": "Number of processes to compute in parallel.",
            "value": -1,
        },
    },
    "isobar_properties": {
        "description": "Nuclear properties of isobars to be sampled.",
        "isobar1": {
            "isobar_name": "Au",
            "WS_radius": {"description": "Woods-Saxon radius parameter R", "value": 6.38},
            "WS_diffusiveness": {"description": "Woods-Saxon diffusiveness parameter a", "value": 0.535},
            "beta_2": {"description": "Quadrupolar deformation", "value": 0.0},
            "gamma": {"description": "Quadrupolar deformation angle (rad)", "value": 0.0},
            "beta_3": {"description": "Octupolar deformation", "value": 0.0},
            "correlation_length": {"description": "Short-range correlation length (fm)", "value": 0.4},
            "correlation_strength": {"description": "Short-range correlation strength", "value": 0.0},
        },
    },
}

isobars_conf_dict_projectile = {
    "isobar_samples": {
        "description": "Options for the isobar nucleon-position samples",
        "number_configs": {
            "description": "Number of configurations to be sampled.",
            "value": 1,
        },
        "number_nucleons": {
            "description": "Mass number A of the nuclei.",
            "value": 197,
        },
        "seeds_file": {
            "description": "Input file with list of seeds for nucleon positions.",
            "filename": "nucleon-seeds.hdf",
        },
        "output_path": {
            "description": "Output directory where to save",
            "dirname": "nuclei_projectile",
        },
        "number_of_parallel_processes": {
            "description": "Number of processes to compute in parallel.",
            "value": -1,
        },
    },
    "isobar_properties": {
        "description": "Nuclear properties of isobars to be sampled.",
        "isobar1": {
            "isobar_name": "Au",
            "WS_radius": {"description": "Woods-Saxon radius parameter R", "value": 6.38},
            "WS_diffusiveness": {"description": "Woods-Saxon diffusiveness parameter a", "value": 0.535},
            "beta_2": {"description": "Quadrupolar deformation", "value": 0.0},
            "gamma": {"description": "Quadrupolar deformation angle (rad)", "value": 0.0},
            "beta_3": {"description": "Octupolar deformation", "value": 0.0},
            "correlation_length": {"description": "Short-range correlation length (fm)", "value": 0.4},
            "correlation_strength": {"description": "Short-range correlation strength", "value": 0.0},
        },
    },
}

trento_dict = {
    'type': "self",
    'projectile': ['nuclei_target/Au.hdf', 'nuclei_projectile/Au.hdf'],
    'number-events': 1,
    'quiet': False,
    'output': 'initial_condition',   
    'reduced-thickness': 0.063, ###
    'fluctuation': 1.05 ,      # gamma fluctuations
    'nucleon-width': 1.12,    # nucleon width
    'cross-section': 4.23,   # inelastic nucleon-nucleon cross-section
    'normalization': 5.73,      # normalization
    'b-min': 0,              # minimum b
    'b-max': 0,             # maximum b
    'grid-max': 10,          #####
    'grid-step': 0.2,        #####
    'nucleon-min-dist': 1.44, #(2.97)^1/3
}

free_streaming_dict = {
    'tau': 1.46,
    'grid_max': 10.0,
    'grid_step': 0.2,
}

music_dict = {
        'Initial_profile': 92,  # type of initial condition 
    # 13: dynamical initialization (3dMCGlauber_dynamical)
    #   -- 131: 3dMCGlauber with zero nucleus thickness
    's_factor': 1.000,  # normalization factor read in initial data file
    'Initial_time_tau_0':
        1.46,  # starting time of the hydrodynamic evolution (fm/c)
    'Delta_Tau': 0.005,  # time step to use in the evolution [fm/c]
    'boost_invariant': 1,  # whether the simulation is boost-invariant
    'EOS_to_use': 24,  # type of the equation of state
    'EOS_gp_l': 400,  # the l parameter for the Gaussian process emulator of the EOS
    'EOS_gp_sigma': 15,  # the sigma parameter for the Gaussian process emulator of the EOS
    'EOS_gp_type': 'hrg',  # the type of the Gaussian process emulator of the EOS
    'EOS_gp_sample': 's0',  # the sample for the Gaussian process emulator of the EOS
    'gp_type': 'training',
    'T_sw': 136,
    # transport coefficients'
    'Eta_grid_size': 1.0,
    'Grid_size_in_eta': 1.0,
    'X_grid_size_in_fm': 18.0,
    'Y_grid_size_in_fm': 18.0,
    'Grid_size_in_x': 90,  # number of the grid points in x direction
    'Grid_size_in_y': 90, 
    'quest_revert_strength': 1.0,  # the strength of the viscous regulation
    'Viscosity_Flag_Yes_1_No_0': 1,  # turn on viscosity in the evolution
    'Include_Shear_Visc_Yes_1_No_0': 1,  # include shear viscous effect
    'Shear_to_S_ratio': 0.12,  # value of \eta/s
    #
    'shear_relax_time_factor': 4.65,
    'T_dependent_Shear_to_S_ratio': 3,  # flag to use temperature dep. \eta/s(T)
    'shear_viscosity_3_eta_over_s_T_kink_in_GeV': 0.223,
    'shear_viscosity_3_eta_over_s_low_T_slope_in_GeV': -0.776,
    'shear_viscosity_3_eta_over_s_high_T_slope_in_GeV': 0.37,
    'shear_viscosity_3_eta_over_s_at_kink': 0.096,
    'Include_Bulk_Visc_Yes_1_No_0': 1,  # include bulk viscous effect
    'T_dependent_zeta_over_s': 3,         # parameterization of \zeta/s(T)
    'bulk_viscosity_3_zeta_over_s_max': 0.133,
    'bulk_viscosity_3_zeta_over_s_T_peak_in_GeV': 0.12,
    'bulk_viscosity_3_zeta_over_s_width_in_GeV': 0.072,
    'bulk_viscosity_3_zeta_over_s_lambda_asymm': -0.122,
    'Include_second_order_terms':
        1,  # include second order non-linear coupling terms
    'Include_vorticity_terms': 0,  # include vorticity coupling terms
    # parameters for freeze out and Cooper-Frye
    'N_freeze_out': 1,
    'eps_freeze_max': 0.13,
    'eps_freeze_min': 0.13,
}

iss_dict = {
    'hydro_mode': 2,
    'include_deltaf_shear': 1,
    'include_deltaf_bulk': 1,
    'bulk_deltaf_kind': 1,
    'include_deltaf_diffusion': 0,
    'local_charge_conservation': 0,
    'global_momentum_conservation': 0,
    'output_samples_into_files': 1,
    'store_samples_in_memory': 0,
    'sample_upto_desired_particle_number': 0,
    'number_of_particles_needed': 1000000,
    'number_of_repeated_sampling': 500,
}

hadronic_afterburner_toolkit_dict = {
    'event_buffer_size': 100000,
    'compute_correlation': 0,
    'flag_charge_dependence': 0,
    'compute_corr_rap_dep': 0,
    'resonance_weak_feed_down_flag': 0,
    #'analyze_HBT': 0,
    #'rapidityPTDistributionFlag': 1,  # output Qn vectors in (eta, pT)
    #'pidwithRapidityPTDistribution': 1,
}
