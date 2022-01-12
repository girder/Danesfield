from typing import Union

from django.http.response import HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from rdoasis.algorithms.models import Dataset
from rdoasis.algorithms.views.algorithms import DatasetViewSet as BaseDatasetViewSet
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rgd.models import ChecksumFile
from rgd_3d.models import Mesh3D
from rgd_imagery.models import Image, Raster
from rgd_imagery.models.raster import RasterMeta


class DatasetViewSet(BaseDatasetViewSet):
    @action(detail=True, methods=['GET'], url_path='viewer/(?P<path>.+)')
    def viewer(self, request: Request, pk: str, path: str):
        """Redirects to the appropriate viewer for the given file."""
        dataset: Dataset = get_object_or_404(Dataset, pk=pk)
        checksum_file: ChecksumFile = get_object_or_404(dataset.files, name=path)
        for model in [Image, Mesh3D]:
            try:
                ingested_file = model.objects.get(file=checksum_file)

                # Display the associated Raster if this is an Image
                if model == Image:
                    ingested_file: Raster = ingested_file.imageset_set.first().raster
                    model = RasterMeta

                return HttpResponseRedirect(
                    reverse(model.detail_view_name, kwargs={'pk': ingested_file.pk})
                )
            except model.DoesNotExist:
                pass

        return HttpResponseNotFound()
