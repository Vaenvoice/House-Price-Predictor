import { useEffect, useState } from "react";
import apiClient from "@/api/client";
import { Card } from "@/components/ui/Card";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Custom SVG Pin Creator
const createCustomIcon = (color) => L.divIcon({
  html: `
    <div style="filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3))">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 21.7C16 17.5 20 13.5 20 8.5C20 4.1 16.4 0.5 12 0.5C7.6 0.5 4 4.1 4 8.5C4 13.5 8 17.5 12 21.7Z" fill="${color}" stroke="white" stroke-width="1.5"/>
        <circle cx="12" cy="8.5" r="3" fill="white"/>
      </svg>
    </div>
  `,
  className: "custom-pin",
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32]
});

export default function LocationIntel() {
  const [data, setData] = useState([]);

  useEffect(() => {
    apiClient.get('/analytics/location-pricing').then(res => setData(res.data)).catch(console.error);
  }, []);

  // India center coords
  const center = [20.5937, 78.9629];

  return (
    <div className="space-y-10 pb-20 h-full flex flex-col">
      <div className="flex flex-col gap-1 shrink-0">
        <h1 className="text-2xl font-bold tracking-tight">Geospatial Intelligence</h1>
        <p className="text-muted-foreground text-sm">Urban tier pricing density and market concentration.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10 flex-1 min-h-0">
        
        {/* Map Panel */}
        <Card className="lg:col-span-2 overflow-hidden relative flex flex-col p-0" delay={0.1}>
          <div className="w-full h-[500px] lg:h-full z-0">
            <MapContainer center={center} zoom={5} style={{ height: "100%", width: "100%", background: "#0a0f1e" }}>
              <TileLayer
                // Dark mode styled map tiles from CartoDB
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
              />
              
              {data.filter(d => d.lat && d.lng).map((loc, i) => {
                const color = loc.type === 'tier-1' ? '#3b82f6' : loc.type === 'tier-2' ? '#8b5cf6' : '#10b981';
                return (
                  <Marker
                    key={i}
                    position={[loc.lat, loc.lng]}
                    icon={createCustomIcon(color)}
                  >
                    <Popup className="custom-popup">
                      <div className="font-sans min-w-[150px] p-1">
                        <h4 className="font-bold text-slate-900 text-base mb-1">{loc.label}</h4>
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-xs text-slate-500 uppercase font-bold">{loc.type}</span>
                          <span className="text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full">{loc.count} units</span>
                        </div>
                        <div className="text-base font-bold text-foreground border-t border-border pt-1">
                          ₹{(loc.avg_price/100000).toFixed(1)}L <span className="text-[10px] font-normal text-muted-foreground uppercase">avg</span>
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                );
              })}
            </MapContainer>
          </div>
        </Card>

        {/* List Panel */}
        <Card className="flex flex-col h-full overflow-hidden p-0" delay={0.2}>
          <div className="p-6 border-b border-border bg-card">
            <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">City Intelligence</h3>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-1">
            {data.map((loc, i) => (
              <div key={i} className="flex justify-between items-center p-4 hover:bg-muted rounded-lg transition-all duration-200 group cursor-default">
                <div className="flex flex-col">
                  <span className="text-xs font-bold text-foreground">{loc.location}</span>
                  <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">{loc.count} Properties</span>
                </div>
                <div className="text-right">
                  <div className="text-xs font-bold text-foreground">₹{(loc.avg_price/100000).toFixed(1)}L</div>
                  <div className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest">{loc.type}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
