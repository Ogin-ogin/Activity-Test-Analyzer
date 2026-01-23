"""
Visualization module for benzene oxidation activity analysis
"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from typing import Dict, Optional, Tuple, List
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
    tick_fontsize: int = 10,
    semi_auto_mode: bool = False,
    num_reactors: int = 1
) -> plt.Figure:
    """
    Create time-series plot showing raw data and temperature steps

    Args:
        times: Time data in seconds
        intensities: Intensity data
        temp_data: Dictionary with temperature step data (keyed by step index)
        language: 'ja' or 'en'
        font_name: Font name for the plot
        label_fontsize: Font size for axis labels
        tick_fontsize: Font size for tick labels
        semi_auto_mode: Whether in semi-auto mode (multiple reactors)
        num_reactors: Number of reactors

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
        reactor_label = '反応管{}'
    else:
        xlabel = 'Time (min)'
        ylabel = 'Intensity'
        title = 'Time-Series Data and Temperature Steps'
        raw_data_label = 'Raw Data'
        reactor_label = 'Reactor {}'

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 4))

    # Convert time from seconds to minutes
    times_min = times / 60.0

    # Plot raw data
    ax.plot(times_min, intensities, 'k-', linewidth=0.5, alpha=0.5, label=raw_data_label)

    # Define colors for each temperature step (for standard mode)
    temp_colors = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple', 'magenta']

    # Define distinct background colors for each reactor (for semi-auto mode)
    reactor_bg_colors = [
        (1.0, 0.8, 0.8, 0.3),   # Light red (reactor 1)
        (0.8, 0.8, 1.0, 0.3),   # Light blue (reactor 2)
        (0.8, 1.0, 0.8, 0.3),   # Light green (reactor 3)
        (1.0, 1.0, 0.8, 0.3),   # Light yellow (reactor 4)
        (1.0, 0.8, 1.0, 0.3),   # Light magenta (reactor 5)
        (0.8, 1.0, 1.0, 0.3),   # Light cyan (reactor 6)
    ]

    # Track which labels have been added
    added_labels = set()

    # Plot each temperature step region
    sorted_steps = sorted(temp_data.keys())
    for step_idx in sorted_steps:
        data = temp_data[step_idx]
        time_start_min = data['time_start'] / 60.0
        time_end_min = data['time_end'] / 60.0
        temp = data['temperature']
        reactor_id = data.get('reactor_id', 1)

        if semi_auto_mode:
            # Use reactor-based background colors
            bg_color = reactor_bg_colors[(reactor_id - 1) % len(reactor_bg_colors)]

            # Only add label for first occurrence of each reactor
            label = None
            if reactor_id not in added_labels:
                label = reactor_label.format(reactor_id)
                added_labels.add(reactor_id)

            # Fill background with reactor color
            ax.axvspan(time_start_min, time_end_min, color=bg_color[:3], alpha=bg_color[3],
                      label=label)

            # Add temperature annotation
            mid_time = (time_start_min + time_end_min) / 2
            y_pos = ax.get_ylim()[1] if ax.get_ylim()[1] != 1.0 else intensities.max()
            ax.text(mid_time, y_pos * 0.95, f'{int(temp)}°C',
                   ha='center', va='top', fontsize=8, alpha=0.7)
        else:
            # Standard mode - color by temperature
            # Get unique temperatures to assign colors
            unique_temps = sorted(set(d['temperature'] for d in temp_data.values()), reverse=True)
            temp_idx = unique_temps.index(temp)
            color = temp_colors[temp_idx % len(temp_colors)]

            # Only add label for first occurrence of each temperature
            label = None
            if temp not in added_labels:
                label = f'{temp}°C'
                added_labels.add(temp)

            ax.axvspan(time_start_min, time_end_min, alpha=0.3, color=color, label=label)

        # Add vertical lines at boundaries
        ax.axvline(time_start_min, color='gray', linestyle='--', linewidth=0.5, alpha=0.3)

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


def create_comparison_plot(
    reactor_data: Dict[int, Dict],
    fitting_results: Dict[int, Dict],
    language: str = 'ja',
    figsize: Tuple[int, int] = (12, 8),
    font_name: str = 'Times New Roman',
    label_fontsize: int = 14,
    tick_fontsize: int = 12,
    legend_fontsize: int = 12
) -> plt.Figure:
    """
    Create comparison plot overlaying multiple reactor activity curves

    Args:
        reactor_data: Dict[reactor_id: {'temperatures': array, 'conversions': array, ...}]
        fitting_results: Dict[reactor_id: {'temp_fit': array, 'conv_fit': array, 'tx_results': dict, 'r_squared': float}]
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
        reactor_label = '反応管{}'
        fit_label = 'フィット'
    else:
        xlabel = 'Temperature (°C)'
        ylabel = 'Conversion (%)'
        reactor_label = 'Reactor {}'
        fit_label = 'Fit'

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Define colors for each reactor
    reactor_colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
    markers = ['o', 's', '^', 'D', 'v', '<']

    all_temps = []
    all_convs = []

    # Plot each reactor's data
    for i, reactor_id in enumerate(sorted(reactor_data.keys())):
        data = reactor_data[reactor_id]
        temperatures = data['temperatures']
        conversions = data['conversions']
        color = reactor_colors[i % len(reactor_colors)]
        marker = markers[i % len(markers)]

        all_temps.extend(temperatures)
        all_convs.extend(conversions)

        # Plot experimental data
        ax.scatter(temperatures, conversions, color=color, s=80, marker=marker,
                  label=f'{reactor_label.format(reactor_id)} (data)', zorder=5, alpha=0.8)

        # Plot fitted curve if available
        if reactor_id in fitting_results and fitting_results[reactor_id] is not None:
            fit_data = fitting_results[reactor_id]
            temp_fit = fit_data['temp_fit']
            conv_fit = fit_data['conv_fit']
            r_squared = fit_data['r_squared']

            all_convs.extend(conv_fit)

            ax.plot(temp_fit, conv_fit, color=color, linewidth=2,
                   label=f'{reactor_label.format(reactor_id)} {fit_label} (R²={r_squared:.3f})',
                   linestyle='-')

    # Set labels and grid
    ax.set_xlabel(xlabel, fontsize=label_fontsize)
    ax.set_ylabel(ylabel, fontsize=label_fontsize)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=legend_fontsize, loc='best')

    # Set tick label font size
    ax.tick_params(axis='both', which='major', labelsize=tick_fontsize)

    # Set axis limits
    if all_temps:
        ax.set_xlim(min(all_temps) - 30, max(all_temps) + 30)

    # Calculate Y-axis limits dynamically based on data
    if all_convs:
        y_min = min(min(all_convs), 0)
        y_max = max(max(all_convs), 100)
        y_margin = (y_max - y_min) * 0.05
        ax.set_ylim(y_min - y_margin, y_max + y_margin)

    plt.tight_layout()

    return fig


def create_multi_file_comparison_plot(
    sample_data: List[Dict],
    language: str = 'ja',
    figsize: Tuple[int, int] = (12, 8),
    font_name: str = 'Times New Roman',
    label_fontsize: int = 14,
    tick_fontsize: int = 12,
    legend_fontsize: int = 12,
    legend_loc: str = 'upper left'
) -> plt.Figure:
    """
    Create comparison plot overlaying multiple sample activity curves from different files

    Args:
        sample_data: List of dicts containing:
            - 'name': Sample name (for legend)
            - 'temperatures': Temperature array
            - 'conversions': Conversion array
            - 'temp_fit': Fitted temperature curve (optional)
            - 'conv_fit': Fitted conversion curve (optional)
            - 'r_squared': R² value (optional)
            - 'tx_results': Dict of TX values (optional)
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
        temp_unit = '℃'
    else:
        xlabel = 'Temperature (°C)'
        ylabel = 'Conversion (%)'
        temp_unit = '°C'

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Define colors and markers for each sample
    sample_colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'cyan', 'olive', 'magenta']
    markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', 'h', '*']

    all_temps = []
    all_convs = []

    # Plot each sample's data
    for i, sample in enumerate(sample_data):
        name = sample.get('name', f'Sample {i+1}')
        temperatures = sample['temperatures']
        conversions = sample['conversions']
        color = sample_colors[i % len(sample_colors)]
        marker = markers[i % len(markers)]

        all_temps.extend(temperatures)
        all_convs.extend(conversions)

        # Build legend label with T50 value if available
        tx_results = sample.get('tx_results', {})
        t50_value = tx_results.get('T50', None)
        if t50_value is not None:
            legend_label = f'{name} (T50={t50_value:.0f}{temp_unit})'
        else:
            legend_label = name

        # Plot experimental data
        ax.scatter(temperatures, conversions, color=color, s=80, marker=marker,
                  label=legend_label, zorder=5, alpha=0.8)

        # Plot fitted curve if available (no legend entry)
        if 'temp_fit' in sample and 'conv_fit' in sample and sample['temp_fit'] is not None:
            temp_fit = sample['temp_fit']
            conv_fit = sample['conv_fit']

            all_convs.extend(conv_fit)

            ax.plot(temp_fit, conv_fit, color=color, linewidth=2, linestyle='-')

    # Set labels and grid
    ax.set_xlabel(xlabel, fontsize=label_fontsize)
    ax.set_ylabel(ylabel, fontsize=label_fontsize)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=legend_fontsize, loc=legend_loc)

    # Set tick label font size
    ax.tick_params(axis='both', which='major', labelsize=tick_fontsize)

    # Set axis limits
    if all_temps:
        ax.set_xlim(min(all_temps) - 30, max(all_temps) + 30)

    # Calculate Y-axis limits dynamically based on data
    if all_convs:
        y_min = min(min(all_convs), 0)
        y_max = max(max(all_convs), 100)
        y_margin = (y_max - y_min) * 0.05
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
