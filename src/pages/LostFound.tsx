import React, { useState, useEffect, useCallback } from 'react';
import { Search, MapPin, AlertCircle, Upload, X, Loader2, CheckCircle } from 'lucide-react';
import L from 'leaflet';
import { MapContainer, TileLayer, Marker, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import client from '../api/client';
import { ErrorBoundary } from '../components/ErrorBoundary';
import type { MapMarker } from '../types';

const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api';
const uploadsBase = apiBase.replace(/\/api\/?$/, '') || 'http://localhost:3000';

function getUploadUrl(path: string | null | undefined): string {
  if (!path) return '';
  return path.startsWith('http') ? path : `${uploadsBase}${path}`;
}

/** Whether the marker has valid lat/lng (exclude 0,0 and invalid values) */
function hasValidCoords(m: MapMarker): boolean {
  return Number.isFinite(m.lat) && Number.isFinite(m.lng) && (m.lat !== 0 || m.lng !== 0);
}

/** Create Leaflet div icon for pet photo circle marker */
function createPetIcon(marker: MapMarker): L.DivIcon {
  const borderColor = marker.type === 'stray' ? '#f97316' : '#3b82f6';
  const imgStyle = marker.image
    ? `background:url(${marker.image}) center/cover;`
    : 'background:#94a3b8;';
  const html = `<div style="width:44px;height:44px;border-radius:50%;border:3px solid ${borderColor};box-shadow:0 2px 10px rgba(0,0,0,0.25);overflow:hidden;${imgStyle}"></div>`;
  return L.divIcon({
    html,
    className: 'custom-pet-marker',
    iconSize: [44, 44],
    iconAnchor: [22, 22],
  });
}

/** Fit map bounds to include all markers when they exist */
function FitBounds({ markers }: { markers: MapMarker[] }) {
  const map = useMap();
  const valid = markers.filter(hasValidCoords);
  const key = valid.map((m) => `${m.lat},${m.lng}`).join('|');
  useEffect(() => {
    if (valid.length === 0) return;
    if (valid.length === 1) {
      map.setView([valid[0].lat, valid[0].lng], 14);
      return;
    }
    const bounds = L.latLngBounds(valid.map((m) => [m.lat, m.lng]));
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
  }, [map, key]);
  return null;
}

function formatTimeAgo(iso: string): string {
  try {
    const d = new Date(iso);
    const diff = Date.now() - d.getTime();
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    if (diff < 86400000 * 7) return `${Math.floor(diff / 86400000)}d ago`;
    return d.toLocaleDateString();
  } catch {
    return '';
  }
}

function MapZoomControl() {
  const map = useMap();
  useEffect(() => {
    const zoomControl = L.control.zoom({ position: 'topright' });
    zoomControl.addTo(map);
    return () => {
      try {
        if (map && map.removeControl) map.removeControl(zoomControl);
      } catch {
        // Map may already be destroyed on unmount; ignore
      }
    };
  }, [map]);
  return null;
}

const LostFound = () => {
  const [mapMarkers, setMapMarkers] = useState<MapMarker[]>([]);
  const [selectedMarker, setSelectedMarker] = useState<string | null>(null);
  const [reportOpen, setReportOpen] = useState(false);
  const [reportSubmitting, setReportSubmitting] = useState(false);
  const [reportSuccess, setReportSuccess] = useState(false);
  const [reportError, setReportError] = useState<string | null>(null);
  const [reportForm, setReportForm] = useState({
    description: '',
    lat: '',
    lng: '',
    report_time: '',
    photo: null as File | null,
    photoPreview: null as string | null,
  });
  const [locationLoading, setLocationLoading] = useState(false);
  /** Time range: 1=24h, 3=3 days, 7=7 days (maps to API days param) */
  const [timeRangeDays, setTimeRangeDays] = useState<1 | 3 | 7>(1);

  const fetchMapMarkers = useCallback(async () => {
    try {
      const params = { days: timeRangeDays };
      const [strayRes, lostRes] = await Promise.all([
        client.get('/map/stray', { params }),
        client.get('/map/lost', { params }),
      ]);
      const strayList = Array.isArray((strayRes as { data?: unknown }).data) ? (strayRes as { data: Record<string, unknown>[] }).data : [];
      const lostList = Array.isArray((lostRes as { data?: unknown }).data) ? (lostRes as { data: Record<string, unknown>[] }).data : [];
      const markers: MapMarker[] = [];
      strayList.forEach((r) => {
        const lat = r.lat ?? 0;
        const lng = r.lng ?? 0;
        markers.push({
          id: `stray-${r.id}`,
          lat,
          lng,
          type: 'stray',
          description: r.description ?? '',
          timeAgo: formatTimeAgo(r.report_time ?? ''),
          image: getUploadUrl(r.photo_path) || '',
        });
      });
      lostList.forEach((r) => {
        if (r.status === 'found') return;
        const lat = r.lat ?? 0;
        const lng = r.lng ?? 0;
        markers.push({
          id: `lost-${r.id}`,
          lat,
          lng,
          type: 'lost',
          petName: r.breed ?? 'Unknown',
          description: r.description ?? '',
          timeAgo: formatTimeAgo(r.lost_time ?? ''),
          image: getUploadUrl(r.photo_path) || '',
        });
      });
      setMapMarkers(markers);
    } catch {
      setMapMarkers([]);
    }
  }, [timeRangeDays]);

  useEffect(() => {
    fetchMapMarkers();
  }, [fetchMapMarkers]);

  const handleGetLocation = () => {
    if (!navigator.geolocation) {
      setReportError('Geolocation is not supported. Please enter coordinates manually.');
      return;
    }
    setReportError(null);
    setLocationLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocationLoading(false);
        setReportForm((f) => ({
          ...f,
          lat: String(pos.coords.latitude),
          lng: String(pos.coords.longitude),
        }));
      },
      (err) => {
        setLocationLoading(false);
        const msg = err.code === 1
          ? 'Location permission denied. Please allow in browser settings or enter coordinates manually.'
          : err.code === 2
          ? 'Location unavailable. Check device location or enter coordinates manually.'
          : err.code === 3
          ? 'Location request timed out. Try again or enter coordinates manually.'
          : 'Could not get location. Please enter coordinates manually.';
        setReportError(msg);
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 60000 }
    );
  };

  const handleReportPhoto = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !file.type.startsWith('image/')) return;
    setReportForm((f) => ({
      ...f,
      photo: file,
      photoPreview: URL.createObjectURL(file),
    }));
  };

  const handleSubmitReport = async (e: React.FormEvent) => {
    e.preventDefault();
    setReportError(null);
    setReportSubmitting(true);
    try {
      const form = new FormData();
      form.append('description', reportForm.description.trim() || 'No description');
      form.append('lat', reportForm.lat || '0');
      form.append('lng', reportForm.lng || '0');
      form.append('report_time', reportForm.report_time || new Date().toISOString().slice(0, 19));
      if (reportForm.photo) form.append('photo', reportForm.photo);
      await client.post('/stray-report', form);
      await fetchMapMarkers();
      setReportSuccess(true);
      setTimeout(() => {
        if (reportForm.photoPreview) URL.revokeObjectURL(reportForm.photoPreview);
        setReportOpen(false);
        setReportSuccess(false);
        setLocationLoading(false);
        setReportForm({ description: '', lat: '', lng: '', report_time: '', photo: null, photoPreview: null });
      }, 1500);
    } catch (err: unknown) {
      const res = err && typeof err === 'object' && 'response' in err ? (err as { response?: { data?: { detail?: unknown } } }).response : undefined;
      const raw = res?.data?.detail;
      setReportError(typeof raw === 'string' ? raw : 'Report failed. Please try again later.');
    } finally {
      setReportSubmitting(false);
    }
  };

  const closeReportModal = () => {
    if (!reportSubmitting) {
      setReportOpen(false);
      setReportError(null);
      setLocationLoading(false);
      if (reportForm.photoPreview) URL.revokeObjectURL(reportForm.photoPreview);
      setReportForm({ description: '', lat: '', lng: '', report_time: '', photo: null, photoPreview: null });
    }
  };

  const validMarkers = mapMarkers.filter(hasValidCoords);
  const defaultCenter: [number, number] = [39.9, 116.4];
  const defaultZoom = 4;

  return (
    <div className="flex-1 relative overflow-hidden h-[calc(100vh-64px)] bg-gray-200">
        {/* Real map: Leaflet + OpenStreetMap */}
        <ErrorBoundary
          fallback={
            <div className="absolute inset-0 z-0 bg-gray-200 flex items-center justify-center">
              <p className="text-gray-600">Map failed to load. Please refresh the page.</p>
            </div>
          }
        >
          <div className="absolute inset-0 z-0 min-h-0">
            <MapContainer
              center={defaultCenter}
              zoom={defaultZoom}
              style={{ height: '100%', width: '100%' }}
              zoomControl={false}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <FitBounds markers={mapMarkers} />
              <MapZoomControl />
              {validMarkers.map((marker) => (
                <Marker
                  key={marker.id}
                  position={[marker.lat, marker.lng]}
                  icon={createPetIcon(marker)}
                  eventHandlers={{
                    click: () => setSelectedMarker(marker.id),
                  }}
                />
              ))}
            </MapContainer>
          </div>
        </ErrorBoundary>

        {/* Map UI Overlay - Search */}
        <div className="absolute top-6 left-6 z-10 w-80 max-w-[calc(100vw-3rem)]">
            <div className="bg-white/95 backdrop-blur-sm rounded-xl shadow-xl border border-gray-200 p-4 space-y-5">
                <div className="relative">
                    <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
                    <input type="text" placeholder="Search location or breed..." className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent" />
                </div>
                <div className="space-y-2">
                    <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Show On Map</label>
                    <div className="flex flex-col space-y-2">
                         <label className="flex items-center space-x-3 cursor-pointer p-2 rounded-lg hover:bg-gray-50">
                            <input type="checkbox" defaultChecked className="text-primary rounded border-gray-300 focus:ring-primary h-4 w-4" />
                            <div className="flex items-center space-x-2">
                                <span className="w-3 h-3 bg-primary rounded-full"></span>
                                <span className="text-sm font-medium text-gray-700">Stray Reports</span>
                            </div>
                        </label>
                        <label className="flex items-center space-x-3 cursor-pointer p-2 rounded-lg hover:bg-gray-50">
                            <input type="checkbox" defaultChecked className="text-secondary rounded border-gray-300 focus:ring-secondary h-4 w-4" />
                            <div className="flex items-center space-x-2">
                                <span className="w-3 h-3 bg-secondary rounded-full"></span>
                                <span className="text-sm font-medium text-gray-700">Lost Pet Announcements</span>
                            </div>
                        </label>
                    </div>
                </div>
                <div className="space-y-2">
                     <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Time Range</label>
                     <div className="flex bg-gray-100 p-1 rounded-lg">
                        <button type="button" onClick={() => setTimeRangeDays(1)} className={`flex-1 py-1.5 px-2 text-xs font-medium rounded-md ${timeRangeDays === 1 ? 'shadow-sm bg-white text-gray-900' : 'text-gray-500 hover:text-gray-900'}`}>24h</button>
                        <button type="button" onClick={() => setTimeRangeDays(3)} className={`flex-1 py-1.5 px-2 text-xs font-medium rounded-md ${timeRangeDays === 3 ? 'shadow-sm bg-white text-gray-900' : 'text-gray-500 hover:text-gray-900'}`}>3 Days</button>
                        <button type="button" onClick={() => setTimeRangeDays(7)} className={`flex-1 py-1.5 px-2 text-xs font-medium rounded-md ${timeRangeDays === 7 ? 'shadow-sm bg-white text-gray-900' : 'text-gray-500 hover:text-gray-900'}`}>7 Days</button>
                     </div>
                </div>
            </div>
        </div>

        {/* Selected Marker Detail Card */}
        {selectedMarker && (() => {
          const marker = mapMarkers.find(m => m.id === selectedMarker);
          if (!marker) return null;
          return (
            <div className="absolute bottom-1/2 left-1/2 transform -translate-x-1/2 -translate-y-20 z-30">
              <div className="w-64 bg-white rounded-xl shadow-2xl overflow-hidden border border-gray-200 animate-in fade-in zoom-in duration-300">
                <div className="relative h-32">
                  {marker.image ? (
                    <img src={marker.image} alt="Pet" className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                      <MapPin size={32} className="text-gray-400" />
                    </div>
                  )}
                  <div className={`absolute top-2 right-2 text-white text-xs px-2 py-0.5 rounded-full font-bold shadow-sm ${marker.type === 'stray' ? 'bg-primary' : 'bg-secondary'}`}>
                    {marker.type === 'stray' ? 'Stray' : 'Lost'}
                  </div>
                </div>
                <div className="p-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-bold text-gray-900">{marker.petName ?? (marker.type === 'stray' ? 'Stray Animal' : 'Lost')}</h3>
                      <p className="text-xs text-gray-500">{marker.timeAgo}</p>
                    </div>
                    <AlertCircle size={16} className="text-gray-400" />
                  </div>
                  {marker.description && (
                    <p className="mt-2 text-xs text-gray-600 line-clamp-2">{marker.description}</p>
                  )}
                  <div className="mt-3 flex space-x-2">
                    <button className="flex-1 bg-primary text-white text-xs font-semibold py-1.5 px-3 rounded-md hover:bg-orange-600 transition-colors shadow-sm">
                      {marker.type === 'lost' ? 'Contact' : 'Details'}
                    </button>
                    <button type="button" className="flex-1 bg-gray-100 text-gray-700 text-xs font-semibold py-1.5 px-3 rounded-md hover:bg-gray-200 transition-colors" onClick={() => setSelectedMarker(null)}>
                      Close
                    </button>
                  </div>
                </div>
                <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-4 h-4 bg-white rotate-45" />
              </div>
            </div>
          );
        })()}

        {/* Bottom right: Report button (zoom control is top-right on map) */}
        <div className="absolute bottom-6 right-6 z-[1000]">
            <button type="button" onClick={() => setReportOpen(true)} className="group flex items-center space-x-2 bg-primary hover:bg-orange-600 text-white px-6 py-3 rounded-full shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200">
                <AlertCircle size={20} />
                <span className="font-bold text-lg">Report Now</span>
            </button>
        </div>

        {/* Report Now modal: stray report */}
        {reportOpen && (
          <div className="absolute inset-0 z-40 flex items-center justify-center bg-black/50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-center p-4 border-b border-gray-100">
                <h2 className="text-lg font-bold text-gray-900">Report Stray Animal</h2>
                <button type="button" onClick={closeReportModal} className="p-2 rounded-lg hover:bg-gray-100 text-gray-500"><X size={20} /></button>
              </div>
              {reportSuccess ? (
                <div className="p-8 text-center">
                  <CheckCircle className="mx-auto text-green-500 mb-3" size={48} />
                  <p className="text-green-800 font-medium">Report submitted</p>
                  <p className="text-sm text-gray-500 mt-1">Thank you. Address will be resolved from coordinates.</p>
                </div>
              ) : (
                <form onSubmit={handleSubmitReport} className="p-4 space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Photo</label>
                    <label className="flex flex-col items-center justify-center w-full h-28 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                      {reportForm.photoPreview ? (
                        <img src={reportForm.photoPreview} alt="Preview" className="h-full w-full object-cover rounded-lg" />
                      ) : (
                        <>
                          <Upload className="text-gray-400 mb-1" size={24} />
                          <span className="text-xs text-gray-500">Click to upload</span>
                        </>
                      )}
                      <input type="file" className="sr-only" accept="image/*" onChange={handleReportPhoto} />
                    </label>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                    <textarea rows={3} value={reportForm.description} onChange={(e) => setReportForm((f) => ({ ...f, description: e.target.value }))} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-primary focus:border-primary" placeholder="Location, appearance, etc." />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Location (GPS)</label>
                    <div className="flex gap-2">
                      <input type="text" value={reportForm.lat} onChange={(e) => setReportForm((f) => ({ ...f, lat: e.target.value }))} className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="Latitude" />
                      <input type="text" value={reportForm.lng} onChange={(e) => setReportForm((f) => ({ ...f, lng: e.target.value }))} className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="Longitude" />
                      <button
                        type="button"
                        onClick={handleGetLocation}
                        disabled={locationLoading}
                        className="flex items-center gap-1 px-3 py-2 bg-secondary text-white rounded-lg text-sm font-medium whitespace-nowrap disabled:opacity-70 disabled:cursor-not-allowed"
                      >
                        {locationLoading ? <Loader2 size={16} className="animate-spin" /> : <MapPin size={16} />}
                        {locationLoading ? 'Getting location…' : 'Use current location'}
                      </button>
                    </div>
                    {locationLoading && <p className="text-xs text-amber-600 mt-1">If the browser prompts for location, choose Allow.</p>}
                    <p className="text-xs text-gray-500 mt-1">Address will be resolved from coordinates after submit.</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Report time</label>
                    <input type="datetime-local" value={reportForm.report_time} onChange={(e) => setReportForm((f) => ({ ...f, report_time: e.target.value }))} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                  </div>
                  {reportError && <p className="text-sm text-red-600">{reportError}</p>}
                  <div className="flex gap-3 pt-2">
                    <button type="button" onClick={closeReportModal} className="flex-1 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700">Cancel</button>
                    <button type="submit" disabled={reportSubmitting} className="flex-1 py-2 bg-primary text-white rounded-lg text-sm font-bold disabled:opacity-50 flex items-center justify-center gap-2">
                      {reportSubmitting ? <><Loader2 size={18} className="animate-spin" /> Submitting…</> : 'Submit report'}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        )}
    </div>
  );
};

export default LostFound;