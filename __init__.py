def classFactory(iface):
    from .buscar_shapefile import BuscarShapefile
    return BuscarShapefile(iface)
