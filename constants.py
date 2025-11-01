"""Shared constants for session state keys and app-wide identifiers."""

# Session key names
CHART_GEN = "chart_gen"
SUBMITTED = "submitted"
QUERY = "query"
IMPROVEMENT_TEXT_VALUE = "improvement_text_value"
HISTORY_INDEX = "history_index"
# NOTE: The app now relies solely on history + HISTORY_INDEX to select code,
# so flags like SHOW_IMPROVED/IS_CODE_GENERATED and caches like LAST_CODE/SELECTED_DFS
# were removed.
