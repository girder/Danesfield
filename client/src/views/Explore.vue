<template>
  <v-row
    style="height: 100%"
    no-gutters
  >
    <v-col cols="3">
      <dataset-list />
    </v-col>
    <v-col
      cols="9"
      class="d-flex justify-center align-center"
    >
      <CesiumViewer :footprints="footprints" />
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref } from 'vue';
import { axiosInstance } from '@/api';
// eslint-disable-next-line import/no-cycle
import router from '@/router';
import DatasetList from '@/components/DatasetList.vue';
import CesiumViewer from '@/components/CesiumViewer.vue';
import DatasetPanel from '@/components/DatasetPanel.vue';
import centroid from '@turf/centroid';
import * as Cesium from 'cesium';
import { Cartesian3 } from 'cesium';
import { addPin } from '@/store/cesium/pins';
import { addGeojson, cesiumViewer } from '@/store/cesium';
import type { Polygon } from 'geojson';  // eslint-disable-line

export default defineComponent({
  name: 'Explore',
  components: {
    DatasetList, CesiumViewer, DatasetPanel,
  },
  setup() {
    const footprints = ref({});

    onMounted(async () => {
      const { data } = await axiosInstance.get('/datasets/footprints/');

      Object.entries(data as Record<number, Polygon>).forEach(([datasetId, footprint]) => {
        if (!footprint?.coordinates) {
          return;
        }
        const [x, y] = centroid(footprint).geometry.coordinates;
        addPin(Cartesian3.fromDegrees(x, y), datasetId); // add pin to dataset location to globe
        addGeojson(footprint, datasetId); // add dataset footprint to globe
      });

      const handler = new Cesium.ScreenSpaceEventHandler(cesiumViewer.value.scene.canvas);
      handler.setInputAction((movement: {position: Cesium.Cartesian2}) => {
        const clickedObject: {
          primitive: Cesium.Primitive; id: Cesium.Entity; } = cesiumViewer.value.scene.pick(
            movement.position,
          );

        router.push({ name: 'focus', params: { datasetId: clickedObject.id.name as string } });
      }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
    });

    return {
      footprints,
    };
  },
});
</script>
