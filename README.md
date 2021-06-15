# wxconfig
A library for managing application settings stored in a yaml file. Provides a dynamically generated wxpython dialog box for enabling the user to modify settings. Supports settings metadata including setting label and help text which can be displayed in the dynamically generated dialog.

# Usage
1) Define your application settings in a yaml file:

###### [config.yaml]
```yaml
app_function_1:
  setting_theme_1:
    setting_1: A text value
    setting_2: True
    setting_3: 22.2
  setting_theme_2:
    setting_1: A text value
    setting_2: True
    setting_3: 22.2
```

2) If you require your settings dialog to contain nicely formatted labels and tooltips, define these in a separate yaml file:

###### [configmeta.yaml]
```yaml
app_function_1:
  setting_theme_1:
    setting_1:
      __label: Setting 1
      __helptext: This is the tooltip for setting 1
    setting_2:
      __label: Setting 2
      __helptext: This is the tooltip for setting 2
```

3) In your application, load your config. Also load your metadata if required:

```python

import wxconfig as cfg

cfg.Config().load("config.yaml", meta="configmeta.yaml")
```

4) You can access your applications config from anywhere in your application. Config is a singleton, and retains its state throughout the applications instance. Config values can be set and retrieved using dot notation to represent their path as defined in the config file:

```python

import wxconfig as cfg

# Get a config value
conf_val = cfg.Config().get('app_function_1.setting_theme_1.setting_1')

# Set a congig value
cfg.Config().set('app_function_1.setting_theme_1.setting_1', 'A new text value')
```

5) Any altered settings can be saved back to the config file:

```python

import wxconfig as cfg

cfg.Config().save()
```

6) Your application can open a setting dialog box that allows the user to change the applications settings. Any settings that you do not want the user to change can be excluded:

```python

import wxconfig as cfg

# Display the dialog. Exclude all settings under setting_theme_2
settings_dialog = cfg.SettingsDialog(parent=None, exclude=['setting_theme_2'])
res = settings_dialog.ShowModal()
```

7) If the user cancels the dialog, any changed settings are discarded, and the return value is wx.ID_CANCEL. If the user selects update, the settings are saved, and the return value is wx.ID_OK. All changed settings can be accessed through the setting dialogs changed_settings property, which contains a dict of settings paths and new values:

```python
import wx
import wxconfig as cfg

# Display the dialog. Exclude all settings under setting_theme_2
settings_dialog = cfg.SettingsDialog(parent=None, exclude=['setting_theme_2'])
res = settings_dialog.ShowModal()

if res == wx.ID_OK:
    for changed_setting in settings_dialog.changed_settings:
        # Application logic to handle changed config values goes here
        # ...
        print(f"Setting {changed_setting} has changed to {settings_dialog.changed_settings[changed_setting]}")

```

7) If you would like the settings dialogs position, size and style to be restored the next time the user opens it, then this can be stored in the config file. Create a config section named settings_window with the initial values. These will be changed if the user repositions or resizes the settings dialog. Keep the style value as is or change to a different wxpython window style:

###### [config.yaml]
```yaml
settings_window:
  x: 354
  y: 299
  width: 727
  height: 419
  style: 524352
```