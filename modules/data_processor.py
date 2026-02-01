"""
Data processing module for benzene oxidation activity analysis
"""
import numpy as np
import pandas as pd
from typing import Tuple, Dict, List, Optional


class BenzeneDataProcessor:
    """Process benzene oxidation activity test data from FT-IR measurements"""

    def __init__(self, conversion_slope=-995.32, conversion_intercept=101.36,
                 protocol_settings=None, auto_intercept=True):
        """
        Initialize data processor

        Args:
            conversion_slope: Slope for intensity to conversion calculation
            conversion_intercept: Intercept for intensity to conversion calculation
            Formula: Conversion [%] = slope * Intensity + intercept
            protocol_settings: ProtocolSettings object (optional, uses default if None)
            auto_intercept: If True, auto-calculate intercept so max intensity = 0% conversion
        """
        self.conversion_slope = conversion_slope
        self.conversion_intercept = conversion_intercept
        self.auto_intercept = auto_intercept

        # Load protocol settings
        if protocol_settings is not None:
            self.set_protocol(protocol_settings)
        else:
            # Default protocol
            self.temp_steps = [500, 450, 400, 350, 300, 250, 200, 150]
            self.hold_times = [20 * 60] * 8  # 20 minutes in seconds for each step
            self.reactor_ids = [1] * 8  # All steps use reactor 1 by default
            self.ramp_time = 10 * 60  # 10 minutes in seconds
            self.analysis_time = 10 * 60  # Use only last 10 minutes of hold time
            self.mode = 'standard'
            self.num_reactors = 1

    def set_protocol(self, protocol_settings):
        """
        Set protocol from ProtocolSettings object

        Args:
            protocol_settings: ProtocolSettings object from settings_manager
        """
        self.temp_steps = [step.temperature for step in protocol_settings.steps]
        self.hold_times = [step.hold_time * 60 for step in protocol_settings.steps]  # Convert to seconds
        self.reactor_ids = [step.reactor_id for step in protocol_settings.steps]  # Reactor assignments
        self.ramp_time = protocol_settings.ramp_time * 60  # Convert to seconds
        self.analysis_time = protocol_settings.analysis_time * 60  # Convert to seconds
        self.mode = getattr(protocol_settings, 'mode', 'standard')
        self.num_reactors = getattr(protocol_settings, 'num_reactors', 1)

    def read_asc_file(self, filepath: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Read .asc file from FT-IR measurement

        Args:
            filepath: Path to .asc file

        Returns:
            Tuple of (times, intensities) as numpy arrays
        """
        times = []
        intensities = []
        data_section = False

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()

                # Check if we're in the data section
                if line == '#DATA':
                    data_section = True
                    continue

                # Parse data lines
                if data_section and line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        try:
                            time = float(parts[0])
                            intensity = float(parts[1])
                            times.append(time)
                            intensities.append(intensity)
                        except ValueError:
                            # Skip lines that can't be parsed as floats
                            continue

        return np.array(times), np.array(intensities)

    def detect_temperature_steps(self, times: np.ndarray, intensities: np.ndarray) -> Dict:
        """
        Detect temperature steps based on measurement protocol

        Args:
            times: Time data in seconds
            intensities: Intensity data

        Returns:
            Dictionary with step index as key and data dict as value
            Each data dict contains: 'temperature', 'reactor_id', 'time_start', 'time_end',
            'times', 'intensities', 'avg_intensity', 'data_points'
        """
        temp_data = {}
        start_time = times[0]
        cumulative_time = 0

        for i, temp in enumerate(self.temp_steps):
            hold_time = self.hold_times[i]
            reactor_id = self.reactor_ids[i] if hasattr(self, 'reactor_ids') else 1

            # Calculate time window for this temperature
            # Use only the last analysis_time minutes of hold period (to allow gas equilibration)
            hold_start = start_time + cumulative_time
            analysis_window = min(self.analysis_time, hold_time)  # Use full hold_time if shorter than analysis_time
            step_start = hold_start + (hold_time - analysis_window)  # Start of analysis window
            step_end = hold_start + hold_time  # End of hold period

            # Extract data points within this time window
            mask = (times >= step_start) & (times <= step_end)
            step_times = times[mask]
            step_intensities = intensities[mask]

            if len(step_intensities) > 0:
                avg_intensity = np.mean(step_intensities)

                # Use step index as key to support multiple steps at same temperature
                temp_data[i] = {
                    'temperature': temp,
                    'reactor_id': reactor_id,
                    'time_start': step_start,
                    'time_end': step_end,
                    'times': step_times,
                    'intensities': step_intensities,
                    'avg_intensity': avg_intensity,
                    'data_points': len(step_intensities)
                }

            # Update cumulative time for next step
            # Determine ramp time: if next step has same temperature, no ramp time needed
            if i + 1 < len(self.temp_steps):
                next_temp = self.temp_steps[i + 1]
                if temp == next_temp:
                    # Same temperature, different reactor - no ramp time
                    ramp_for_this_step = 0
                else:
                    # Different temperature - use normal ramp time
                    ramp_for_this_step = self.ramp_time
            else:
                # Last step - no next step
                ramp_for_this_step = 0

            cumulative_time += hold_time + ramp_for_this_step

        return temp_data

    def intensity_to_conversion(self, intensity: float) -> float:
        """
        Convert intensity to conversion rate

        Args:
            intensity: Benzene intensity from FT-IR

        Returns:
            Conversion rate in %
        """
        return self.conversion_slope * intensity + self.conversion_intercept

    def process_file(self, filepath: str) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame, np.ndarray, np.ndarray, Dict]:
        """
        Complete processing pipeline for a data file (standard mode)

        Args:
            filepath: Path to .asc file

        Returns:
            Tuple of (temperatures, conversions, detailed_df, times, intensities, temp_data)
            - temperatures: Array of temperature values
            - conversions: Array of conversion values
            - detailed_df: DataFrame with detailed data for each temperature
            - times: Raw time data
            - intensities: Raw intensity data
            - temp_data: Dictionary with temperature step data
        """
        # Read file
        times, intensities = self.read_asc_file(filepath)

        # Detect temperature steps
        temp_data = self.detect_temperature_steps(times, intensities)

        # Extract temperatures and average intensities first
        temperatures = []
        avg_intensities = []
        data_points_list = []

        for step_idx in sorted(temp_data.keys()):
            step_data = temp_data[step_idx]
            temperatures.append(step_data['temperature'])
            avg_intensity = step_data['avg_intensity']
            avg_intensities.append(avg_intensity)
            data_points_list.append(step_data['data_points'])

        # Auto-calculate intercept if enabled
        if self.auto_intercept and avg_intensities:
            # Find max intensity (corresponds to 0% conversion - no benzene oxidized)
            max_intensity = max(avg_intensities)
            # Calculate intercept so that max_intensity gives 0% conversion
            # 0 = slope * max_intensity + intercept
            # intercept = -slope * max_intensity
            self.conversion_intercept = -self.conversion_slope * max_intensity

        # Calculate conversions with (possibly updated) intercept
        conversions = []
        for avg_intensity in avg_intensities:
            conversion = self.intensity_to_conversion(avg_intensity)
            conversions.append(conversion)

        # Create detailed DataFrame
        detailed_df = pd.DataFrame({
            'Temperature_C': temperatures,
            'Avg_Intensity': avg_intensities,
            'Conversion_%': conversions,
            'Data_Points': data_points_list
        })

        return np.array(temperatures), np.array(conversions), detailed_df, times, intensities, temp_data

    def process_file_semi_auto(self, filepath: str) -> Tuple[Dict[int, Dict], np.ndarray, np.ndarray, Dict]:
        """
        Complete processing pipeline for semi-auto mode (multiple reactors)

        Args:
            filepath: Path to .asc file

        Returns:
            Tuple of (reactor_data, times, intensities, temp_data)
            - reactor_data: Dict[reactor_id: {
                'temperatures': np.array,
                'conversions': np.array,
                'detailed_df': pd.DataFrame
              }]
            - times: Raw time data
            - intensities: Raw intensity data
            - temp_data: Dictionary with all temperature step data
        """
        # Read file
        times, intensities = self.read_asc_file(filepath)

        # Detect temperature steps
        temp_data = self.detect_temperature_steps(times, intensities)

        # Group data by reactor (first pass - collect intensities)
        reactor_data = {}

        for step_idx in sorted(temp_data.keys()):
            step = temp_data[step_idx]
            reactor_id = step['reactor_id']

            if reactor_id not in reactor_data:
                reactor_data[reactor_id] = {
                    'temperatures': [],
                    'avg_intensities': [],
                    'data_points_list': []
                }

            reactor_data[reactor_id]['temperatures'].append(step['temperature'])
            avg_intensity = step['avg_intensity']
            reactor_data[reactor_id]['avg_intensities'].append(avg_intensity)
            reactor_data[reactor_id]['data_points_list'].append(step['data_points'])

        # Calculate conversions for each reactor
        for reactor_id in reactor_data:
            data = reactor_data[reactor_id]

            # Auto-calculate intercept if enabled (per reactor)
            if self.auto_intercept and data['avg_intensities']:
                # Find max intensity for this reactor (corresponds to 0% conversion)
                max_intensity = max(data['avg_intensities'])
                # Calculate intercept so that max_intensity gives 0% conversion
                intercept = -self.conversion_slope * max_intensity
            else:
                intercept = self.conversion_intercept

            # Calculate conversions with appropriate intercept
            conversions = []
            for avg_intensity in data['avg_intensities']:
                conversion = self.conversion_slope * avg_intensity + intercept
                conversions.append(conversion)

            data['conversions'] = conversions

        # Convert lists to arrays and create DataFrames
        for reactor_id in reactor_data:
            data = reactor_data[reactor_id]
            data['temperatures'] = np.array(data['temperatures'])
            data['conversions'] = np.array(data['conversions'])
            data['detailed_df'] = pd.DataFrame({
                'Temperature_C': data['temperatures'],
                'Avg_Intensity': data['avg_intensities'],
                'Conversion_%': data['conversions'],
                'Data_Points': data['data_points_list']
            })
            # Clean up temporary lists
            del data['avg_intensities']
            del data['data_points_list']

        return reactor_data, times, intensities, temp_data


def get_file_list(folder_path: str, extension: str = '.asc') -> List[str]:
    """
    Get list of files with specified extension in a folder

    Args:
        folder_path: Path to folder
        extension: File extension to filter (default: '.asc')

    Returns:
        List of file paths
    """
    import os

    if not os.path.exists(folder_path):
        return []

    files = []
    for file in os.listdir(folder_path):
        if file.endswith(extension):
            files.append(os.path.join(folder_path, file))

    return sorted(files)
