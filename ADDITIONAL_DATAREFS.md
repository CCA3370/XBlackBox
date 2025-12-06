# Additional Datarefs Analysis

This document analyzes the comprehensive datarefs.json file from X-Plane SDK to identify additional useful parameters that could enhance the XBlackBox recording capabilities.

## Currently Implemented Datarefs

The current implementation includes approximately:
- **Simple Level**: ~25 datarefs (basic flight data)
- **Normal Level**: +45 datarefs (controls, engines, systems)
- **Detailed Level**: +110 datarefs (autopilot, environment, warnings, etc.)

**Total: ~180 datarefs**

## Suggested Additional Datarefs for Enhanced Recording

### High Priority Additions

#### Cockpit Switches and Controls (for detailed analysis)
```
sim/cockpit2/switches/battery_on[8]           // Battery switches
sim/cockpit2/switches/avionics_power_on       // Avionics master
sim/cockpit2/switches/landing_lights_on       // Landing lights
sim/cockpit2/switches/beacon_on               // Beacon light
sim/cockpit2/switches/strobe_lights_on        // Strobe lights
sim/cockpit2/switches/nav_lights_on           // Nav lights
```

#### TCAS and Traffic
```
sim/cockpit2/tcas/targets/position/x[64]      // Traffic X position
sim/cockpit2/tcas/targets/position/y[64]      // Traffic Y position
sim/cockpit2/tcas/targets/position/altitude[64] // Traffic altitude
sim/cockpit2/tcas/targets/modeS_id[64]        // Traffic Mode S ID
```

#### Weather and Visibility
```
sim/weather/visibility_reported_m              // Visibility
sim/weather/cloud_base_msl_m[3]               // Cloud base heights
sim/weather/cloud_coverage[3]                 // Cloud coverage
sim/weather/temperature_altitude_c[13]        // Temperature at altitudes
sim/weather/dewpoint_altitude_c[13]           // Dewpoint at altitudes
```

#### Performance Metrics
```
sim/flightmodel/position/Qrad                 // Dynamic pressure
sim/flightmodel/position/Pstatic             // Static pressure
sim/flightmodel/position/local_vx            // Local velocity X
sim/flightmodel/position/local_vy            // Local velocity Y
sim/flightmodel/position/local_vz            // Local velocity Z
sim/flightmodel/position/mag_psi             // Magnetic heading
```

#### Flight Management System (FMS)
```
sim/cockpit2/autopilot/fms_vnav              // VNAV mode
sim/cockpit2/autopilot/approach_status       // Approach status
sim/cockpit2/autopilot/nav1_coupling         // NAV1 coupling
sim/cockpit2/autopilot/gps_coupling          // GPS coupling
```

#### Failures and Malfunctions
```
sim/operation/failures/rel_servo_ailn        // Aileron servo failure
sim/operation/failures/rel_servo_elev        // Elevator servo failure
sim/operation/failures/rel_servo_rudd        // Rudder servo failure
sim/operation/failures/rel_ss_dgy            // Directional gyro failure
sim/operation/failures/rel_ss_ahz            // Attitude gyro failure
sim/operation/failures/rel_ss_asi            // Airspeed indicator failure
sim/operation/failures/rel_ss_alt            // Altimeter failure
```

#### Engine Extended Parameters (for turboprops/jets)
```
sim/flightmodel2/engines/thrust_reverser_deploy_ratio[8]  // Reverser position
sim/flightmodel2/engines/engine_is_burning_fuel[8]        // Fuel burn status
sim/flightmodel2/engines/fuel_flow_kg_sec[8]              // Fuel flow kg/s
sim/flightmodel2/engines/nacelle_temp_c[8]                // Nacelle temp
```

### Medium Priority Additions

#### Audio Panel
```
sim/cockpit2/radios/actuators/audio_selection_com1  // COM1 audio
sim/cockpit2/radios/actuators/audio_selection_com2  // COM2 audio
sim/cockpit2/radios/actuators/audio_selection_nav1  // NAV1 audio
sim/cockpit2/radios/actuators/audio_selection_nav2  // NAV2 audio
```

#### Trim Settings
```
sim/cockpit2/controls/elevator_trim           // Elevator trim
sim/cockpit2/controls/aileron_trim            // Aileron trim
sim/cockpit2/controls/rudder_trim             // Rudder trim
```

#### Pressurization (for detailed cabin analysis)
```
sim/cockpit2/pressurization/actuators/safety_valve  // Safety valve
sim/cockpit2/pressurization/actuators/dump_all      // Dump valve
```

#### GPS Navigation
```
sim/cockpit2/radios/actuators/gps_desired_course    // GPS course
sim/cockpit2/radios/indicators/gps_hdef_dots        // GPS HDEF
sim/cockpit2/radios/indicators/gps_vdef_dots        // GPS VDEF
sim/cockpit2/radios/indicators/gps_dme_distance_nm  // GPS distance
```

### Low Priority but Useful

#### Payload and CG
```
sim/flightmodel/weight/m_fixed                // Fixed weight
sim/flightmodel/weight/m_jettison             // Jettisoned weight
sim/flightmodel/misc/cgz_ref_to_default       // CG position
```

#### Replay/Multiplayer Info
```
sim/time/is_in_replay                         // In replay mode
sim/network/misc/network_time_sec             // Network time
```

## Implementation Strategy

To add these datarefs to XBlackBox:

1. **Create Level 4 (Extended)**:
   - Add a new recording level beyond "Detailed"
   - Include all high-priority additions
   - Estimated total: ~250-300 datarefs

2. **Selective Recording**:
   - Allow users to create custom dataref lists
   - Load custom datarefs from a configuration file
   - Would require UI changes

3. **Aircraft-Specific Profiles**:
   - Different dataref sets for different aircraft types
   - Light aircraft vs. airliners vs. helicopters
   - Automatically detect and load appropriate profile

## Performance Considerations

Adding more datarefs increases:
- File size (linearly with number of datarefs)
- Processing overhead (minimal with efficient C++ implementation)
- Memory usage (pre-allocated buffers)

Estimated impact for Level 4 (300 datarefs):
- At 4 Hz: ~6 KB/sec, ~21 MB/hour
- At 20 Hz: ~30 KB/sec, ~105 MB/hour

These are acceptable for modern storage systems.

## Recommended Implementation

For the current implementation, I recommend:
1. **Keep current 3 levels** as they provide good coverage
2. **Document the architecture** for users to add custom datarefs
3. **Consider Level 4** in future versions with user feedback
4. **Prioritize most-requested datarefs** based on community input

The current ~180 datarefs provide excellent coverage for:
- Flight analysis and replay
- Accident investigation
- Training and evaluation
- Performance monitoring
- System troubleshooting

Additional datarefs should be added based on specific use cases and user requirements.
