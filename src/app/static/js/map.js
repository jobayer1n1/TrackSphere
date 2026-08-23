// TrackSphere Interactive Leaflet Map & GPS Telemetry Engine
// Built for high-precision live fleet tracking and driver telemetry

let map = null;
let vehicleMarkers = {};
let historyPolylines = {};
let activeVehicleId = null;

/**
 * Initialize or reset the Leaflet Map instance
 */
function initMap(defaultLat = 40.7128, defaultLon = -74.0060, zoom = 11) {
    const mapEl = document.getElementById('map');
    if (!mapEl) return null;

    // Defensive teardown if already initialized
    if (map) {
        try {
            map.remove();
        } catch (e) {
            console.warn('[TrackSphere Map] Existing map teardown warning:', e);
        }
        map = null;
        vehicleMarkers = {};
        historyPolylines = {};
    }

    try {
        map = L.map('map', {
            zoomControl: true,
            attributionControl: true,
        }).setView([defaultLat, defaultLon], zoom);

        // High-contrast modern Voyager tile layer with OpenStreetMap fallback
        const cartoVoyager = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://carto.com/">CartoDB</a> | &copy; <a href="https://openstreetmap.org">OpenStreetMap</a>',
            maxZoom: 19,
            subdomains: 'abcd',
        });

        cartoVoyager.addTo(map);

        // Auto-recalculate sizing once container has laid out
        setTimeout(() => {
            if (map) map.invalidateSize();
        }, 200);

        return map;
    } catch (err) {
        console.error('[TrackSphere Map] Map initialization failed:', err);
        showToast('Map initialization error: ' + err.message, 'error');
        return null;
    }
}

/**
 * Generate a modern, themed SVG / HTML icon for vehicles and driver units
 */
function createVehicleIcon(registrationNumber, status = 'AVAILABLE', isFiller = false) {
    const isAssigned = status === 'ASSIGNED' || status === 'IN_PROGRESS';
    const color = isFiller ? '#8b5cf6' : (isAssigned ? '#06b6d4' : '#10b981');
    const iconSymbol = isFiller ? '🧑‍✈️' : (registrationNumber.startsWith('VAN') ? '🚐' : '🚚');
    const pulseClass = isAssigned ? 'pulse-active' : '';

    return L.divIcon({
        className: 'custom-vehicle-marker-wrapper',
        html: `
            <div class="marker-container ${pulseClass}" style="display: flex; flex-direction: column; align-items: center; cursor: pointer;">
                <div style="background: ${color}; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 16px; border: 2px solid #ffffff; box-shadow: 0 0 12px ${color};">
                    ${iconSymbol}
                </div>
                <div style="background: rgba(17, 24, 39, 0.95); border: 1px solid ${color}; padding: 2px 7px; border-radius: 9999px; font-size: 10px; font-weight: 700; color: #f9fafb; margin-top: 3px; white-space: nowrap; box-shadow: 0 2px 6px rgba(0,0,0,0.5);">
                    ${registrationNumber}
                </div>
            </div>
        `,
        iconSize: [50, 55],
        iconAnchor: [25, 25],
        popupAnchor: [0, -25],
    });
}

/**
 * Query REST API for a vehicle or driver location
 */
async function fetchVehicleLocation(vehicleId) {
    try {
        const res = await fetch(`/api/locations/${vehicleId}`);
        if (!res.ok) {
            if (res.status === 403) {
                console.info(`[TrackSphere Map] Vehicle #${vehicleId} RBAC restricted for this user session.`);
                return null;
            }
            const err = await res.json();
            throw new Error(err.detail || 'Failed to fetch location');
        }
        return await res.json();
    } catch (err) {
        console.warn(`[TrackSphere Map] Telemetry fetch for vehicle #${vehicleId}:`, err.message);
        return null;
    }
}

/**
 * Fetch current logged-in driver's location (assigned vehicle or filler)
 */
async function fetchMyDriverLocation() {
    try {
        const res = await fetch('/api/locations/driver/me');
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Failed to fetch driver location');
        }
        return await res.json();
    } catch (err) {
        console.error('[TrackSphere Map] Driver location fetch error:', err);
        return null;
    }
}

/**
 * Plot or update vehicle / driver marker on the interactive map
 */
async function updateVehicleOnMap(vehicleId, registrationNumber, status, isFiller = false) {
    if (!map) return null;

    let loc = null;
    if (isFiller) {
        loc = await fetchMyDriverLocation();
    } else {
        loc = await fetchVehicleLocation(vehicleId);
    }

    if (!loc) return null;

    const latLng = [loc.latitude, loc.longitude];
    const timestampStr = new Date(loc.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

    const popupHtml = `
        <div style="color: #111827; font-family: 'Inter', sans-serif; min-width: 170px;">
            <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                <span style="font-size: 1.1rem;">${isFiller ? '🧑‍✈️' : '🚚'}</span>
                <strong style="font-size: 0.95rem; color: #111827;">${registrationNumber}</strong>
            </div>
            <div style="font-size: 11px; line-height: 1.5; color: #4b5563;">
                <div><strong>Status:</strong> <span style="color: ${status === 'ASSIGNED' ? '#0284c7' : '#059669'}; font-weight: 600;">${status}</span></div>
                <div><strong>Latitude:</strong> ${loc.latitude.toFixed(5)}</div>
                <div><strong>Longitude:</strong> ${loc.longitude.toFixed(5)}</div>
                <div><strong>Last Ping:</strong> ${timestampStr}</div>
            </div>
            <div style="margin-top: 8px; border-top: 1px solid #e5e7eb; padding-top: 6px; display: flex; gap: 4px;">
                <button onclick="toggleBreadcrumbHistory(${vehicleId})" style="flex: 1; font-size: 10px; padding: 4px 6px; background: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    📍 Trace Path
                </button>
            </div>
        </div>
    `;

    if (vehicleMarkers[vehicleId]) {
        vehicleMarkers[vehicleId].setLatLng(latLng);
        vehicleMarkers[vehicleId].setPopupContent(popupHtml);
    } else {
        const marker = L.marker(latLng, {
            icon: createVehicleIcon(registrationNumber, status, isFiller)
        }).addTo(map);

        marker.bindPopup(popupHtml);
        vehicleMarkers[vehicleId] = marker;
    }

    // Update telemetry coordinates panel if present
    const coordsEl = document.getElementById(`coords-${vehicleId}`);
    if (coordsEl) {
        coordsEl.textContent = `${loc.latitude.toFixed(4)}, ${loc.longitude.toFixed(4)}`;
    }

    return loc;
}

/**
 * Focus and zoom into a specific fleet unit or driver
 */
async function selectVehicleForTracking(vehicleId, reg, status, isFiller = false) {
    activeVehicleId = vehicleId;
    document.querySelectorAll('.vehicle-selector-item').forEach(el => el.classList.remove('selected'));
    const selectedEl = document.getElementById(`vehicle-item-${vehicleId}`);
    if (selectedEl) selectedEl.classList.add('selected');

    const loc = await updateVehicleOnMap(vehicleId, reg, status, isFiller);
    if (loc && map) {
        map.flyTo([loc.latitude, loc.longitude], 13, {
            animate: true,
            duration: 1.2
        });
        if (vehicleMarkers[vehicleId]) {
            vehicleMarkers[vehicleId].openPopup();
        }
    }
}

/**
 * Auto-fit map bounds across all currently active vehicle markers
 */
function fitMapToAllMarkers() {
    if (!map) return;
    const markers = Object.values(vehicleMarkers);
    if (markers.length === 0) return;

    if (markers.length === 1) {
        const latLng = markers[0].getLatLng();
        map.setView(latLng, 13);
        return;
    }

    const group = L.featureGroup(markers);
    map.fitBounds(group.getBounds(), {
        padding: [60, 60],
        maxZoom: 14,
        animate: true,
    });
}

/**
 * Fetch and toggle historical GPS breadcrumbs route for a vehicle
 */
async function toggleBreadcrumbHistory(vehicleId) {
    if (!map) return;

    // Toggle off if already displayed
    if (historyPolylines[vehicleId]) {
        map.removeLayer(historyPolylines[vehicleId]);
        delete historyPolylines[vehicleId];
        showToast('Cleared historical GPS breadcrumb path.', 'info');
        return;
    }

    try {
        const res = await fetch(`/api/locations/${vehicleId}/history?limit=30`);
        if (!res.ok) {
            throw new Error('Failed to retrieve telemetry history');
        }
        const historyData = await res.json();
        if (!historyData || historyData.length === 0) {
            showToast('No breadcrumb history points recorded yet.', 'info');
            return;
        }

        const latLngs = historyData.map(h => [h.latitude, h.longitude]);
        const polyline = L.polyline(latLngs, {
            color: '#38bdf8',
            weight: 4,
            opacity: 0.85,
            dashArray: '6, 8',
            lineJoin: 'round',
        }).addTo(map);

        historyPolylines[vehicleId] = polyline;
        map.fitBounds(polyline.getBounds(), { padding: [40, 40] });
        showToast(`Rendered ${historyData.length} GPS breadcrumb points!`, 'success');
    } catch (err) {
        showToast(err.message, 'error');
    }
}

/**
 * Simulate live GPS telemetry movement and push to backend
 */
async function simulateGpsPing(vehicleId, reg, status, isFiller = false) {
    let loc = null;
    if (isFiller) {
        loc = await fetchMyDriverLocation();
    } else {
        loc = await fetchVehicleLocation(vehicleId);
    }

    const currentLat = loc ? loc.latitude : 40.7580;
    const currentLon = loc ? loc.longitude : -73.9855;

    // Add natural vector movement jitter (approx 150-300m shift)
    const jitterLat = (Math.random() - 0.45) * 0.004;
    const jitterLon = (Math.random() - 0.45) * 0.004;
    const newLat = parseFloat((currentLat + jitterLat).toFixed(6));
    const newLon = parseFloat((currentLon + jitterLon).toFixed(6));

    try {
        const res = await fetch('/api/locations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vehicle_id: vehicleId,
                latitude: newLat,
                longitude: newLon,
            })
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Failed to submit GPS ping');
        }

        const saved = await res.json();
        await updateVehicleOnMap(vehicleId, reg, status, isFiller);
        showToast(`📍 Simulated GPS ping dispatched: [${newLat}, ${newLon}]`, 'success');
    } catch (err) {
        showToast(err.message, 'error');
    }
}
