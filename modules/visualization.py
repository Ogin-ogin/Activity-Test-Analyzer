"""
Visualization module for benzene oxidation activity analysis
"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from typing import Dict, Optional, Tuple
import os


def find_japanese_font():
    """Find available Japanese fonts"""
    japanese_fonts = []

    # Windows standard fonts
    windows_fonts = ['Yu Gothic', 'Yu Gothic UI', 'Meiryo', 'Meiryo UI',
                    'MS Gothic', 'MS UI Gothic', 'MS PGothic', 'MS PMincho']

    # Linux/Mac fonts
    unix_fonts = ['Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic',
                 'Noto Sans CJK JP', 'Hiragino Sans', 'Hiragino Kaku Gothic Pro']

    all_fonts = windows_fonts + unix_fonts

    # Get installed fonts
    available_fonts = [f.name for f in fm.fontManager.ttflist]

    # Search for Japanese fonts
    for font in all_fonts:
        if font in available_fonts:
            japanese_fonts.append(font)

    return japanese_fonts


def get_available_fonts():
    """Get list of available fonts for plotting"""
    # Common fonts that should be available
    common_fonts = [
        'Times New Roman',
        'Arial',
        'Helvetica',
        'DejaVu Sans',
        'DejaVu Serif',
        'Calibri',
        'Cambria',
        'Georgia',
        'Verdana'
    ]

    # Add Japanese fonts if available
    japanese_fonts = find_japanese_font()

    # Get all available fonts
    available_fonts = [f.name for f in fm.fontManager.ttflist]

    # Filter to only include fonts that exist
    available = []
    for font in common_fonts:
        if font in available_fonts:
            available.append(font)

    # Add Japanese fonts
    for font in japanese_fonts:
        if font not in available:
            available.append(font)

    # If Times New Roman is not available, add it anyway (it's usually available)
    if 'Times New Roman' not in available:
        available.insert(0, 'Times New Roman')

    return available


def setup_matplotlib_font(font_name='Times New Roman', language='en'):
    """
    Setup matplotlib font with fallback for Japanese characters

    Args:
        font_name: Font name to use for Latin characters
        language: 'ja' for Japanese, 'en' for English
    """
    if language == 'ja':
        # For Japanese, use Japanese font as primary and specified font as fallback
        japanese_fonts = find_japanese_font()
        if japanese_fonts:
            # Set font list with fallback
            plt.rcParams['font.sans-serif'] = [japanese_fonts[0], font_name, 'DejaVu Sans']
            plt.rcParams['font.family'] = 'sans-serif'
        else:
            plt.rcParams['font.family'] = font_name
    else:
        # For English, use the specified font
        plt.rcParams['font.sans-serif'] = [font_name, 'DejaVu Sans', 'Arial']
        plt.rcParams['font.family'] = 'sans-serif'

    plt.rcParams['axes.unicode_minus'] = False


def create_activity_plot(
    temperatures: np.ndarray,
    conversions: np.ndarray,
    temp_fit: np.ndarray,
    conv_fit: np.ndarray,
    tx_results: Dict[str, float],
    r_squared: float,
    language: str = 'ja',
    figsize: Tuple[int, int] = (12, 8),
    font_name: str = 'Times New Roman',
    label_fontsize: int = 14,
    tick_fontsize: int = 12,
    legend_fontsize: int = 12
) -> plt.Figure:
    """
    Create benzene oxidation activity plot

    Args:
        temperatures: Experimental temperature data
        conversions: Experimental conversion data
        temp_fit: Fitted temperature curve
        conv_fit: Fitted conversion curve
        tx_results: Dictionary of TX values (e.g., {'T20': 285.3, 'T50': 305.1})
        r_squared: R² value
        language: 'ja' or 'en'
        figsize: Figure size
        font_name: Font name for the plot
        label_fontsize: Font size for axis labels
        tick_fontsize: Font size for tick labels
        legend_fontsize: Font size for legend

    Returns:
        matplotlib Figure object
    """
    # Setup font with fallback support
    setup_matplotlib_font(font_name, language)

    # Text labels
    if language == 'ja':
        xlabel = '温度 (℃)'
        ylabel = '転換率 (%)'
        exp_data = '実測データ'
        sigmoid_fit = 'シグモイドフィット'
        temp_unit = '℃'
    else:
        xlabel = 'Temperature (°C)'
        ylabel = 'Conversion (%)'
        exp_data = 'Experimental Data'
        sigmoid_fit = 'Sigmoid Fit'
        temp_unit = '°C'

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Plot experimental data
    ax.scatter(temperatures, conversions, color='red', s=80,
              label=exp_data, zorder=5, alpha=0.8)

    # Plot fitted curve
    ax.plot(temp_fit, conv_fit, 'b-', linewidth=2,
           label=f'{sigmoid_fit} (R²={r_squared:.3f})')

    # Plot TX points
    colors = ['green', 'orange', 'purple', 'brown', 'pink', 'cyan', 'magenta']
    for i, (key, tx_temp) in enumerate(sorted(tx_results.items())):
        if tx_temp is not None:
            # Extract target conversion from key (e.g., 'T20' -> 20)
            target = int(key[1:])

            # Plot horizontal and vertical lines
            ax.axhline(y=target, color=colors[i % len(colors)],
                      linestyle='--', alpha=0.5, linewidth=1)
            ax.axvline(x=tx_temp, color=colors[i % len(colors)],
                      linestyle='--', alpha=0.5, linewidth=1)

            # Plot TX point marker
            ax.plot(tx_temp, target, 'o', color=colors[i % len(colors)],
                   markersize=10, label=f'{key}={tx_temp:.1f}{temp_unit}',
                   markeredgecolor='black', markeredgewidth=1)

    # Set labels and grid
    ax.set_xlabel(xlabel, fontsize=label_fontsize)
    ax.set_ylabel(ylabel, fontsize=label_fontsize)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=legend_fontsize, loc='best')

    # Set tick label font size
    ax.tick_params(axis='both', which='major', labelsize=tick_fontsize)

    # Set axis limits
    ax.set_xlim(temperatures.min() - 30, temperatures.max() + 30)

    # Calculate Y-axis limits dynamically based on data
    all_conv_data = np.concatenate([conversions, conv_fit])
    y_min = min(all_conv_data.min(), 0)  # Include 0 if data is all positive
    y_max = max(all_conv_data.max(), 100)  # Include 100 if data is below 100
    y_margin = (y_max - y_min) * 0.05  # 5% margin
    ax.set_ylim(y_min - y_margin, y_max + y_margin)

    plt.tight_layout()

    return fig


def create_timeseries_plot(
    times: np.ndarray,
    intensities: np.ndarray,
    temp_data: Dict,
    language: str = 'ja',
    font_name: str = 'Times New Roman',
    label_fontsize: int = 12,
    tick_fontsize: int = 10
) -> plt.Figure:
    """
    Create time-series plot showing raw data and temperature steps

    Args:
        times: Time data in seconds
        intensities: Intensity data
        temp_data: Dictionary with temperature step data
        language: 'ja' or 'en'
        font_name: Font name for the plot
        label_fontsize: Font size for axis labels
        tick_fontsize: Font size for tick labels

    Returns:
        matplotlib Figure object
    """
    # Setup font with fallback support
    setup_matplotlib_font(font_name, language)

    # Text labels
    if language == 'ja':
        xlabel = '時間 (分)'
        ylabel = '強度'
        title = '時系列データと各温度ステップ'
        raw_data_label = '生データ'
    else:
        xlabel = 'Time (min)'
        ylabel = 'Intensity'
        title = 'Time-Series Data and Temperature Steps'
        raw_data_label = 'Raw Data'

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 4))

    # Convert time from seconds to minutes
    times_min = times / 60.0

    # Plot raw data
    ax.plot(times_min, intensities, 'k-', linewidth=0.5, alpha=0.5, label=raw_data_label)

    # Define colors for each temperature step
    colors = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple', 'magenta']

    # Plot each temperature step region
    sorted_temps = sorted(temp_data.keys(), reverse=True)  # Sort from high to low
    for i, temp in enumerate(sorted_temps):
        data = temp_data[temp]
        time_start_min = data['time_start'] / 60.0
        time_end_min = data['time_end'] / 60.0

        # Highlight the region used for this temperature
        ax.axvspan(time_start_min, time_end_min,
                  alpha=0.3, color=colors[i % len(colors)],
                  label=f'{temp}°C')

        # Add vertical lines at boundaries
        ax.axvline(time_start_min, color=colors[i % len(colors)],
                  linestyle='--', linewidth=1, alpha=0.5)

    # Set labels and title
    ax.set_xlabel(xlabel, fontsize=label_fontsize)
    ax.set_ylabel(ylabel, fontsize=label_fontsize)
    ax.set_title(title, fontsize=label_fontsize + 2)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10, loc='upper left', ncol=4)

    # Set tick label font size
    ax.tick_params(axis='both', which='major', labelsize=tick_fontsize)

    plt.tight_layout()

    return fig


def create_simple_activity_plot(
    temperatures: np.ndarray,
    conversions: np.ndarray,
    language: str = 'ja',
    figsize: Tuple[int, int] = (12, 8),
    font_name: str = 'Times New Roman',
    label_fontsize: int = 14,
    tick_fontsize: int = 12,
    legend_fontsize: int = 12
) -> plt.Figure:
    """
    Create simple activity plot with experimental data only (no fitting)

    Args:
        temperatures: Experimental temperature data
        conversions: Experimental conversion data
        language: 'ja' or 'en'
        figsize: Figure size
        font_name: Font name for the plot
        label_fontsize: Font size for axis labels
        tick_fontsize: Font size for tick labels
        legend_fontsize: Font size for legend

    Returns:
        matplotlib Figure object
    """
    # Setup font with fallback support
    setup_matplotlib_font(font_name, language)

    # Text labels
    if language == 'ja':
        xlabel = '温度 (℃)'
        ylabel = '転換率 (%)'
        exp_data = '実測データ'
    else:
        xlabel = 'Temperature (°C)'
        ylabel = 'Conversion (%)'
        exp_data = 'Experimental Data'

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Plot experimental data
    ax.scatter(temperatures, conversions, color='red', s=80,
              label=exp_data, zorder=5, alpha=0.8)

    # Connect points with line
    sorted_indices = np.argsort(temperatures)
    ax.plot(temperatures[sorted_indices], conversions[sorted_indices],
           'k--', linewidth=1, alpha=0.3)

    # Set labels and grid
    ax.set_xlabel(xlabel, fontsize=label_fontsize)
    ax.set_ylabel(ylabel, fontsize=label_fontsize)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=legend_fontsize, loc='best')

    # Set tick label font size
    ax.tick_params(axis='both', which='major', labelsize=tick_fontsize)

    # Set axis limits
    ax.set_xlim(temperatures.min() - 30, temperatures.max() + 30)

    # Calculate Y-axis limits dynamically based on data
    y_min = min(conversions.min(), 0)  # Include 0 if data is all positive
    y_max = max(conversions.max(), 100)  # Include 100 if data is below 100
    y_margin = (y_max - y_min) * 0.05  # 5% margin
    ax.set_ylim(y_min - y_margin, y_max + y_margin)

    plt.tight_layout()

    return fig


def save_plot(fig: plt.Figure, filepath: str, dpi: int = 600):
    """
    Save plot to file in high quality

    Args:
        fig: matplotlib Figure object
        filepath: Output file path
        dpi: Resolution in dots per inch (default: 600 for high quality)
    """
    # Create directory if it doesn't exist
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    # Save figure
    fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
