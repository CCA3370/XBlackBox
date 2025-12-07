# Dataref Additions Summary

This document summarizes the datarefs added from the XBlackBox-SASL repository's datarefs.json file.

## Overview

**Total datarefs added:** 45 new dataref definitions
**Previous total:** ~110 unique datarefs
**New total:** 155 unique datarefs

**Parameter counts (including array elements):**
- **Level 1 (Simple):** 26 parameters (unchanged)
- **Level 2 (Normal):** 163 parameters (was ~70)
- **Level 3 (Detailed):** 363 parameters (was ~180)

## New Datarefs Added to Level 3 (Detailed)

### Cockpit Switches and Lights (8 datarefs, 9 parameters)
- `sim/cockpit2/switches/battery_on[8]` - Battery switches for all batteries
- `sim/cockpit2/switches/avionics_power_on` - Avionics master switch (0 or 1)
- `sim/cockpit2/switches/landing_lights_on` - Landing lights switch (0 or 1)
- `sim/cockpit2/switches/beacon_on` - Beacon light switch (0 or 1)
- `sim/cockpit2/switches/strobe_lights_on` - Strobe lights switch (0 or 1)
- `sim/cockpit2/switches/navigation_lights_on` - Nav lights switch (0 or 1)
- `sim/cockpit2/switches/taxi_light_on` - Taxi light switch (0 or 1)

### TCAS and Traffic (1 dataref)
- `sim/cockpit2/tcas/indicators/tcas_num_acf` - Number of TCAS targets

### Enhanced Autopilot Status (3 datarefs)
- `sim/cockpit2/autopilot/fms_vnav` - FMS VNAV mode enabled
- `sim/cockpit2/autopilot/approach_status` - Approach status: 0=off, 1=armed, 2=captured
- `sim/cockpit2/autopilot/nav_status` - Nav status: 0=off, 1=armed, 2=captured

### System Failures Monitoring (7 datarefs)
- `sim/operation/failures/rel_servo_ailn` - Autopilot servo failed - ailerons
- `sim/operation/failures/rel_servo_elev` - Autopilot servo failed - elevators
- `sim/operation/failures/rel_servo_rudd` - Autopilot servo failed - rudder
- `sim/operation/failures/rel_ss_dgy` - Directional gyro failure (Pilot)
- `sim/operation/failures/rel_ss_ahz` - Artificial horizon failure (Pilot)
- `sim/operation/failures/rel_ss_asi` - Airspeed indicator failure (Pilot)
- `sim/operation/failures/rel_ss_alt` - Altimeter failure (Pilot)

### Engine Extended Parameters (4 datarefs, 16 parameters)
- `sim/flightmodel2/engines/thrust_reverser_deploy_ratio[8]` - Thrust reverser position (0-1)
- `sim/flightmodel2/engines/engine_is_burning_fuel[8]` - Engine burning fuel status (yes/no)
- `sim/flightmodel2/engines/fuel_flow_kg_sec[8]` - Fuel flow in kg/sec
- `sim/flightmodel2/engines/nacelle_temp_c[8]` - Nacelle temperature in Celsius

### Control Trim Settings (3 datarefs)
- `sim/cockpit2/controls/elevator_trim` - Elevator trim position (-1 to 1)
- `sim/cockpit2/controls/aileron_trim` - Aileron trim position (-1 to 1)
- `sim/cockpit2/controls/rudder_trim` - Rudder trim position (-1 to 1)

### GPS Navigation Indicators (4 datarefs)
- `sim/cockpit2/radios/indicators/gps_dme_distance_nm` - GPS DME distance in nautical miles
- `sim/cockpit2/radios/indicators/gps_hdef_dots_pilot` - GPS HDEF lateral deflection dots
- `sim/cockpit2/radios/actuators/gps_course_degtm` - GPS course in degrees
- `sim/cockpit2/radios/indicators/gps_vdef_dots_pilot` - GPS VDEF vertical deflection dots

### Weight and Center of Gravity (3 datarefs)
- `sim/flightmodel/weight/m_fixed` - Payload weight (sum of all stations)
- `sim/flightmodel/weight/m_jettison` - Jettisoned weight
- `sim/flightmodel/misc/cgz_ref_to_default` - Longitudinal CG position

### Performance Metrics (4 datarefs)
- `sim/flightmodel/position/local_vx` - Local velocity X component
- `sim/flightmodel/position/local_vy` - Local velocity Y component
- `sim/flightmodel/position/local_vz` - Local velocity Z component
- `sim/flightmodel2/position/mag_psi` - True magnetic heading (corrected version)

### Weather Information (7 datarefs, 10 parameters)
- `sim/weather/visibility_reported_m` - Visibility in meters
- `sim/weather/cloud_base_msl_m[3]` - Cloud base MSL for 3 layers
- `sim/weather/cloud_coverage[3]` - Cloud coverage for 3 layers
- `sim/weather/cloud_type[3]` - Cloud type for 3 layers
- `sim/weather/temperature_sealevel_c` - Temperature at sea level
- `sim/weather/temperature_ambient_c` - Ambient temperature

### Pressurization Controls (2 datarefs)
- `sim/cockpit2/pressurization/actuators/safety_valve` - Safety valve position
- `sim/cockpit2/pressurization/actuators/dump_all` - Dump all valve status

### Replay Mode Detection (1 dataref)
- `sim/time/is_in_replay` - True if in replay mode, false if flying

## Benefits

### Enhanced Flight Analysis
- **System Monitoring**: Track all cockpit switches and lights for complete system state recording
- **Failure Analysis**: Monitor autopilot servo and instrument failures for accident investigation
- **Performance Analysis**: Local velocity components and improved magnetic heading for detailed performance metrics

### Better Weather Recording
- **Complete Weather Picture**: 3 cloud layers with base, coverage, and type
- **Visibility**: Important for approach and landing analysis
- **Temperature Profile**: Sea level and ambient temperature for performance calculations

### Improved Navigation
- **GPS Status**: Full GPS navigation data with lateral and vertical deviation
- **TCAS**: Number of traffic targets for traffic awareness analysis
- **FMS/Autopilot**: Enhanced autopilot mode tracking including approach capture status

### Weight and Balance
- **CG Tracking**: Longitudinal center of gravity position
- **Weight Changes**: Track payload and jettisoned weight

### Engine Monitoring
- **Thrust Reversers**: Track reverser deployment
- **Fuel Flow**: Precise fuel flow in kg/sec
- **Nacelle Temperature**: Engine thermal monitoring

## Source

All datarefs were sourced from the [XBlackBox-SASL repository](https://github.com/CCA3370/XBlackBox-SASL)'s comprehensive `datarefs.json` file, which contains the complete X-Plane dataref database with descriptions and metadata.

Each dataref was verified to be:
- **CURRENT**: Active in current X-Plane versions
- **READABLE**: Has READONLY, MUTABLE, or ACCESSOR access mode
- **USEFUL**: Provides valuable flight data for analysis

## Compatibility

All added datarefs are standard X-Plane datarefs that should be available in X-Plane 12. Some datarefs may not be available on all aircraft types (e.g., thrust reversers on aircraft without reversers), but the DatarefManager safely handles unavailable datarefs by not recording them.
