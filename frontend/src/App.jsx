import React, { useState, useEffect } from "react";
import Papa from "papaparse"; // for CSV parsing

export default function CropSelector() {
  const [data, setData] = useState([]);
  const [states, setStates] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [currentYear, setCurrentYear] = useState("");

  const [selectedState, setSelectedState] = useState("");
  const [selectedDistrict, setSelectedDistrict] = useState("");

  const [suggestedCrops, setSuggestedCrops] = useState([]);

  // ---- DARK MODE STATE (non-intrusive) ----
  const [darkMode, setDarkMode] = useState(() => {
    try {
      const s = localStorage.getItem("darkMode");
      if (s !== null) return JSON.parse(s);
      return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    } catch {
      return false;
    }
  });

  // apply/remove 'dark' class on the html root and persist preference
  useEffect(() => {
    try {
      const root = document.documentElement;
      if (darkMode) root.classList.add("dark");
      else root.classList.remove("dark");
      localStorage.setItem("darkMode", JSON.stringify(darkMode));
    } catch (e) {
      // ignore in SSR or sandboxed env
    }
  }, [darkMode]);

  // ---- CSV loading + filtering logic ----
  useEffect(() => {
    Papa.parse("/crop_data.csv", {
      download: true,
      header: true,
      complete: (results) => {
        setData(results.data);
        const uniqueStates = [...new Set(results.data.map((d) => d.State))];
        const uniqueYears = [...new Set(results.data.map((d) => d.Year))];
        setStates(uniqueStates.sort());
        // Set the current year (2025) or the most recent year if 2025 is not available
        const currentYear = "2025";
        const availableYear = uniqueYears.includes(currentYear)
          ? currentYear
          : uniqueYears.sort((a, b) => b - a)[0]; // Fallback to most recent year
        setCurrentYear(availableYear);
      },
    });
  }, []);

  useEffect(() => {
    if (selectedState) {
      const uniqueDistricts = [
        ...new Set(
          data.filter((d) => d.State === selectedState).map((d) => d.District)
        ),
      ];
      setDistricts(uniqueDistricts.sort());
      setSelectedDistrict("");
      setSuggestedCrops([]);
    } else {
      setDistricts([]);
      setSelectedDistrict("");
      setSuggestedCrops([]);
    }
  }, [selectedState, data]);

  useEffect(() => {
    if (selectedState && selectedDistrict && currentYear) {
      // Filter data by state, district, and current or most recent year
      const filtered = data.filter(
        (d) =>
          d.State === selectedState &&
          d.District === selectedDistrict &&
          d.Year === currentYear
      );

      // Aggregate crops by total area to suggest top crops
      const cropStats = filtered.reduce((acc, row) => {
        const crop = row.Crop;
        if (!acc[crop]) {
          acc[crop] = {
            crop,
            area: parseFloat(row.Area) || 0,
            production: parseFloat(row.Production) || 0,
            yield: parseFloat(row.Yield) || 0,
            areaUnits: row["Area Units"],
            productionUnits: row["Production Units"],
            season: row.Season,
            count: 0,
          };
        }
        acc[crop].count += 1;
        acc[crop].area += parseFloat(row.Area) || 0;
        acc[crop].production += parseFloat(row.Production) || 0;
        return acc;
      }, {});

      // Sort crops by total area (descending) and limit to top suggestions
      const sortedCrops = Object.values(cropStats)
        .sort((a, b) => b.area - a.area)
        .slice(0, 5); // Suggest top 5 crops

      setSuggestedCrops(sortedCrops);
    } else {
      setSuggestedCrops([]);
    }
  }, [selectedState, selectedDistrict, currentYear, data]);

  // ---- UI (professional yet sexy design) ----
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50 dark:from-gray-900 dark:via-gray-800 dark:to-teal-900 p-6 md:p-10 lg:p-12 transition-all duration-700 ease-in-out">
      <div className="max-w-6xl mx-auto space-y-10 relative overflow-hidden">
        {/* Subtle animated background with a premium shimmer */}
        <div className="absolute inset-0 opacity-15 dark:opacity-10">
          <div className="absolute top-16 left-8 w-64 h-64 bg-teal-300/30 rounded-full mix-blend-overlay filter blur-2xl animate-pulse-slow"></div>
          <div className="absolute top-32 right-8 w-64 h-64 bg-teal-200/30 rounded-full mix-blend-overlay filter blur-2xl animate-pulse-slow delay-2000"></div>
          <div className="absolute bottom-12 left-12 w-64 h-64 bg-teal-100/30 rounded-full mix-blend-overlay filter blur-2xl animate-pulse-slow delay-4000"></div>
        </div>

        {/* Dark Mode Toggle (sleek and elegant) */}
        <div className="flex justify-end z-10">
          <button
            onClick={() => setDarkMode((v) => !v)}
            aria-label="Toggle dark mode"
            className="group relative inline-flex items-center gap-2 px-5 py-2 rounded-lg bg-white/10 dark:bg-gray-800/50 backdrop-blur-md text-sm font-semibold text-gray-700 dark:text-gray-200 shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 border border-gray-200/20 dark:border-gray-700/40 hover:border-teal-400/50"
          >
            <span className={`transition-transform duration-300 ${darkMode ? 'rotate-180' : ''}`}>
              {darkMode ? "☀️" : "🌙"}
            </span>
            <span className="hidden md:inline">{darkMode ? "Light Mode" : "Dark Mode"}</span>
            <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-teal-400/10 to-teal-300/10 scale-0 group-hover:scale-100 transition-transform duration-300" />
          </button>
        </div>

        <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-center bg-gradient-to-r from-teal-600 to-gray-800 dark:from-teal-400 dark:to-gray-600 bg-clip-text text-transparent drop-shadow-md animate-fade-in-slow">
          🌱 Indian Crop Recommender
        </h1>
        <p className="text-center text-lg md:text-xl text-gray-600 dark:text-gray-300 max-w-xl mx-auto opacity-0 animate-fade-in-slow delay-300">
          Discover the best crops to grow in your region based on recent data.
        </p>

        {/* Professional Dropdown Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8 z-10">
          <div className="group relative bg-white/20 dark:bg-gray-800/40 backdrop-blur-lg rounded-xl shadow-xl p-5 md:p-6 border border-gray-100/10 dark:border-gray-700/30 hover:border-teal-400/30 transition-all duration-500 hover:shadow-teal-500/20 hover:-translate-y-1">
            <label className="block text-xs md:text-sm font-bold text-gray-700 dark:text-gray-200 mb-3 flex items-center gap-1.5">
              <span className="text-teal-500">📍</span> State
            </label>
            <select
              className="w-full p-3 md:p-4 rounded-lg bg-white/10 dark:bg-gray-700/30 backdrop-blur-sm border border-gray-200/10 dark:border-gray-600/30 shadow-inner focus:ring-2 focus:ring-teal-400/40 dark:focus:ring-teal-300/40 transition-all duration-300 text-gray-800 dark:text-gray-100 font-medium hover:bg-white/15 dark:hover:bg-gray-700/40"
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
            >
              <option value="">Select a State</option>
              {states.map((s, i) => (
                <option key={i} value={s}>
                  {s}
                </option>
              ))}
            </select>
            <div className="absolute -inset-1 bg-gradient-to-r from-teal-400/10 to-teal-300/10 rounded-xl -z-10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-sm" />
          </div>

          <div className="group relative bg-white/20 dark:bg-gray-800/40 backdrop-blur-lg rounded-xl shadow-xl p-5 md:p-6 border border-gray-100/10 dark:border-gray-700/30 hover:border-teal-400/30 transition-all duration-500 hover:shadow-teal-500/20 hover:-translate-y-1">
            <label className="block text-xs md:text-sm font-bold text-gray-700 dark:text-gray-200 mb-3 flex items-center gap-1.5">
              <span className="text-teal-500">🏛️</span> District
            </label>
            <select
              className="w-full p-3 md:p-4 rounded-lg bg-white/10 dark:bg-gray-700/30 backdrop-blur-sm border border-gray-200/10 dark:border-gray-600/30 shadow-inner focus:ring-2 focus:ring-teal-400/40 dark:focus:ring-teal-300/40 transition-all duration-300 text-gray-800 dark:text-gray-100 font-medium hover:bg-white/15 dark:hover:bg-gray-700/40 disabled:bg-gray-200/10 dark:disabled:bg-gray-800/40 disabled:cursor-not-allowed disabled:opacity-50"
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
              disabled={!districts.length}
            >
              <option value="">Select District</option>
              {districts.map((d, i) => (
                <option key={i} value={d}>
                  {d}
                </option>
              ))}
            </select>
            <div className="absolute -inset-1 bg-gradient-to-r from-teal-400/10 to-teal-300/10 rounded-xl -z-10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-sm" />
          </div>
        </div>

        {/* Professional Results Section */}
        {suggestedCrops.length > 0 && (
          <div className="animate-slide-up-slow z-10">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-teal-600 to-gray-800 dark:from-teal-400 dark:to-gray-600 bg-clip-text text-transparent mb-6 text-center drop-shadow-md">
              📊 Crop Suggestions for {selectedDistrict}, {selectedState}
            </h2>
            <div className="bg-white/15 dark:bg-gray-800/40 backdrop-blur-lg rounded-xl shadow-2xl border border-gray-100/5 dark:border-gray-700/20 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gradient-to-r from-teal-500/10 to-teal-300/10 dark:from-teal-500/20 dark:to-teal-300/20">
                    <tr>
                      <th className="p-4 md:p-5 text-left font-semibold text-gray-700 dark:text-gray-200 uppercase tracking-wide text-xs md:text-sm">Crop</th>
                      <th className="p-4 md:p-5 text-left font-semibold text-gray-700 dark:text-gray-200 uppercase tracking-wide text-xs md:text-sm">Season</th>
                      <th className="p-4 md:p-5 text-left font-semibold text-gray-700 dark:text-gray-200 uppercase tracking-wide text-xs md:text-sm">Area</th>
                      <th className="p-4 md:p-5 text-left font-semibold text-gray-700 dark:text-gray-200 uppercase tracking-wide text-xs md:text-sm">Production</th>
                      <th className="p-4 md:p-5 text-left font-semibold text-gray-700 dark:text-gray-200 uppercase tracking-wide text-xs md:text-sm">Yield</th>
                    </tr>
                  </thead>
                  <tbody>
                    {suggestedCrops.map((row, i) => (
                      <tr
                        key={i}
                        className="border-b border-gray-100/5 dark:border-gray-700/20 hover:bg-teal-50/10 dark:hover:bg-teal-900/10 transition-all duration-300 hover:scale-[1.02]"
                      >
                        <td className="p-4 md:p-5 font-medium text-gray-800 dark:text-gray-100">{row.crop}</td>
                        <td className="p-4 md:p-5 text-gray-600 dark:text-gray-300">{row.season}</td>
                        <td className="p-4 md:p-5 text-gray-600 dark:text-gray-300">
                          {row.area.toFixed(2)} {row.areaUnits}
                        </td>
                        <td className="p-4 md:p-5 text-gray-600 dark:text-gray-300">
                          {row.production.toFixed(2)} {row.productionUnits}
                        </td>
                        <td className="p-4 md:p-5 font-medium text-teal-600 dark:text-teal-400">{row.yield.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* No data message with professional styling */}
        {selectedState && selectedDistrict && suggestedCrops.length === 0 && (
          <div className="text-center py-10 animate-fade-in-slow">
            <p className="text-lg md:text-xl text-gray-500 dark:text-gray-400 font-medium">No crop data available for the selected region. Try another combination! 🌱</p>
          </div>
        )}
      </div>

      {/* Custom CSS for animations and effects */}
      <style jsx>{`
        @keyframes pulse-slow {
          0%, 100% { transform: scale(1); opacity: 0.3; }
          50% { transform: scale(1.05); opacity: 0.5; }
        }
        .animate-pulse-slow { animation: pulse-slow 8s infinite ease-in-out; }
        .delay-2000 { animation-delay: 2s; }
        .delay-4000 { animation-delay: 4s; }
        @keyframes fade-in-slow {
          from { opacity: 0; transform: translateY(15px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in-slow { animation: fade-in-slow 1s ease-out forwards; }
        .delay-300 { animation-delay: 0.3s; }
        @keyframes slide-up-slow {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-slide-up-slow { animation: slide-up-slow 0.8s ease-out; }
      `}</style>
    </div>
  );
}
