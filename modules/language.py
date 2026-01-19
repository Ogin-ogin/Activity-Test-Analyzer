"""
Multi-language support for the application
"""

TEXTS = {
    'ja': {
        # UI elements
        'app_title': 'ベンゼン酸化活性試験 自動解析システム',
        'sidebar_title': '設定',
        'language_select': '言語 / Language',
        'file_select': 'データファイル選択',
        'browse_folder': 'フォルダをブラウズ',
        'select_file': 'ファイルを選択してください',
        'no_file_selected': 'ファイルが選択されていません',
        'file_selected': '選択されたファイル',

        # Analysis parameters
        'analysis_params': '解析パラメータ',
        'default_tx': 'デフォルトTX値',
        'custom_tx': 'カスタムTX値を追加',
        'custom_tx_help': 'カンマ区切りで入力 (例: 10,30,60,90)',
        'run_analysis': '解析実行',

        # Results
        'results_title': '解析結果',
        'fitting_results': 'フィッティング結果',
        'max_conv': '最大転換率 (a)',
        'growth_rate': '成長率 (b)',
        'inflection_temp': '変曲点温度 (c)',
        'min_conv': '最小転換率 (d)',
        'r_squared': '決定係数 (R²)',
        'tx_results': 'TX計算結果',
        'temp_unit': '℃',
        'percent': '%',

        # Graph
        'graph_title': 'ベンゼン酸化活性曲線',
        'xlabel': '温度 (℃)',
        'ylabel': '転換率 (%)',
        'exp_data': '実測データ',
        'sigmoid_fit': 'シグモイドフィット',
        'save_graph': 'グラフを保存',
        'graph_saved': 'グラフが保存されました',

        # Data processing
        'processing': '処理中...',
        'reading_file': 'ファイル読み込み中...',
        'calculating': '計算中...',
        'fitting': 'フィッティング中...',

        # Errors
        'error': 'エラー',
        'fitting_error': 'フィッティングエラー',
        'file_read_error': 'ファイル読み込みエラー',
        'invalid_data': '無効なデータ形式',
        'cannot_calc': '計算不可（範囲外）',

        # Temperature data
        'temp_data_title': '各温度でのデータ',
        'temperature': '温度',
        'intensity_avg': '平均強度',
        'conversion': '転換率',
        'data_points': 'データポイント数',

        # Graph settings
        'graph_settings': 'グラフ設定',
        'font_family': 'フォント',
        'label_fontsize': '軸ラベルのフォントサイズ',
        'tick_fontsize': '目盛りのフォントサイズ',
        'legend_fontsize': '凡例のフォントサイズ',

        # Save settings
        'save_folder_preset': '保存先フォルダ（プリセット）',
        'save_folder_custom': 'カスタムパス',
        'use_custom_path': 'カスタムパスを使用',

        # Time-series plot
        'timeseries_title': '時系列データと使用データ範囲',
        'timeseries_desc': '各色の範囲は、対応する温度での平均強度計算に使用されたデータを示します。',

        # Protocol settings
        'protocol_settings': 'パターン設定',
        'load_protocol': 'パターンを読み込む',
        'save_protocol': 'パターンを保存',
        'custom_protocol': 'カスタムパターン',
        'protocol_name': 'パターン名',
        'new_pattern': '新規作成',
        'select_pattern': 'パターンを選択',
        'num_steps': 'ステップ数',
        'ramp_time': 'ランプ時間 (分)',
        'analysis_time': '解析時間 (分)',
        'step': 'ステップ',
        'hold_time': 'ホールド時間 (分)',
        'protocol_saved': 'パターンが保存されました',
        'protocol_loaded': 'パターンが読み込まれました',
        'enter_protocol_name': 'パターン名を入力してください',
        'delete_protocol': 'パターンを削除',
        'confirm_delete': '本当に削除しますか？',
        'protocol_deleted': 'パターンが削除されました',
        'cannot_delete_default': 'デフォルト設定は削除できません',
        'ramp_time_help': '各ステップ間の温度移動時間',
        'analysis_time_help': '各ステップのホールド時間のうち、後半何分を解析に使用するか',

        # Calibration curve settings
        'calibration_settings': '検量線設定',
        'calibration_slope': '傾き',
        'calibration_intercept': '切片',
        'calibration_formula': '計算式: 転換率(%) = 傾き × 強度 + 切片',
        'calibration_saved': '検量線設定が保存されました',
    },
    'en': {
        # UI elements
        'app_title': 'Benzene Oxidation Activity - Automated Analysis System',
        'sidebar_title': 'Settings',
        'language_select': 'Language / 言語',
        'file_select': 'Data File Selection',
        'browse_folder': 'Browse Folder',
        'select_file': 'Please select a file',
        'no_file_selected': 'No file selected',
        'file_selected': 'Selected file',

        # Analysis parameters
        'analysis_params': 'Analysis Parameters',
        'default_tx': 'Default TX values',
        'custom_tx': 'Add Custom TX values',
        'custom_tx_help': 'Enter comma-separated values (e.g., 10,30,60,90)',
        'run_analysis': 'Run Analysis',

        # Results
        'results_title': 'Analysis Results',
        'fitting_results': 'Fitting Results',
        'max_conv': 'Maximum conversion (a)',
        'growth_rate': 'Growth rate (b)',
        'inflection_temp': 'Inflection temperature (c)',
        'min_conv': 'Minimum conversion (d)',
        'r_squared': 'Coefficient of determination (R²)',
        'tx_results': 'TX Calculation Results',
        'temp_unit': '°C',
        'percent': '%',

        # Graph
        'graph_title': 'Benzene Oxidation Activity Curve',
        'xlabel': 'Temperature (°C)',
        'ylabel': 'Conversion (%)',
        'exp_data': 'Experimental Data',
        'sigmoid_fit': 'Sigmoid Fit',
        'save_graph': 'Save Graph',
        'graph_saved': 'Graph saved successfully',

        # Data processing
        'processing': 'Processing...',
        'reading_file': 'Reading file...',
        'calculating': 'Calculating...',
        'fitting': 'Fitting...',

        # Errors
        'error': 'Error',
        'fitting_error': 'Fitting error',
        'file_read_error': 'File reading error',
        'invalid_data': 'Invalid data format',
        'cannot_calc': 'Cannot calculate (out of range)',

        # Temperature data
        'temp_data_title': 'Data at Each Temperature',
        'temperature': 'Temperature',
        'intensity_avg': 'Average Intensity',
        'conversion': 'Conversion',
        'data_points': 'Data Points',

        # Graph settings
        'graph_settings': 'Graph Settings',
        'font_family': 'Font Family',
        'label_fontsize': 'Axis Label Font Size',
        'tick_fontsize': 'Tick Label Font Size',
        'legend_fontsize': 'Legend Font Size',

        # Save settings
        'save_folder_preset': 'Save Folder (Preset)',
        'save_folder_custom': 'Custom Path',
        'use_custom_path': 'Use Custom Path',

        # Time-series plot
        'timeseries_title': 'Time-Series Data and Used Data Ranges',
        'timeseries_desc': 'Colored regions indicate data used for calculating average intensity at each temperature.',

        # Protocol settings
        'protocol_settings': 'Protocol Settings',
        'load_protocol': 'Load Protocol',
        'save_protocol': 'Save Protocol',
        'custom_protocol': 'Custom Protocol',
        'protocol_name': 'Protocol Name',
        'new_pattern': 'New Pattern',
        'select_pattern': 'Select Pattern',
        'num_steps': 'Number of Steps',
        'ramp_time': 'Ramp Time (min)',
        'analysis_time': 'Analysis Time (min)',
        'step': 'Step',
        'hold_time': 'Hold Time (min)',
        'protocol_saved': 'Protocol saved successfully',
        'protocol_loaded': 'Protocol loaded successfully',
        'enter_protocol_name': 'Please enter protocol name',
        'delete_protocol': 'Delete Protocol',
        'confirm_delete': 'Are you sure you want to delete?',
        'protocol_deleted': 'Protocol deleted successfully',
        'cannot_delete_default': 'Cannot delete default settings',
        'ramp_time_help': 'Time to move between temperature steps',
        'analysis_time_help': 'Duration (from end of hold) to use for analysis',

        # Calibration curve settings
        'calibration_settings': 'Calibration Curve Settings',
        'calibration_slope': 'Slope',
        'calibration_intercept': 'Intercept',
        'calibration_formula': 'Formula: Conversion(%) = Slope × Intensity + Intercept',
        'calibration_saved': 'Calibration settings saved successfully',
    }
}

def get_text(language='ja'):
    """Get text dictionary for specified language"""
    return TEXTS.get(language, TEXTS['en'])
