import { GeoJsonDataSource, HeadingPitchRange, Math } from 'cesium';
import { ref, watch } from 'vue';
import { cesiumViewer, addGeojson } from '@/store/cesium';
import type { GeoJSON } from 'geojson';  // eslint-disable-line

export const visibleFootprints = ref<Record<string, GeoJSON >>({});

export const addFootprint = async (spatialId: number, footprint: GeoJSON|undefined, type: 'imagery' | 'tiles3d' | 'fmv') => {
  let key: string;
  switch (type) {
    case 'imagery':
      key = `imagery_${spatialId}`;
      break;
    case 'tiles3d':
      key = `tiles3d_${spatialId}`;
      break;
    case 'fmv':
      key = `fmv_${spatialId}`;
      break;
    default:
      return;
  }
  if (key && footprint) {
    visibleFootprints.value = { ...visibleFootprints.value, [key]: footprint };
  }
};

export const removeFootprint = (spatialId: number, type: 'imagery' | 'tiles3d' | 'fmv') => {
  let key: string;
  switch (type) {
    case 'imagery':
      key = `imagery_${spatialId}`;
      break;
    case 'tiles3d':
      key = `tiles3d_${spatialId}`;
      break;
    case 'fmv':
      key = `fmv_${spatialId}`;
      break;
    default:
      return;
  }
  if (visibleFootprints.value[key]) {
    visibleFootprints.value = Object.fromEntries(
      Object.entries(visibleFootprints.value).filter(([k]) => k !== key),
    );
  }
};

const footprintSources: Record<string, GeoJsonDataSource> = {};

watch(visibleFootprints, (newFootprints, oldFootprints) => {
  Object.keys(oldFootprints).forEach(
    (key) => {
      if (!Object.keys(newFootprints).includes(key)) {
        // remove footprint
        if (key in footprintSources) {
          cesiumViewer.value.dataSources.remove(footprintSources[key]);
          delete footprintSources[key];
        }
      }
    },
  );
  Object.entries(newFootprints).forEach(
    async ([key, footprint]) => {
      if (!Object.keys(oldFootprints).includes(key)) {
        // add footprint
        footprintSources[key] = await addGeojson(footprint, key);
        cesiumViewer.value.flyTo(footprintSources[key], {
          offset: new HeadingPitchRange(
            Math.toRadians(0),
            Math.toRadians(-90.0),
          ),
        });
      }
    },
  );
});
