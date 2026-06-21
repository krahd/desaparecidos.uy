import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { useEffect, useRef } from 'react';
import type { RouteGeometry } from './api';

const style: maplibregl.StyleSpecification = {
  version: 8,
  sources: {
    osm: {
      type: 'raster',
      tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
      tileSize: 256,
      attribution: '© OpenStreetMap contributors',
    },
  },
  layers: [{ id: 'osm', type: 'raster', source: 'osm' }],
};

function feature(geometry: RouteGeometry): GeoJSON.Feature {
  return { type: 'Feature', properties: {}, geometry: geometry as GeoJSON.Geometry };
}

export function TraversalMap({
  geometry,
  mode,
  onChange,
}: {
  geometry: RouteGeometry;
  mode: 'manual' | 'import' | 'autonomous';
  onChange: (geometry: RouteGeometry) => void;
}) {
  const container = useRef<HTMLDivElement | null>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const latest = useRef(geometry);
  const onChangeRef = useRef(onChange);

  useEffect(() => { latest.current = geometry; }, [geometry]);
  useEffect(() => { onChangeRef.current = onChange; }, [onChange]);

  useEffect(() => {
    if (!container.current) return;
    const instance = new maplibregl.Map({
      container: container.current,
      style,
      center: [-56.05, -32.8],
      zoom: 5.3,
      attributionControl: {},
    });
    instance.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
    instance.on('load', () => {
      instance.addSource('route', { type: 'geojson', data: feature(latest.current) });
      instance.addLayer({
        id: 'route-fill', type: 'fill', source: 'route',
        paint: { 'fill-color': '#8f3f32', 'fill-opacity': 0.18 },
        filter: ['==', '$type', 'Polygon'],
      });
      instance.addLayer({
        id: 'route-line', type: 'line', source: 'route',
        paint: { 'line-color': '#bc5a49', 'line-width': 4 },
      });
    });
    instance.on('click', (event) => {
      if (mode === 'import') return;
      const point = [event.lngLat.lng, event.lngLat.lat];
      const current = latest.current;
      const points = current.type === 'Polygon'
        ? (current.coordinates as number[][][])[0].slice(0, -1)
        : (current.coordinates as number[][]).slice();
      points.push(point);
      const next: RouteGeometry = mode === 'autonomous' && points.length >= 3
        ? { type: 'Polygon', coordinates: [[...points, points[0]]] }
        : { type: 'LineString', coordinates: points };
      latest.current = next;
      onChangeRef.current(next);
    });
    map.current = instance;
    return () => {
      instance.remove();
      map.current = null;
    };
  }, [mode]);

  useEffect(() => {
    const source = map.current?.getSource('route') as maplibregl.GeoJSONSource | undefined;
    source?.setData(feature(geometry));
  }, [geometry]);

  return <div className="traversal-map" ref={container} aria-label="Traversal route map" />;
}
