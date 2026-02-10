"""
Settings management module for temperature step protocols
"""
import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class TemperatureStep:
    """Single temperature step configuration"""
    temperature: float  # Temperature in °C
    hold_time: int  # Hold time in minutes
    reactor_id: int = 1  # Reactor ID (1-based, default 1 for standard mode)


@dataclass
class CalibrationSettings:
    """Calibration curve settings"""
    name: str
    slope: float  # Slope for intensity to conversion
    intercept: float  # Intercept (used only in no-correction mode)


@dataclass
class ProtocolSettings:
    """Complete protocol settings"""
    name: str
    steps: List[TemperatureStep]
    ramp_time: int  # Time to move between steps in minutes
    analysis_time: int  # Time window to use for analysis in minutes (from end of hold time)
    mode: str = "standard"  # "standard" or "semi_auto"
    num_reactors: int = 1  # Number of reactors (1 for standard, 2+ for semi-auto)


class SettingsManager:
    """Manage protocol settings files"""

    def __init__(self, settings_dir: str = "settings"):
        """
        Initialize settings manager

        Args:
            settings_dir: Directory for settings files (relative to app root)
        """
        # Use relative path from the app root
        self.settings_dir = settings_dir
        self._ensure_settings_dir()
        self._create_default_settings()
        self._create_default_calibration()

    def _ensure_settings_dir(self):
        """Create settings directory if it doesn't exist"""
        if not os.path.exists(self.settings_dir):
            os.makedirs(self.settings_dir, exist_ok=True)

    def _create_default_settings(self):
        """Create default settings file if it doesn't exist"""
        default_path = os.path.join(self.settings_dir, "default.json")

        if not os.path.exists(default_path):
            default_settings = ProtocolSettings(
                name="Standard Protocol (500-150°C)",
                steps=[
                    TemperatureStep(500, 20),
                    TemperatureStep(450, 20),
                    TemperatureStep(400, 20),
                    TemperatureStep(350, 20),
                    TemperatureStep(300, 20),
                    TemperatureStep(250, 20),
                    TemperatureStep(200, 20),
                    TemperatureStep(150, 20),
                ],
                ramp_time=10,
                analysis_time=10
            )
            self.save_settings(default_settings, "default.json")

    def save_settings(self, settings: ProtocolSettings, filename: str) -> str:
        """
        Save settings to JSON file

        Args:
            settings: ProtocolSettings object
            filename: Filename (with .json extension)

        Returns:
            Full path to saved file
        """
        filepath = os.path.join(self.settings_dir, filename)

        # Convert to dictionary
        settings_dict = {
            "name": settings.name,
            "steps": [asdict(step) for step in settings.steps],
            "ramp_time": settings.ramp_time,
            "analysis_time": settings.analysis_time,
            "mode": settings.mode,
            "num_reactors": settings.num_reactors
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(settings_dict, f, indent=2, ensure_ascii=False)

        return filepath

    def load_settings(self, filename: str) -> Optional[ProtocolSettings]:
        """
        Load settings from JSON file

        Args:
            filename: Filename (with .json extension)

        Returns:
            ProtocolSettings object or None if file doesn't exist
        """
        filepath = os.path.join(self.settings_dir, filename)

        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle backward compatibility for steps without reactor_id
            steps = []
            for step_data in data['steps']:
                if 'reactor_id' not in step_data:
                    step_data['reactor_id'] = 1  # Default to reactor 1
                steps.append(TemperatureStep(**step_data))

            settings = ProtocolSettings(
                name=data['name'],
                steps=steps,
                ramp_time=data['ramp_time'],
                analysis_time=data['analysis_time'],
                mode=data.get('mode', 'standard'),  # Default to standard for old files
                num_reactors=data.get('num_reactors', 1)  # Default to 1 for old files
            )

            return settings

        except Exception as e:
            print(f"Error loading settings: {e}")
            return None

    def list_settings_files(self) -> List[str]:
        """
        Get list of available settings files

        Returns:
            List of filenames (without path)
        """
        if not os.path.exists(self.settings_dir):
            return []

        files = [f for f in os.listdir(self.settings_dir) if f.endswith('.json')]
        return sorted(files)

    def delete_settings(self, filename: str) -> bool:
        """
        Delete a settings file

        Args:
            filename: Filename (with .json extension)

        Returns:
            True if successful, False otherwise
        """
        filepath = os.path.join(self.settings_dir, filename)

        if os.path.exists(filepath) and filename != "default.json":
            try:
                os.remove(filepath)
                return True
            except Exception as e:
                print(f"Error deleting settings: {e}")
                return False
        return False

    def get_default_settings(self) -> ProtocolSettings:
        """
        Get default settings

        Returns:
            Default ProtocolSettings object
        """
        settings = self.load_settings("default.json")
        if settings is None:
            # If default doesn't exist, recreate it
            self._create_default_settings()
            settings = self.load_settings("default.json")
        return settings

    # --- Calibration curve management ---

    def _ensure_calibration_dir(self):
        """Create calibration directory if it doesn't exist"""
        cal_dir = os.path.join(self.settings_dir, "calibrations")
        if not os.path.exists(cal_dir):
            os.makedirs(cal_dir, exist_ok=True)
        return cal_dir

    def _create_default_calibration(self):
        """Create default calibration if it doesn't exist"""
        cal_dir = self._ensure_calibration_dir()
        default_path = os.path.join(cal_dir, "default.json")
        if not os.path.exists(default_path):
            default_cal = CalibrationSettings(
                name="Default",
                slope=-995.32,
                intercept=101.36
            )
            self.save_calibration(default_cal, "default.json")

    def save_calibration(self, cal: CalibrationSettings, filename: str) -> str:
        """Save calibration settings to JSON file"""
        cal_dir = self._ensure_calibration_dir()
        filepath = os.path.join(cal_dir, filename)
        cal_dict = {"name": cal.name, "slope": cal.slope, "intercept": cal.intercept}
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cal_dict, f, indent=2, ensure_ascii=False)
        return filepath

    def load_calibration(self, filename: str) -> Optional[CalibrationSettings]:
        """Load calibration settings from JSON file"""
        cal_dir = self._ensure_calibration_dir()
        filepath = os.path.join(cal_dir, filename)
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return CalibrationSettings(
                name=data['name'],
                slope=data['slope'],
                intercept=data.get('intercept', 0.0)
            )
        except Exception as e:
            print(f"Error loading calibration: {e}")
            return None

    def list_calibration_files(self) -> List[str]:
        """Get list of available calibration files"""
        cal_dir = self._ensure_calibration_dir()
        files = [f for f in os.listdir(cal_dir) if f.endswith('.json')]
        return sorted(files)

    def delete_calibration(self, filename: str) -> bool:
        """Delete a calibration file (cannot delete default)"""
        cal_dir = self._ensure_calibration_dir()
        filepath = os.path.join(cal_dir, filename)
        if os.path.exists(filepath) and filename != "default.json":
            try:
                os.remove(filepath)
                return True
            except Exception:
                return False
        return False

    def save_user_preferences(self, preferences: Dict) -> str:
        """
        Save user preferences (paths, etc.)

        Args:
            preferences: Dictionary with user preferences

        Returns:
            Full path to saved file
        """
        filepath = os.path.join(self.settings_dir, "user_preferences.json")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(preferences, f, indent=2, ensure_ascii=False)

        return filepath

    def load_user_preferences(self) -> Optional[Dict]:
        """
        Load user preferences

        Returns:
            Dictionary with user preferences or None if file doesn't exist
        """
        filepath = os.path.join(self.settings_dir, "user_preferences.json")

        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                preferences = json.load(f)
            return preferences
        except Exception as e:
            print(f"Error loading user preferences: {e}")
            return None
