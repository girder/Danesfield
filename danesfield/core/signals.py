from django.db import transaction
from django.db.models.base import ModelBase
from django.db.models.signals import post_save
from django.dispatch import receiver
from rgd.utility import skip_signal
from rgd_3d.models import Mesh3D

from danesfield.core.tasks.etl import extract_las_spatial_ref


@receiver(post_save, sender=Mesh3D)
@skip_signal()
def _post_save_mesh_file(sender: ModelBase, instance: Mesh3D, *args, **kwargs):
    transaction.on_commit(lambda: extract_las_spatial_ref.delay(instance.pk))
