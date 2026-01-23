"""
Benzene Oxidation Activity Analysis System
Streamlit-based web application for automatic analysis of FT-IR benzene intensity data
"""
import streamlit as st
import os
import numpy as np
from modules.language import get_text
from modules.data_processor import BenzeneDataProcessor, get_file_list
from modules.fitting import SigmoidFitter
from modules.visualization import create_activity_plot, create_simple_activity_plot, create_timeseries_plot, create_comparison_plot, create_multi_file_comparison_plot, save_plot, get_available_fonts
from modules.settings_manager import SettingsManager, ProtocolSettings, TemperatureStep

# Page configuration
st.set_page_config(
    page_title="Benzene Oxidation Activity Analysis",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = 'ja'
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'default_save_path' not in st.session_state:
    st.session_state.default_save_path = r"C:\Users\ginga\OneDrive\画像\グラフ\M2\活性曲線"
if 'default_data_path' not in st.session_state:
    st.session_state.default_data_path = r"C:\Users\ginga\OneDrive\ドキュメント\研究室\修士研究\USBデータ\FT-IR"
if 'font_name' not in st.session_state:
    st.session_state.font_name = 'Times New Roman'
if 'label_fontsize' not in st.session_state:
    st.session_state.label_fontsize = 25
if 'tick_fontsize' not in st.session_state:
    st.session_state.tick_fontsize = 25
if 'legend_fontsize' not in st.session_state:
    st.session_state.legend_fontsize = 20
if 'settings_manager' not in st.session_state:
    st.session_state.settings_manager = SettingsManager()
if 'protocol_settings' not in st.session_state:
    st.session_state.protocol_settings = st.session_state.settings_manager.get_default_settings()
if 'calibration_slope' not in st.session_state:
    st.session_state.calibration_slope = -995.32
if 'calibration_intercept' not in st.session_state:
    st.session_state.calibration_intercept = 101.36

# Load user preferences (paths, fonts, TX values, etc.)
if 'user_preferences_loaded' not in st.session_state:
    settings_mgr = st.session_state.settings_manager
    user_prefs = settings_mgr.load_user_preferences()
    if user_prefs:
        if 'default_save_path' in user_prefs:
            st.session_state.default_save_path = user_prefs['default_save_path']
        if 'default_data_path' in user_prefs:
            st.session_state.default_data_path = user_prefs['default_data_path']
        if 'font_name' in user_prefs:
            st.session_state.font_name = user_prefs['font_name']
        if 'label_fontsize' in user_prefs:
            st.session_state.label_fontsize = user_prefs['label_fontsize']
        if 'tick_fontsize' in user_prefs:
            st.session_state.tick_fontsize = user_prefs['tick_fontsize']
        if 'legend_fontsize' in user_prefs:
            st.session_state.legend_fontsize = user_prefs['legend_fontsize']
        if 'default_tx' in user_prefs:
            st.session_state.default_tx = user_prefs['default_tx']
        if 'calibration_slope' in user_prefs:
            st.session_state.calibration_slope = user_prefs['calibration_slope']
        if 'calibration_intercept' in user_prefs:
            st.session_state.calibration_intercept = user_prefs['calibration_intercept']
    st.session_state.user_preferences_loaded = True

if 'default_tx' not in st.session_state:
    st.session_state.default_tx = [20, 50, 80]
if 'multi_file_comparison_done' not in st.session_state:
    st.session_state.multi_file_comparison_done = False
if 'legend_position' not in st.session_state:
    st.session_state.legend_position = 'upper left'


def save_user_prefs():
    """Save user preferences (paths, fonts, TX values, calibration curve, etc.)"""
    settings_mgr = st.session_state.settings_manager

    # Get current values from session state
    prefs = {
        'default_save_path': st.session_state.get('save_folder_input', st.session_state.get('default_save_path')),
        'default_data_path': st.session_state.get('data_folder_input', st.session_state.get('default_data_path')),
        'font_name': st.session_state.get('font_selector', st.session_state.get('font_name', 'Times New Roman')),
        'label_fontsize': st.session_state.get('label_fontsize_input', st.session_state.get('label_fontsize', 25)),
        'tick_fontsize': st.session_state.get('tick_fontsize_input', st.session_state.get('tick_fontsize', 25)),
        'legend_fontsize': st.session_state.get('legend_fontsize_input', st.session_state.get('legend_fontsize', 20)),
        'default_tx': st.session_state.get('default_tx_selector', st.session_state.get('default_tx', [20, 50, 80])),
        'calibration_slope': st.session_state.get('calibration_slope_input', st.session_state.get('calibration_slope', -995.32)),
        'calibration_intercept': st.session_state.get('calibration_intercept_input', st.session_state.get('calibration_intercept', 101.36))
    }

    settings_mgr.save_user_preferences(prefs)


def main():
    """Main application"""

    # Sidebar - Settings
    with st.sidebar:
        # Language selection
        lang_options = {'日本語': 'ja', 'English': 'en'}
        selected_lang = st.selectbox(
            '言語 / Language',
            options=list(lang_options.keys()),
            index=0 if st.session_state.language == 'ja' else 1
        )
        st.session_state.language = lang_options[selected_lang]

    # Get text for current language
    text = get_text(st.session_state.language)

    # Title
    st.title(text['app_title'])

    # Sidebar - File selection and parameters
    with st.sidebar:
        st.header(text['sidebar_title'])

        # Protocol settings section
        with st.expander(text['protocol_settings'], expanded=False):
            settings_mgr = st.session_state.settings_manager

            # Get available patterns
            available_protocols = settings_mgr.list_settings_files()

            # Create pattern options (add "New Pattern" option)
            pattern_options = ['__new__'] + available_protocols
            pattern_display_names = {
                '__new__': f"🆕 {text['new_pattern']}",
                **{p: p.replace('.json', '') for p in available_protocols}
            }

            # Initialize current_pattern_file if not exists
            if 'current_pattern_file' not in st.session_state:
                st.session_state.current_pattern_file = 'default.json'

            # Pattern selector - use session state for current value
            selected_pattern = st.selectbox(
                text['select_pattern'],
                options=pattern_options,
                format_func=lambda x: pattern_display_names.get(x, x),
                index=pattern_options.index(st.session_state.current_pattern_file) if st.session_state.current_pattern_file in pattern_options else 0,
                key='pattern_selector_widget'
            )

            # Check if pattern selection changed
            if selected_pattern != st.session_state.current_pattern_file:
                print(f"[DEBUG] Pattern changed from '{st.session_state.current_pattern_file}' to '{selected_pattern}'")
                st.session_state.current_pattern_file = selected_pattern

                if selected_pattern == '__new__':
                    print("[DEBUG] Creating new pattern with default settings")
                    # Create new pattern with default settings
                    st.session_state.protocol_settings = ProtocolSettings(
                        name="New Pattern",
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
                    st.session_state.editing_new = True
                elif selected_pattern:
                    print(f"[DEBUG] Loading pattern: {selected_pattern}")
                    # Load selected pattern
                    loaded = settings_mgr.load_settings(selected_pattern)
                    if loaded:
                        print(f"[DEBUG] Pattern loaded successfully: {loaded.name}")
                        print(f"[DEBUG] Steps: {len(loaded.steps)} steps")
                        print(f"[DEBUG] First step temp: {loaded.steps[0].temperature if loaded.steps else 'N/A'}")
                        st.session_state.protocol_settings = loaded
                        st.session_state.editing_new = False
                    else:
                        st.error(f"Failed to load pattern: {selected_pattern}")

                print("[DEBUG] Clearing widget states...")
                # Clear form widget states to force refresh
                keys_to_clear = ['protocol_name_input', 'ramp_time_input', 'analysis_time_input', 'num_steps_input']
                for key in keys_to_clear:
                    if key in st.session_state:
                        print(f"[DEBUG] Deleting key: {key}")
                        del st.session_state[key]

                # Clear temperature and hold time keys
                for i in range(20):  # Max 20 steps
                    temp_key = f'temp_{i}'
                    hold_key = f'hold_{i}'
                    if temp_key in st.session_state:
                        print(f"[DEBUG] Deleting key: {temp_key}")
                        del st.session_state[temp_key]
                    if hold_key in st.session_state:
                        print(f"[DEBUG] Deleting key: {hold_key}")
                        del st.session_state[hold_key]

                print("[DEBUG] Calling st.rerun()...")
                st.rerun()

            # Delete button (only show if not editing new and not default)
            if st.session_state.current_pattern_file != '__new__' and st.session_state.current_pattern_file != 'default.json':
                if st.button(f"🗑️ {text['delete_protocol']}", key='del_btn'):
                    if settings_mgr.delete_settings(st.session_state.current_pattern_file):
                        st.success(text['protocol_deleted'])
                        st.session_state.current_pattern_file = 'default.json'
                        st.session_state.protocol_settings = settings_mgr.get_default_settings()
                        st.rerun()

            st.divider()

            # Edit pattern section
            current_protocol = st.session_state.protocol_settings

            # Use pattern file as part of widget keys to force refresh when pattern changes
            pattern_key = st.session_state.current_pattern_file.replace('.json', '').replace('/', '_')

            print(f"[DEBUG] Rendering widgets with pattern_key: {pattern_key}")
            print(f"[DEBUG] Current protocol name: {current_protocol.name}")
            print(f"[DEBUG] Current protocol steps: {len(current_protocol.steps)}")

            # Measurement mode selection
            mode_options = {
                text['standard_mode']: 'standard',
                text['semi_auto_mode']: 'semi_auto'
            }
            current_mode = getattr(current_protocol, 'mode', 'standard')
            mode_display = text['standard_mode'] if current_mode == 'standard' else text['semi_auto_mode']

            selected_mode_display = st.radio(
                text['measurement_mode'],
                options=list(mode_options.keys()),
                index=0 if current_mode == 'standard' else 1,
                key=f'mode_selector_{pattern_key}',
                horizontal=True,
                help=text['semi_auto_mode_help']
            )
            selected_mode = mode_options[selected_mode_display]
            is_semi_auto = selected_mode == 'semi_auto'

            # Number of reactors (only for semi-auto mode)
            if is_semi_auto:
                num_reactors = st.number_input(
                    text['num_reactors'],
                    min_value=2,
                    max_value=10,
                    value=max(2, getattr(current_protocol, 'num_reactors', 2)),
                    step=1,
                    key=f'num_reactors_input_{pattern_key}'
                )
            else:
                num_reactors = 1

            st.divider()

            # Protocol name
            protocol_name = st.text_input(
                text['protocol_name'],
                value=current_protocol.name,
                key=f'protocol_name_input_{pattern_key}'
            )

            # Common parameters
            col1, col2 = st.columns(2)

            with col1:
                ramp_time = st.number_input(
                    text['ramp_time'],
                    min_value=0,
                    max_value=60,
                    value=current_protocol.ramp_time,
                    step=1,
                    help=text['ramp_time_help'],
                    key=f'ramp_time_input_{pattern_key}'
                )

            with col2:
                analysis_time = st.number_input(
                    text['analysis_time'],
                    min_value=1,
                    max_value=60,
                    value=current_protocol.analysis_time,
                    step=1,
                    help=text['analysis_time_help'],
                    key=f'analysis_time_input_{pattern_key}'
                )

            # Number of steps
            num_steps = st.number_input(
                text['num_steps'],
                min_value=1,
                max_value=20,
                value=len(current_protocol.steps),
                step=1,
                key=f'num_steps_input_{pattern_key}'
            )

            # Temperature steps
            steps = []
            for i in range(num_steps):
                st.markdown(f"**{text['step']} {i+1}**")

                if is_semi_auto:
                    col_temp, col_hold, col_reactor = st.columns([2, 2, 1])
                else:
                    col_temp, col_hold = st.columns(2)

                with col_temp:
                    if i < len(current_protocol.steps):
                        default_temp = current_protocol.steps[i].temperature
                    else:
                        # Use previous step's temperature minus 50, or fallback to safe value
                        if i > 0 and len(steps) > 0:
                            default_temp = max(50.0, steps[-1].temperature - 50)
                        else:
                            default_temp = max(50.0, 500 - i * 50)

                    temp = st.number_input(
                        f"{text['temperature']} (℃)",
                        min_value=0.0,
                        max_value=1000.0,
                        value=float(default_temp),
                        step=10.0,
                        key=f'temp_{i}_{pattern_key}'
                    )

                with col_hold:
                    if i < len(current_protocol.steps):
                        default_hold = current_protocol.steps[i].hold_time
                    else:
                        default_hold = 20

                    hold = st.number_input(
                        f"{text['hold_time']}",
                        min_value=1,
                        max_value=180,
                        value=default_hold,
                        step=1,
                        key=f'hold_{i}_{pattern_key}'
                    )

                # Reactor selection (only for semi-auto mode)
                if is_semi_auto:
                    with col_reactor:
                        if i < len(current_protocol.steps):
                            default_reactor = getattr(current_protocol.steps[i], 'reactor_id', 1)
                        else:
                            # Alternate reactors by default
                            default_reactor = (i % num_reactors) + 1

                        reactor_id = st.selectbox(
                            text['reactor'],
                            options=list(range(1, num_reactors + 1)),
                            index=min(default_reactor - 1, num_reactors - 1),
                            key=f'reactor_{i}_{pattern_key}'
                        )
                else:
                    reactor_id = 1

                steps.append(TemperatureStep(temperature=temp, hold_time=hold, reactor_id=reactor_id))

            st.divider()

            # Save protocol
            if st.button(text['save_protocol'], key='save_btn', type='primary'):
                if protocol_name.strip():
                    new_protocol = ProtocolSettings(
                        name=protocol_name,
                        steps=steps,
                        ramp_time=ramp_time,
                        analysis_time=analysis_time,
                        mode=selected_mode,
                        num_reactors=num_reactors
                    )

                    # Update current protocol
                    st.session_state.protocol_settings = new_protocol

                    # Save to file
                    filename = f"{protocol_name}.json" if not protocol_name.endswith('.json') else protocol_name
                    settings_mgr.save_settings(new_protocol, filename)

                    # Update current pattern file reference
                    st.session_state.current_pattern_file = filename
                    st.session_state.editing_new = False

                    st.success(text['protocol_saved'])
                    st.rerun()
                else:
                    st.error(text['enter_protocol_name'])

        st.divider()

        # Data folder path setting
        st.subheader(text['file_select'])
        st.text_input(
            text['browse_folder'],
            value=st.session_state.default_data_path,
            help="Path to folder containing .asc files",
            key='data_folder_input',
            on_change=save_user_prefs
        )

        # Update default_data_path from widget state
        if 'data_folder_input' in st.session_state:
            st.session_state.default_data_path = st.session_state.data_folder_input
            data_folder = st.session_state.data_folder_input
        else:
            data_folder = st.session_state.default_data_path

        # Get file list
        file_list = get_file_list(data_folder, '.asc')
        file_names = [os.path.basename(f) for f in file_list]

        # File selection
        if len(file_names) > 0:
            selected_file_name = st.selectbox(
                text['select_file'],
                options=file_names
            )
            selected_file_idx = file_names.index(selected_file_name)
            selected_file_path = file_list[selected_file_idx]
            st.success(f"{text['file_selected']}: {selected_file_name}")
        else:
            st.warning(text['no_file_selected'])
            selected_file_path = None

        # File upload as alternative
        uploaded_file = st.file_uploader(
            "Upload .asc file (alternative)",
            type=['asc']
        )

        st.divider()

        # Multi-file comparison mode
        st.subheader(text['multi_file_mode'])
        st.caption(text['multi_file_mode_help'])

        # Multi-select for files
        if len(file_names) > 0:
            selected_files_for_comparison = st.multiselect(
                text['select_files'],
                options=file_names,
                key='multi_file_selector'
            )
        else:
            selected_files_for_comparison = []

        # Sample names for each selected file
        multi_file_sample_names = {}
        for i, fname in enumerate(selected_files_for_comparison):
            default_name = os.path.splitext(fname)[0]
            multi_file_sample_names[fname] = st.text_input(
                f"{text['sample_name']} ({fname})",
                value=default_name,
                key=f'sample_name_{i}'
            )

        # Run multi-file comparison button
        run_multi_comparison = st.button(
            text['run_comparison'],
            type="secondary",
            key='run_multi_comparison_btn'
        )

        st.divider()

        # Analysis parameters
        st.subheader(text['analysis_params'])

        # Default TX values
        default_tx = st.multiselect(
            text['default_tx'],
            options=[10, 20, 30, 40, 50, 60, 70, 80, 90],
            default=st.session_state.default_tx,
            key='default_tx_selector',
            on_change=save_user_prefs
        )

        # Update session state
        st.session_state.default_tx = default_tx

        # Custom TX values
        custom_tx_input = st.text_input(
            text['custom_tx'],
            value="",
            help=text['custom_tx_help']
        )

        # Parse custom TX values
        custom_tx = []
        if custom_tx_input.strip():
            try:
                custom_tx = [float(x.strip()) for x in custom_tx_input.split(',') if x.strip()]
            except ValueError:
                st.error("Invalid custom TX values")

        # Combine TX values
        all_tx = sorted(set(default_tx + custom_tx))

        st.divider()

        # Graph settings
        st.subheader(text['graph_settings'])

        # Get available fonts
        available_fonts = get_available_fonts()

        # Font selection
        font_name = st.selectbox(
            text['font_family'],
            options=available_fonts,
            index=available_fonts.index(st.session_state.font_name) if st.session_state.font_name in available_fonts else 0,
            key='font_selector',
            on_change=save_user_prefs
        )
        st.session_state.font_name = font_name

        # Font size settings in columns
        font_col1, font_col2, font_col3 = st.columns(3)

        with font_col1:
            label_fontsize = st.number_input(
                text['label_fontsize'],
                min_value=6,
                max_value=40,
                value=st.session_state.label_fontsize,
                step=1,
                key='label_fontsize_input',
                on_change=save_user_prefs
            )
            st.session_state.label_fontsize = label_fontsize

        with font_col2:
            tick_fontsize = st.number_input(
                text['tick_fontsize'],
                min_value=6,
                max_value=40,
                value=st.session_state.tick_fontsize,
                step=1,
                key='tick_fontsize_input',
                on_change=save_user_prefs
            )
            st.session_state.tick_fontsize = tick_fontsize

        with font_col3:
            legend_fontsize = st.number_input(
                text['legend_fontsize'],
                min_value=6,
                max_value=40,
                value=st.session_state.legend_fontsize,
                step=1,
                key='legend_fontsize_input',
                on_change=save_user_prefs
            )
            st.session_state.legend_fontsize = legend_fontsize

        # Legend position selector
        legend_pos_options = {
            text['upper_left']: 'upper left',
            text['lower_right']: 'lower right'
        }
        current_legend_pos = st.session_state.get('legend_position', 'upper left')
        current_legend_display = text['upper_left'] if current_legend_pos == 'upper left' else text['lower_right']

        legend_pos_display = st.radio(
            text['legend_position'],
            options=list(legend_pos_options.keys()),
            index=0 if current_legend_pos == 'upper left' else 1,
            horizontal=True,
            key='legend_position_selector'
        )
        st.session_state.legend_position = legend_pos_options[legend_pos_display]

        st.divider()

        # Calibration curve settings
        st.subheader(text['calibration_settings'])
        st.caption(text['calibration_formula'])

        cal_col1, cal_col2 = st.columns(2)

        with cal_col1:
            calibration_slope = st.number_input(
                text['calibration_slope'],
                value=st.session_state.calibration_slope,
                step=0.01,
                format="%.4f",
                key='calibration_slope_input',
                on_change=save_user_prefs
            )
            st.session_state.calibration_slope = calibration_slope

        with cal_col2:
            calibration_intercept = st.number_input(
                text['calibration_intercept'],
                value=st.session_state.calibration_intercept,
                step=0.01,
                format="%.4f",
                key='calibration_intercept_input',
                on_change=save_user_prefs
            )
            st.session_state.calibration_intercept = calibration_intercept

        st.divider()

        # Run analysis button
        run_analysis = st.button(text['run_analysis'], type="primary", width='stretch')

    # Main content area
    if run_analysis:
        if selected_file_path is None and uploaded_file is None:
            st.error(text['no_file_selected'])
            return

        # Determine file path
        if uploaded_file is not None:
            # Save uploaded file temporarily
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getvalue())
            file_path = temp_path
            file_name_base = os.path.splitext(uploaded_file.name)[0]
        else:
            file_path = selected_file_path
            file_name_base = os.path.splitext(os.path.basename(selected_file_path))[0]

        # Check if semi-auto mode
        protocol = st.session_state.protocol_settings
        is_semi_auto_mode = getattr(protocol, 'mode', 'standard') == 'semi_auto'

        # Progress indicator
        with st.spinner(text['processing']):
            try:
                # Data processing
                st.info(text['reading_file'])
                processor = BenzeneDataProcessor(
                    conversion_slope=st.session_state.calibration_slope,
                    conversion_intercept=st.session_state.calibration_intercept,
                    protocol_settings=st.session_state.protocol_settings
                )

                if is_semi_auto_mode:
                    # Semi-auto mode: process for multiple reactors
                    reactor_data, times, intensities, temp_data = processor.process_file_semi_auto(file_path)

                    # Store raw data
                    st.session_state.reactor_data = reactor_data
                    st.session_state.times = times
                    st.session_state.intensities = intensities
                    st.session_state.temp_data = temp_data
                    st.session_state.file_name_base = file_name_base
                    st.session_state.is_semi_auto_mode = True

                    # Fitting for each reactor
                    st.info(text['fitting'])
                    fitting_results = {}

                    for reactor_id, data in reactor_data.items():
                        fitter = SigmoidFitter()
                        success = fitter.fit(data['temperatures'], data['conversions'])

                        if success:
                            fitting_params = fitter.get_fitting_params()
                            tx_results = fitter.calculate_tx_values(all_tx)
                            temp_fit, conv_fit = fitter.get_fitted_curve()

                            fitting_results[reactor_id] = {
                                'success': True,
                                'fitting_params': fitting_params,
                                'tx_results': tx_results,
                                'temp_fit': temp_fit,
                                'conv_fit': conv_fit,
                                'r_squared': fitting_params['r_squared']
                            }
                        else:
                            fitting_results[reactor_id] = {
                                'success': False
                            }

                    st.session_state.fitting_results = fitting_results
                    st.session_state.analysis_done = True

                else:
                    # Standard mode
                    temperatures, conversions, detailed_df, times, intensities, temp_data = processor.process_file(file_path)

                    # Store raw data first (so timeseries plot can always be shown)
                    st.session_state.temperatures = temperatures
                    st.session_state.conversions = conversions
                    st.session_state.detailed_df = detailed_df
                    st.session_state.times = times
                    st.session_state.intensities = intensities
                    st.session_state.temp_data = temp_data
                    st.session_state.file_name_base = file_name_base
                    st.session_state.is_semi_auto_mode = False

                    # Fitting
                    st.info(text['fitting'])
                    fitter = SigmoidFitter()
                    success = fitter.fit(temperatures, conversions)

                    if not success:
                        # Fitting failed, but still show timeseries data
                        st.session_state.analysis_done = True
                        st.session_state.fitting_success = False
                        st.warning(text['fitting_error'])
                    else:
                        # Calculate TX values
                        st.info(text['calculating'])
                        fitting_params = fitter.get_fitting_params()
                        tx_results = fitter.calculate_tx_values(all_tx)
                        temp_fit, conv_fit = fitter.get_fitted_curve()

                        # Store fitting results in session state
                        st.session_state.analysis_done = True
                        st.session_state.fitting_success = True
                        st.session_state.fitting_params = fitting_params
                        st.session_state.tx_results = tx_results
                        st.session_state.temp_fit = temp_fit
                        st.session_state.conv_fit = conv_fit

                # Clean up temp file
                if uploaded_file is not None and os.path.exists(temp_path):
                    os.remove(temp_path)

            except Exception as e:
                st.error(f"{text['error']}: {str(e)}")
                import traceback
                st.error(traceback.format_exc())
                return

    # Display results if analysis is done
    if st.session_state.analysis_done:
        st.success(text['results_title'])

        # Show protocol info
        protocol = st.session_state.protocol_settings
        is_semi_auto_display = getattr(protocol, 'mode', 'standard') == 'semi_auto'

        with st.expander(f"📋 {text['protocol_settings']}: {protocol.name}", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(text['num_steps'], len(protocol.steps))
            with col2:
                st.metric(text['ramp_time'], f"{protocol.ramp_time} min")
            with col3:
                st.metric(text['analysis_time'], f"{protocol.analysis_time} min")

            # Show step details
            steps_data = []
            for i, step in enumerate(protocol.steps):
                step_info = {
                    text['step']: f"{i+1}",
                    f"{text['temperature']} (℃)": step.temperature,
                    f"{text['hold_time']}": f"{step.hold_time} min"
                }
                if is_semi_auto_display:
                    step_info[text['reactor']] = getattr(step, 'reactor_id', 1)
                steps_data.append(step_info)
            st.table(steps_data)

        # Check if semi-auto mode results
        if st.session_state.get('is_semi_auto_mode', False):
            # Semi-auto mode: display with tabs for each reactor
            reactor_data = st.session_state.reactor_data
            fitting_results = st.session_state.fitting_results
            num_reactors = len(reactor_data)

            # Create tabs for each reactor + comparison tab
            tab_names = [text['reactor_n'].format(rid) for rid in sorted(reactor_data.keys())]
            tab_names.append(text['comparison'])
            tabs = st.tabs(tab_names)

            # Store figures for saving
            reactor_figs = {}

            # Display each reactor's results in its tab
            for tab_idx, reactor_id in enumerate(sorted(reactor_data.keys())):
                with tabs[tab_idx]:
                    data = reactor_data[reactor_id]
                    fit_result = fitting_results.get(reactor_id, {})

                    if fit_result.get('success', False):
                        # Create two columns for results
                        col1, col2 = st.columns(2)

                        with col1:
                            # Fitting parameters
                            st.subheader(text['fitting_results'])
                            params = fit_result['fitting_params']

                            st.metric(text['max_conv'], f"{params['a_max_conversion']:.2f} %")
                            st.metric(text['growth_rate'], f"{params['b_growth_rate']:.4f}")
                            st.metric(text['inflection_temp'], f"{params['c_inflection_temp']:.1f} {text['temp_unit']}")
                            st.metric(text['min_conv'], f"{params['d_min_conversion']:.2f} %")
                            st.metric(text['r_squared'], f"{params['r_squared']:.4f}")

                        with col2:
                            # TX results
                            st.subheader(text['tx_results'])
                            tx_data = []
                            for key, value in sorted(fit_result['tx_results'].items()):
                                if value is not None:
                                    tx_data.append({
                                        'TX': key,
                                        f"{text['temperature']} ({text['temp_unit']})": f"{value:.1f}"
                                    })
                                else:
                                    tx_data.append({
                                        'TX': key,
                                        f"{text['temperature']} ({text['temp_unit']})": text['cannot_calc']
                                    })
                            st.table(tx_data)

                        st.divider()

                        # Activity plot with fitting
                        st.subheader(text['graph_title'])
                        fig = create_activity_plot(
                            data['temperatures'],
                            data['conversions'],
                            fit_result['temp_fit'],
                            fit_result['conv_fit'],
                            fit_result['tx_results'],
                            fit_result['r_squared'],
                            language=st.session_state.language,
                            font_name=st.session_state.font_name,
                            label_fontsize=st.session_state.label_fontsize,
                            tick_fontsize=st.session_state.tick_fontsize,
                            legend_fontsize=st.session_state.legend_fontsize
                        )
                        reactor_figs[reactor_id] = fig
                        st.pyplot(fig)

                    else:
                        st.warning(text['fitting_error'])

                        # Simple plot without fitting
                        st.subheader(text['graph_title'])
                        fig = create_simple_activity_plot(
                            data['temperatures'],
                            data['conversions'],
                            language=st.session_state.language,
                            font_name=st.session_state.font_name,
                            label_fontsize=st.session_state.label_fontsize,
                            tick_fontsize=st.session_state.tick_fontsize,
                            legend_fontsize=st.session_state.legend_fontsize
                        )
                        reactor_figs[reactor_id] = fig
                        st.pyplot(fig)

                    # Temperature data table
                    st.subheader(text['temp_data_title'])
                    display_df = data['detailed_df'].copy()
                    display_df.columns = [
                        f"{text['temperature']} ({text['temp_unit']})",
                        text['intensity_avg'],
                        f"{text['conversion']} (%)",
                        text['data_points']
                    ]
                    st.dataframe(display_df, use_container_width=True)

            # Comparison tab
            with tabs[-1]:
                # Time-series plot with reactor colors
                st.subheader(text['timeseries_title'])
                st.caption(text['timeseries_desc'])

                timeseries_fig = create_timeseries_plot(
                    st.session_state.times,
                    st.session_state.intensities,
                    st.session_state.temp_data,
                    language=st.session_state.language,
                    font_name=st.session_state.font_name,
                    label_fontsize=st.session_state.label_fontsize,
                    tick_fontsize=st.session_state.tick_fontsize,
                    semi_auto_mode=True,
                    num_reactors=num_reactors
                )
                st.pyplot(timeseries_fig)

                st.divider()

                # Comparison plot
                st.subheader(text['graph_title'])
                comparison_fig = create_comparison_plot(
                    reactor_data,
                    fitting_results,
                    language=st.session_state.language,
                    font_name=st.session_state.font_name,
                    label_fontsize=st.session_state.label_fontsize,
                    tick_fontsize=st.session_state.tick_fontsize,
                    legend_fontsize=st.session_state.legend_fontsize
                )
                st.pyplot(comparison_fig)

                st.divider()

                # TX comparison table
                st.subheader(text['comparison_table'])
                comparison_data = []
                for reactor_id in sorted(reactor_data.keys()):
                    fit_result = fitting_results.get(reactor_id, {})
                    row = {text['reactor']: reactor_id}
                    if fit_result.get('success', False):
                        for key, value in sorted(fit_result['tx_results'].items()):
                            row[key] = f"{value:.1f}" if value is not None else "-"
                    else:
                        row['Status'] = text['fitting_error']
                    comparison_data.append(row)
                st.table(comparison_data)

            # Store the main figure for saving (comparison plot)
            fig = comparison_fig

        else:
            # Standard mode display (original code)
            # Only show fitting results if fitting succeeded
            if st.session_state.get('fitting_success', False):
                # Create two columns for results
                col1, col2 = st.columns(2)

                with col1:
                    # Fitting parameters
                    st.subheader(text['fitting_results'])
                    params = st.session_state.fitting_params

                    st.metric(
                        text['max_conv'],
                        f"{params['a_max_conversion']:.2f} %"
                    )
                    st.metric(
                        text['growth_rate'],
                        f"{params['b_growth_rate']:.4f}"
                    )
                    st.metric(
                        text['inflection_temp'],
                        f"{params['c_inflection_temp']:.1f} {text['temp_unit']}"
                    )
                    st.metric(
                        text['min_conv'],
                        f"{params['d_min_conversion']:.2f} %"
                    )
                    st.metric(
                        text['r_squared'],
                        f"{params['r_squared']:.4f}"
                    )

                with col2:
                    # TX results
                    st.subheader(text['tx_results'])
                    tx_data = []
                    for key, value in sorted(st.session_state.tx_results.items()):
                        if value is not None:
                            tx_data.append({
                                'TX': key,
                                f"{text['temperature']} ({text['temp_unit']})": f"{value:.1f}"
                            })
                        else:
                            tx_data.append({
                                'TX': key,
                                f"{text['temperature']} ({text['temp_unit']})": text['cannot_calc']
                            })

                    st.table(tx_data)

                st.divider()

            # Time-series plot
            st.subheader(text['timeseries_title'])
            st.caption(text['timeseries_desc'])

            # Create time-series plot
            timeseries_fig = create_timeseries_plot(
                st.session_state.times,
                st.session_state.intensities,
                st.session_state.temp_data,
                language=st.session_state.language,
                font_name=st.session_state.font_name,
                label_fontsize=st.session_state.label_fontsize,
                tick_fontsize=st.session_state.tick_fontsize
            )

            # Display time-series plot
            st.pyplot(timeseries_fig)

            # Temperature data table
            st.subheader(text['temp_data_title'])
            display_df = st.session_state.detailed_df.copy()
            display_df.columns = [
                f"{text['temperature']} ({text['temp_unit']})",
                text['intensity_avg'],
                f"{text['conversion']} (%)",
                text['data_points']
            ]
            st.dataframe(display_df, use_container_width=True)

            # Activity plot - show regardless of fitting success
            st.divider()

            # Graph
            st.subheader(text['graph_title'])

            # Create plot based on fitting success
            if st.session_state.get('fitting_success', False):
                # Create plot with fitting curve
                fig = create_activity_plot(
                    st.session_state.temperatures,
                    st.session_state.conversions,
                    st.session_state.temp_fit,
                    st.session_state.conv_fit,
                    st.session_state.tx_results,
                    st.session_state.fitting_params['r_squared'],
                    language=st.session_state.language,
                    font_name=st.session_state.font_name,
                    label_fontsize=st.session_state.label_fontsize,
                    tick_fontsize=st.session_state.tick_fontsize,
                    legend_fontsize=st.session_state.legend_fontsize
                )
            else:
                # Create simple plot with experimental data only
                fig = create_simple_activity_plot(
                    st.session_state.temperatures,
                    st.session_state.conversions,
                    language=st.session_state.language,
                    font_name=st.session_state.font_name,
                    label_fontsize=st.session_state.label_fontsize,
                    tick_fontsize=st.session_state.tick_fontsize,
                    legend_fontsize=st.session_state.legend_fontsize
                )

            # Display plot
            st.pyplot(fig)

        st.divider()

        # Save graph section
        st.subheader(text['save_graph'])

        # Create columns for save settings
        save_col1, save_col2 = st.columns(2)

        with save_col1:
            # Save folder path setting (same style as data folder)
            st.text_input(
                text['save_folder_custom'],
                value=st.session_state.default_save_path,
                help="Path to save graphs",
                key='save_folder_input',
                on_change=save_user_prefs
            )

            # Update default_save_path from widget state
            if 'save_folder_input' in st.session_state:
                st.session_state.default_save_path = st.session_state.save_folder_input
                save_directory = st.session_state.save_folder_input
            else:
                save_directory = st.session_state.default_save_path

        with save_col2:
            # File name
            save_filename = st.text_input(
                "File name (without extension) / ファイル名（拡張子なし）",
                value=st.session_state.file_name_base
            )

            # DPI setting
            dpi_value = st.number_input(
                "DPI (解像度)",
                min_value=150,
                max_value=1200,
                value=600,
                step=50,
                help="Higher DPI = Higher quality (default: 600)"
            )

        # Save button
        if st.button(text['save_graph'], type="primary"):
            try:
                # Create full file path
                full_path = os.path.join(save_directory, f"{save_filename}.png")

                # Save plot with specified DPI
                save_plot(fig, full_path, dpi=dpi_value)

                st.success(f"{text['graph_saved']}: {full_path}")

            except Exception as e:
                st.error(f"{text['error']}: {str(e)}")

    # Multi-file comparison mode
    if run_multi_comparison:
        if len(selected_files_for_comparison) < 2:
            st.error(text['min_files_required'])
        else:
            with st.spinner(text['processing']):
                try:
                    # Process each file
                    multi_sample_data = []
                    multi_file_detailed_results = {}

                    for fname in selected_files_for_comparison:
                        # Get full path
                        file_idx = file_names.index(fname)
                        fpath = file_list[file_idx]
                        sample_name = multi_file_sample_names.get(fname, fname)

                        # Create processor
                        processor = BenzeneDataProcessor(
                            conversion_slope=st.session_state.calibration_slope,
                            conversion_intercept=st.session_state.calibration_intercept,
                            protocol_settings=st.session_state.protocol_settings
                        )

                        # Process file
                        temperatures, conversions, detailed_df, times, intensities, temp_data = processor.process_file(fpath)

                        # Fit sigmoid
                        fitter = SigmoidFitter()
                        success = fitter.fit(temperatures, conversions)

                        sample_entry = {
                            'name': sample_name,
                            'temperatures': temperatures,
                            'conversions': conversions,
                            'detailed_df': detailed_df
                        }

                        if success:
                            fitting_params = fitter.get_fitting_params()
                            tx_results = fitter.calculate_tx_values(all_tx)
                            temp_fit, conv_fit = fitter.get_fitted_curve()

                            sample_entry['temp_fit'] = temp_fit
                            sample_entry['conv_fit'] = conv_fit
                            sample_entry['r_squared'] = fitting_params['r_squared']
                            sample_entry['fitting_params'] = fitting_params
                            sample_entry['tx_results'] = tx_results
                            sample_entry['fitting_success'] = True
                        else:
                            sample_entry['fitting_success'] = False

                        multi_sample_data.append(sample_entry)
                        multi_file_detailed_results[sample_name] = sample_entry

                    # Store results in session state
                    st.session_state.multi_sample_data = multi_sample_data
                    st.session_state.multi_file_detailed_results = multi_file_detailed_results
                    st.session_state.multi_file_comparison_done = True

                except Exception as e:
                    st.error(f"{text['error']}: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())

    # Display multi-file comparison results
    if st.session_state.get('multi_file_comparison_done', False):
        st.divider()
        st.header(text['multi_file_graph_title'])

        multi_sample_data = st.session_state.multi_sample_data
        multi_file_detailed_results = st.session_state.multi_file_detailed_results

        # Create comparison plot
        multi_fig = create_multi_file_comparison_plot(
            multi_sample_data,
            language=st.session_state.language,
            font_name=st.session_state.font_name,
            label_fontsize=st.session_state.label_fontsize,
            tick_fontsize=st.session_state.tick_fontsize,
            legend_fontsize=st.session_state.legend_fontsize,
            legend_loc=st.session_state.legend_position
        )
        st.pyplot(multi_fig)

        st.divider()

        # TX comparison table
        st.subheader(text['comparison_table'])
        comparison_rows = []
        for sample in multi_sample_data:
            row = {text['sample_name']: sample['name']}
            if sample.get('fitting_success', False):
                for key, value in sorted(sample['tx_results'].items()):
                    row[key] = f"{value:.1f}" if value is not None else "-"
                row['R²'] = f"{sample['r_squared']:.4f}"
            else:
                row['Status'] = text['fitting_error']
            comparison_rows.append(row)
        st.table(comparison_rows)

        st.divider()

        # Individual sample details in expanders
        for sample in multi_sample_data:
            with st.expander(f"📊 {sample['name']}", expanded=False):
                if sample.get('fitting_success', False):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader(text['fitting_results'])
                        params = sample['fitting_params']
                        st.metric(text['max_conv'], f"{params['a_max_conversion']:.2f} %")
                        st.metric(text['growth_rate'], f"{params['b_growth_rate']:.4f}")
                        st.metric(text['inflection_temp'], f"{params['c_inflection_temp']:.1f} {text['temp_unit']}")
                        st.metric(text['min_conv'], f"{params['d_min_conversion']:.2f} %")
                        st.metric(text['r_squared'], f"{params['r_squared']:.4f}")

                    with col2:
                        st.subheader(text['tx_results'])
                        tx_data = []
                        for key, value in sorted(sample['tx_results'].items()):
                            if value is not None:
                                tx_data.append({
                                    'TX': key,
                                    f"{text['temperature']} ({text['temp_unit']})": f"{value:.1f}"
                                })
                            else:
                                tx_data.append({
                                    'TX': key,
                                    f"{text['temperature']} ({text['temp_unit']})": text['cannot_calc']
                                })
                        st.table(tx_data)
                else:
                    st.warning(text['fitting_error'])

                # Data table
                st.subheader(text['temp_data_title'])
                display_df = sample['detailed_df'].copy()
                display_df.columns = [
                    f"{text['temperature']} ({text['temp_unit']})",
                    text['intensity_avg'],
                    f"{text['conversion']} (%)",
                    text['data_points']
                ]
                st.dataframe(display_df, use_container_width=True)

        st.divider()

        # Save multi-file comparison graph
        st.subheader(text['save_graph'])

        save_col1, save_col2 = st.columns(2)

        with save_col1:
            multi_save_directory = st.text_input(
                text['save_folder_custom'],
                value=st.session_state.default_save_path,
                key='multi_save_folder_input'
            )

        with save_col2:
            multi_save_filename = st.text_input(
                "File name / ファイル名",
                value="multi_comparison",
                key='multi_save_filename'
            )

            multi_dpi_value = st.number_input(
                "DPI",
                min_value=150,
                max_value=1200,
                value=600,
                step=50,
                key='multi_dpi_input'
            )

        if st.button(text['save_graph'], type="primary", key='save_multi_graph_btn'):
            try:
                full_path = os.path.join(multi_save_directory, f"{multi_save_filename}.png")
                save_plot(multi_fig, full_path, dpi=multi_dpi_value)
                st.success(f"{text['graph_saved']}: {full_path}")
            except Exception as e:
                st.error(f"{text['error']}: {str(e)}")


if __name__ == "__main__":
    main()
