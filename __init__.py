def classFactory(iface):  # QGIS will use this
    from .main import GoPro360ImporterPlugin
    return GoPro360ImporterPlugin(iface)