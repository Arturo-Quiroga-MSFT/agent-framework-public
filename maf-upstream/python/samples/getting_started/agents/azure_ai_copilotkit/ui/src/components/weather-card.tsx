"use client";

interface WeatherData {
  location: string;
  temperature: number;
  condition: string;
  humidity: number;
  wind_speed: number;
  feels_like: number;
  error?: string;
}

function SunIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-12 h-12 text-yellow-300">
      <circle cx="12" cy="12" r="5" />
      <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" strokeWidth="2" stroke="currentColor" />
    </svg>
  );
}

function CloudIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-12 h-12 text-gray-400">
      <path d="M18 10.5c0 .828-.672 1.5-1.5 1.5h-.5c-.276 0-.5.224-.5.5v1c0 .276.224.5.5.5h2.5c1.381 0 2.5-1.119 2.5-2.5S19.881 9 18.5 9h-.5c-.276 0-.5-.224-.5-.5 0-2.485-2.015-4.5-4.5-4.5S8.5 6.015 8.5 8.5c0 .276-.224.5-.5.5H7c-1.657 0-3 1.343-3 3s1.343 3 3 3h2.5c.276 0 .5.224.5.5v1c0 .276-.224.5-.5.5H7c-2.761 0-5-2.239-5-5s2.239-5 5-5h.05c.232-3.609 3.256-6.5 6.95-6.5 3.866 0 7 3.134 7 7v.5z"/>
    </svg>
  );
}

function getWeatherIcon(condition: string) {
  const lower = condition.toLowerCase();
  if (lower.includes("clear") || lower.includes("sun")) {
    return <SunIcon />;
  }
  return <CloudIcon />;
}

export function WeatherCard({ weather }: { weather: WeatherData }) {
  if (weather.error) {
    return (
      <div className="rounded-xl shadow-lg bg-red-50 p-6 max-w-md w-full border border-red-200">
        <h3 className="text-lg font-bold text-red-800">{weather.location}</h3>
        <p className="text-red-600 mt-2">{weather.error}</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl shadow-xl bg-gradient-to-br from-blue-500 to-indigo-600 p-6 max-w-md w-full">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-2xl font-bold text-white capitalize">{weather.location}</h3>
          <p className="text-blue-100 text-sm">Current Weather</p>
        </div>
        {getWeatherIcon(weather.condition)}
      </div>
      
      <div className="mb-4">
        <div className="text-5xl font-bold text-white">{Math.round(weather.temperature)}°C</div>
        <div className="text-lg text-blue-100 capitalize mt-1">{weather.condition}</div>
      </div>
      
      <div className="pt-4 border-t border-blue-400">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-blue-100 text-xs uppercase tracking-wide">Humidity</p>
            <p className="text-white font-semibold text-lg">{weather.humidity}%</p>
          </div>
          <div>
            <p className="text-blue-100 text-xs uppercase tracking-wide">Wind</p>
            <p className="text-white font-semibold text-lg">{weather.wind_speed} m/s</p>
          </div>
          <div>
            <p className="text-blue-100 text-xs uppercase tracking-wide">Feels Like</p>
            <p className="text-white font-semibold text-lg">{Math.round(weather.feels_like)}°C</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export function CompareWeatherCard({ cities }: { cities: WeatherData[] }) {
  return (
    <div className="space-y-4 w-full max-w-4xl">
      <h2 className="text-xl font-bold text-gray-800 mb-4">Weather Comparison</h2>
      <div className="grid md:grid-cols-2 gap-4">
        {cities.map((weather, idx) => (
          <WeatherCard key={idx} weather={weather} />
        ))}
      </div>
    </div>
  );
}
