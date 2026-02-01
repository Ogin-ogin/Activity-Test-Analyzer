"""
Sigmoid fitting module for benzene oxidation activity analysis
"""
import numpy as np
from scipy.optimize import curve_fit
from typing import Tuple, Dict, Optional


def sigmoid_function(T: np.ndarray, a: float, b: float, c: float, d: float) -> np.ndarray:
    """
    4-parameter sigmoid function (legacy, kept for compatibility)

    Args:
        T: Temperature
        a: Maximum conversion (upper limit)
        b: Growth rate (steepness of curve)
        c: Inflection point temperature
        d: Minimum conversion (lower limit)

    Returns:
        Conversion values
    """
    return d + (a - d) / (1 + np.exp(-b * (T - c)))


def sigmoid_constrained(T: np.ndarray, b: float, c: float) -> np.ndarray:
    """
    2-parameter sigmoid function with fixed asymptotes (0% at -∞, 100% at +∞)

    Args:
        T: Temperature
        b: Growth rate (steepness of curve)
        c: Inflection point temperature (T50)

    Returns:
        Conversion values (0-100%)

    At T → -∞: returns 0%
    At T → +∞: returns 100%
    At T = c: returns 50%
    """
    return 100.0 / (1 + np.exp(-b * (T - c)))


def calculate_tx(params: np.ndarray, target_conversion: float) -> Optional[float]:
    """
    Calculate temperature for target conversion rate (legacy 4-param version)

    Args:
        params: Fitting parameters [a, b, c, d]
        target_conversion: Target conversion rate (%)

    Returns:
        Temperature (TX) or None if out of range
    """
    a, b, c, d = params

    if target_conversion <= d:
        return None  # Below lower limit
    if target_conversion >= a:
        return None  # Above upper limit

    # Inverse sigmoid function
    tx = c - (1/b) * np.log((a - d)/(target_conversion - d) - 1)
    return tx


def calculate_tx_constrained(b: float, c: float, target_conversion: float) -> Optional[float]:
    """
    Calculate temperature for target conversion rate (constrained sigmoid)

    Args:
        b: Growth rate
        c: Inflection point (T50)
        target_conversion: Target conversion rate (%)

    Returns:
        Temperature (TX) or None if out of range
    """
    # With fixed asymptotes: a=100, d=0
    if target_conversion <= 0:
        return None  # Below lower limit
    if target_conversion >= 100:
        return None  # Above upper limit

    # Inverse sigmoid function: T = c - (1/b) * ln(100/x - 1)
    tx = c - (1/b) * np.log(100.0/target_conversion - 1)
    return tx


class SigmoidFitter:
    """Sigmoid fitting for activity data with constrained asymptotes (0% to 100%)"""

    def __init__(self):
        self.popt = None  # [b, c] for constrained sigmoid
        self.pcov = None
        self.r_squared = None
        self.temperatures = None
        self.conversions = None

    def fit(self, temperatures: np.ndarray, conversions: np.ndarray) -> bool:
        """
        Perform constrained sigmoid fitting (0% at -∞, 100% at +∞)

        Args:
            temperatures: Temperature data
            conversions: Conversion data

        Returns:
            True if fitting succeeded, False otherwise
        """
        self.temperatures = np.array(temperatures)
        self.conversions = np.array(conversions)

        # Estimate initial parameters for constrained sigmoid
        # c_init: temperature at ~50% conversion
        mid_conv = 50.0
        c_init = self.temperatures[
            np.argmin(np.abs(self.conversions - mid_conv))
        ]
        b_init = 0.05  # Initial growth rate

        initial_guess = [b_init, c_init]

        try:
            # Perform curve fitting with constrained sigmoid
            self.popt, self.pcov = curve_fit(
                sigmoid_constrained,
                self.temperatures,
                self.conversions,
                p0=initial_guess,
                maxfev=5000,
                bounds=([0.001, -np.inf], [np.inf, np.inf])  # b must be positive
            )

            # Calculate R²
            y_pred = sigmoid_constrained(self.temperatures, *self.popt)
            ss_res = np.sum((self.conversions - y_pred) ** 2)
            ss_tot = np.sum((self.conversions - np.mean(self.conversions)) ** 2)
            self.r_squared = 1 - (ss_res / ss_tot)

            return True

        except Exception as e:
            print(f"Fitting error: {e}")
            return False

    def get_fitting_params(self) -> Optional[Dict[str, float]]:
        """
        Get fitting parameters

        Returns:
            Dictionary with parameter names and values, or None if not fitted
        """
        if self.popt is None:
            return None

        # Return parameters with fixed asymptotes for display
        return {
            'a_max_conversion': 100.0,  # Fixed upper asymptote
            'b_growth_rate': self.popt[0],
            'c_inflection_temp': self.popt[1],  # Also equals T50
            'd_min_conversion': 0.0,  # Fixed lower asymptote
            'r_squared': self.r_squared
        }

    def calculate_tx_values(self, target_conversions: list) -> Dict[str, Optional[float]]:
        """
        Calculate TX values for target conversions

        Args:
            target_conversions: List of target conversion rates (%)

        Returns:
            Dictionary with TX names and temperatures
        """
        if self.popt is None:
            return {}

        b, c = self.popt
        tx_results = {}
        for target in target_conversions:
            tx = calculate_tx_constrained(b, c, target)
            tx_results[f"T{int(target)}"] = tx

        return tx_results

    def get_fitted_curve(self, temp_range: Optional[Tuple[float, float]] = None,
                        num_points: int = 300) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get fitted curve data for plotting

        Args:
            temp_range: (min_temp, max_temp) or None to auto-calculate
            num_points: Number of points for smooth curve

        Returns:
            Tuple of (temperatures, conversions) for fitted curve
        """
        if self.popt is None:
            return np.array([]), np.array([])

        if temp_range is None:
            temp_min = self.temperatures.min() - 20
            temp_max = self.temperatures.max() + 20
        else:
            temp_min, temp_max = temp_range

        temp_fit = np.linspace(temp_min, temp_max, num_points)
        conv_fit = sigmoid_constrained(temp_fit, *self.popt)

        return temp_fit, conv_fit
