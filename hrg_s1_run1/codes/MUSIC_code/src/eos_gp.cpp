// Copyright 2018 @ Chun Shen

#include "eos_gp.h"
#include "util.h"

#include <sstream>
#include <fstream>
#include <cmath>
#include <gsl/gsl_spline.h>
#include <gsl/gsl_interp.h>

using std::stringstream;
using std::string;

EOS_gp::EOS_gp(const int eos_id_in) : eos_id(eos_id_in) {
    set_EOS_id(eos_id);
    set_number_of_tables(0);
    set_eps_max(1e5);
    set_flag_muB(false);
    set_flag_muS(false);
    set_flag_muQ(false);
}


void EOS_gp::initialize_eos() {
    // read the lattice EOS pressure, temperature, and 
    music_message.info("reading EOS_gp");
    
    auto envPath = get_hydro_env_path();
    music_message << "from path " << envPath.c_str() << "/EOS/EOS-gp";
    music_message.flush("info");
    
    set_number_of_tables(1);
    resize_table_info_arrays();

    int ntables = get_number_of_tables();

    //string eos_file_string_array[2] = {"1"};
    pressure_tb    = new double** [ntables];
    temperature_tb = new double** [ntables];
    cs2_tb = new double** [ntables];
    entropy_tb = new double** [ntables];
    energy_tb = new double** [ntables];

    for (int itable = 0; itable < ntables; itable++) {

        int l = 400;
        int sigma = 15;
        std::string eos_type = "hrg";
        std::string sample = "s0";

    	std::string base = envPath + "/EOS/EOS-gp/constrained";

        std::ostringstream path;
        path << base << "/l" << l << "_s" << sigma << "/eos_" << eos_type << "_" 
        << sample << "_l" << l << "_s" << sigma << ".dat";

        std::string EOS_FILE = path.str();

        std::ifstream eos_file(EOS_FILE);

        if (!eos_file.is_open()) {
        music_message << "ERROR: Could not open EOS file: " << EOS_FILE << "\n";
        exit(1);
        }

        music_message << "file from path " << EOS_FILE << "\n";


        //fixed baryon number/density -> not a grid in energy and density  
        nb_length[itable] = 1;
        
        //reads first line with number of energy points
        eos_file >> e_length[itable];
        music_message << "e_length[itable] " << e_length[itable];
        music_message.flush("info");

        // skip the header in the file        
        string dummy;
        std::getline(eos_file, dummy);
        
        // read pressure, temperature and chemical potential values from the file and store it in each array
        
        // allocate memory for EOS arrays
        //mtx_malloc allocates and initializes a matrix of size nb_length x e_length
        pressure_tb[itable] = Util::mtx_malloc(nb_length[itable],
                                               e_length[itable]);
                                               
        temperature_tb[itable] = Util::mtx_malloc(nb_length[itable],
                                                  e_length[itable]);
                                                  
        cs2_tb[itable] = Util::mtx_malloc(nb_length[itable],
                                           e_length[itable]);
                                           
        entropy_tb[itable] = Util::mtx_malloc(nb_length[itable],
                                           e_length[itable]);
                                           
        energy_tb[itable] = Util::mtx_malloc(nb_length[itable],
                                           e_length[itable]);
        
            
        string line;
        
        for (int ii = 0; ii < e_length[itable]; ii++) {

            getline(eos_file, line);
            std::istringstream iss(line);
            double energy, temperature, pressure, cs2, entropy;
            
            if (!(iss >> energy >> temperature >> pressure >> cs2 >> entropy)) {
        	music_message << "Error parsing line " << ii << ": " << line;
        	music_message.flush("info");
        	break;
            }

            
            temperature_tb[itable][0][ii] = temperature/ Util::hbarc;    // 1/fm

            pressure_tb[itable][0][ii] = pressure/ Util::hbarc; // 1/fm^4
            
            cs2_tb[itable][0][ii] = cs2; //dimensionless
            
            entropy_tb[itable][0][ii] = entropy; //1/fm^3
            
            energy_tb[itable][0][ii] = energy/ Util::hbarc; // 1/fm^4
            
        }
        
    }

    music_message.info("Done reading EOS.");
}


// Interpolations

double EOS_gp::p_e_func(double e, double rhob) const {
    return(get_dpOverde3(e, rhob));
}

void EOS_gp::get_pressure_with_gradients(
    double epsilon, double rhob, double &p, double &dpde, double &dpdrhob,
    double &cs2) const {
    // For EOS_gp, we have tabulated cs2 and can compute dpde from it
    // This avoids numerical differentiation issues that can occur in MaxSpeed
    p = get_pressure(epsilon, rhob);
    cs2 = get_cs2(epsilon, rhob);
    dpde = p_e_func(epsilon, rhob);
    
    // For zero rhob EOS (which EOS_gp uses), dpdrhob = 0
    // but we compute it for consistency with the base class signature
    dpdrhob = 0.0;  // EOS_gp is independent of rhob
}

//! This function returns the local temperature in [1/fm]
//! input local energy density eps [1/fm^4] and rhob [1/fm^3]
double EOS_gp::get_temperature(double e, double rhob) const {
    //double T = interpolate_spline(e, 0, temperature_spline_cache, 
    //                              temperature_accel_cache, temperature_tb);
    double T = interpolate1D_nonuniform(e, 0, energy_tb, temperature_tb, 7000.);
    return(std::max(Util::small_eps, T));
}

//! This function returns the local pressure in [1/fm^4]
//! the input local energy density [1/fm^4], rhob [1/fm^3]
double EOS_gp::get_pressure(double e, double rhob) const {
    double f = interpolate1D_nonuniform(e, 0, energy_tb, pressure_tb, 200/Util::hbarc);
    return(std::max(Util::small_eps, f));
}

double EOS_gp::get_cs2(double e, double rhob) const {
    double f = interpolate1D_nonuniform(e, 0, energy_tb, cs2_tb, 0.333);
    return(std::max(Util::small_eps, f));
}

double EOS_gp::get_entropy(double e, double rhob) const {
    double f = interpolate1D_nonuniform(e, 0, energy_tb, entropy_tb, 1000.);
    return(std::max(Util::small_eps, f));
}

double EOS_gp::get_s2e(double s, double rhob) const {
    double e = get_s2e_finite_rhob(s, 0.0);
    return(e);
}

double EOS_gp::get_T2e(double T_in_GeV, double rhob) const {
    double e = get_T2e_finite_rhob(T_in_GeV, 0.0);
    return(e);
}

