# Saved-delay UI checkpoint failure

On the89a489d7a AppImage (Qt6.12.0), choosing3seconds through the Capture monitor button menu persisted preferences.captureDelaySeconds. Clicking Capture monitor then failed to hide/checkpoint the UI, with the saved unclassified-provider-settings modal. No operation was accepted. src/ui/ViewState.cpp omitted the new nonsecret preference. Fixed e1459d104; regression covers all delay choices and unknown-field rejection. Later evidence records the corrected menus on each desktop.
