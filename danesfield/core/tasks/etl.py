import numpy as np
from django.contrib.gis.geos import Polygon
from rgd.models import ChecksumFile
from rgd_3d.models import Mesh3D, Mesh3DSpatial
import celery


@celery.shared_task
def extract_las_spatial_ref(mesh_pk):
    from pyntcloud import PyntCloud
    from pyproj import Transformer

    mesh: Mesh3D = Mesh3D.objects.get(pk=mesh_pk)
    mesh_file: ChecksumFile = mesh.file
    with mesh_file.yield_local_path(try_fuse=False, yield_file_set=False) as input_path:
        cloud = PyntCloud.from_file(str(input_path))
    header = cloud.las_header

    header.x_min, header.x_max
    header.y_min, header.y_max

    coords = np.array(
        (
            (header.x_min, header.y_max),
            (header.x_min, header.y_max),
            (header.x_max, header.y_max),
            (header.x_max, header.y_min),
            (header.x_min, header.y_min),
            (header.x_min, header.y_max),  # Close the loop
        )
    )

    # convert coords from EPSG:32617 to EPSG:4326
    # https://spatialreference.org/ref/epsg/wgs-84-utm-zone-17n/
    transformer = Transformer.from_crs("EPSG:32617", "epsg:4326")
    y, x = transformer.transform(coords[:, 0], coords[:, 1])
    gcoords = np.c_[x, y]

    Mesh3DSpatial.objects.get_or_create(
        source=mesh, outline=Polygon(gcoords.tolist()), footprint=Polygon(gcoords.tolist())
    )
