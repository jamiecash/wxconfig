import wxconfig as cfg
import definitions
import wx


if __name__ == '__main__':

    # Load the config
    cfg.Config().load(fr"{definitions.ROOT_DIR}\test\testconfig.yaml",
                      meta=fr"{definitions.ROOT_DIR}\test\testconfigmeta.yaml")

    # Create the app and frame
    app = wx.App(False)
    frame = wx.Frame()
    frame.Show()
    app.MainLoop()

    # Display the dialog
    settings_dialog = cfg.SettingsDialog(parent=None, exclude=[])
    res = settings_dialog.ShowModal()
