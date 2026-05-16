export function getSunriseSunset(date, lat, lon) {
  if (typeof globalThis.SunCalc !== "undefined") {
    const times = globalThis.SunCalc.getTimes(date, lat, lon);
    return { sunrise: times.sunrise, sunset: times.sunset };
  }

  const sunrise = new Date(date);
  sunrise.setHours(6, 0, 0, 0);
  const sunset = new Date(date);
  sunset.setHours(18, 0, 0, 0);
  return { sunrise, sunset };
}

export function agniCurve(hour) {
  const t = (hour - 6) / 12;
  if (t < 0 || t > 1) return 0;
  return Math.sin(Math.PI * t);
}

export function getAbhijitWindow(sunrise, sunset) {
  const midday = new Date((sunrise.getTime() + sunset.getTime()) / 2);
  return {
    start: new Date(midday.getTime() - 24 * 60000),
    end: new Date(midday.getTime() + 24 * 60000)
  };
}
