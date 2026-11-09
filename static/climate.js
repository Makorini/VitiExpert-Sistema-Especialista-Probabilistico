/* ============================================================
   VITIEXPERT — CLIMA (VERSÃO 4 • TELA INTEIRA)
   Este script atua SOMENTE na página /climate.
   Fonte: Open-Meteo (previsão) e Open-Meteo Geocoding (cidades).
   O cenário muda automaticamente conforme clima e horário locais.
   ============================================================ */
(() => {
    'use strict';

    const page = document.getElementById('climate-page');
    if (!page) return;

    const locale = ['pt', 'en', 'es'].includes(page.dataset.lang) ? page.dataset.lang : 'pt';
    const languageTag = { pt: 'pt-BR', en: 'en-US', es: 'es-ES' }[locale];
    const DEFAULT_CITY = {
        name: 'Videira', admin1: 'Santa Catarina', country: 'Brasil',
        country_code: 'BR', latitude: -27.00833, longitude: -51.15167,
        timezone: 'America/Sao_Paulo'
    };
    const CITY_STORAGE_KEY = 'vitiexpert-climate-city';

    const STRINGS = {
        pt: {
            top_eyebrow: 'CLIMA E CONDIÇÕES EM TEMPO REAL', intro_body: 'Condições meteorológicas em tempo real para apoiar o manejo do seu vinhedo.', maximum: 'Máx:', minimum: 'Mín:', hour_title: 'Previsão horária', now: 'Agora', location_eyebrow: 'LOCALIZAÇÃO', where: 'Onde você quer consultar o clima?',
            back_videira: 'Voltar para Videira', search_label: 'Pesquisar cidade ou região',
            search_placeholder: 'Buscar cidade ou região',
            search_button: 'Buscar', live_label: 'CLIMA ATUAL',
            loading: 'Consultando previsão...', awaiting_update: 'Aguardando informações meteorológicas', feels_like: 'Sensação térmica',
            humidity: 'Umidade', wind: 'Vento', rain_chance: 'Chance de chuva',
            week_eyebrow: 'OLHANDO PARA OS PRÓXIMOS DIAS', week_title: 'Previsão para os próximos 7 dias',
            forecast_note: 'Previsões podem mudar. Dados meteorológicos de Open-Meteo.', source: 'Fonte meteorológica',
            source_extra: 'Dados atualizados mediante conexão à internet.',
            searching: 'Buscando cidades...', no_city: 'Nenhuma cidade encontrada. Tente outro nome.',
            type_more: 'Digite pelo menos 2 caracteres para buscar uma cidade.',
            choose_city: 'Escolha uma cidade da lista para ver a previsão.',
            city_error: 'Não foi possível pesquisar cidades. Verifique sua conexão e tente novamente.',
            weather_error: 'Não foi possível carregar a previsão. Confira sua conexão e tente novamente.',
            updated: 'Dados de', today: 'Hoje', rain: 'chuva',
            sunny: 'Céu limpo', partly: 'Parcialmente nublado', cloudy: 'Nublado',
            foggy: 'Neblina', drizzle: 'Garoa', rainy: 'Chuva', snowy: 'Neve',
            stormy: 'Tempestade', unknown: 'Condição indisponível', local_time: 'Horário local'
        },
        en: {
            top_eyebrow: 'REAL-TIME WEATHER AND CONDITIONS', intro_body: 'Real-time weather conditions to support the care of your vineyard.', maximum: 'High:', minimum: 'Low:', hour_title: 'Hourly forecast', now: 'Now', location_eyebrow: 'LOCATION', where: 'Where would you like to check the weather?',
            back_videira: 'Back to Videira', search_label: 'Search for a city or region',
            search_placeholder: 'Search city or region',
            search_button: 'Search', live_label: 'CURRENT WEATHER',
            loading: 'Loading forecast...', awaiting_update: 'Waiting for weather data', feels_like: 'Feels like',
            humidity: 'Humidity', wind: 'Wind', rain_chance: 'Chance of rain',
            week_eyebrow: 'LOOKING AHEAD', week_title: '7-day weather forecast',
            forecast_note: 'Forecasts may change. Weather data by Open-Meteo.', source: 'Weather source',
            source_extra: 'Updated data requires an internet connection.',
            searching: 'Searching for cities...', no_city: 'No cities found. Try a different name.',
            type_more: 'Enter at least 2 characters to search for a city.',
            choose_city: 'Select a city from the list to see its forecast.',
            city_error: 'Unable to search cities. Check your connection and retry.',
            weather_error: 'Unable to load the forecast. Check your connection and retry.',
            updated: 'Weather data from', today: 'Today', rain: 'rain',
            sunny: 'Clear sky', partly: 'Partly cloudy', cloudy: 'Overcast',
            foggy: 'Fog', drizzle: 'Drizzle', rainy: 'Rain', snowy: 'Snow',
            stormy: 'Thunderstorm', unknown: 'Condition unavailable', local_time: 'Local time'
        },
        es: {
            top_eyebrow: 'CLIMA Y CONDICIONES EN TIEMPO REAL', intro_body: 'Condiciones meteorológicas en tiempo real para cuidar tu viñedo.', maximum: 'Máx:', minimum: 'Mín:', hour_title: 'Pronóstico por horas', now: 'Ahora', location_eyebrow: 'UBICACIÓN', where: '¿Dónde quieres consultar el clima?',
            back_videira: 'Volver a Videira', search_label: 'Buscar ciudad o región',
            search_placeholder: 'Buscar ciudad o región',
            search_button: 'Buscar', live_label: 'CLIMA ACTUAL',
            loading: 'Consultando pronóstico...', awaiting_update: 'Esperando datos meteorológicos', feels_like: 'Sensación térmica',
            humidity: 'Humedad', wind: 'Viento', rain_chance: 'Probabilidad de lluvia',
            week_eyebrow: 'PRÓXIMOS DÍAS', week_title: 'Pronóstico de los próximos 7 días',
            forecast_note: 'Los pronósticos pueden cambiar. Datos meteorológicos de Open-Meteo.', source: 'Fuente meteorológica',
            source_extra: 'Los datos actualizados requieren conexión a internet.',
            searching: 'Buscando ciudades...', no_city: 'No se encontraron ciudades. Prueba con otro nombre.',
            type_more: 'Escribe al menos 2 caracteres para buscar una ciudad.',
            choose_city: 'Selecciona una ciudad de la lista para ver el pronóstico.',
            city_error: 'No se pudieron buscar ciudades. Comprueba tu conexión.',
            weather_error: 'No se pudo cargar el pronóstico. Comprueba tu conexión.',
            updated: 'Datos de', today: 'Hoy', rain: 'lluvia',
            sunny: 'Cielo despejado', partly: 'Parcialmente nublado', cloudy: 'Nublado',
            foggy: 'Niebla', drizzle: 'Llovizna', rainy: 'Lluvia', snowy: 'Nieve',
            stormy: 'Tormenta', unknown: 'Condición no disponible', local_time: 'Hora local'
        }
    };
    const t = STRINGS[locale];
    const byId = (id) => document.getElementById(id);
    const form = byId('climate-search-form');
    const search = byId('climate-city-search');
    const results = byId('climate-search-results');
    const status = byId('climate-search-status');
    const sceneEl = byId('climate-scene');
    const climateTitle = byId('climate-title-text');
    if (climateTitle) climateTitle.textContent = {pt:'Clima',en:'Weather',es:'Clima'}[locale];

    let city = readSavedCity() || DEFAULT_CITY;
    let weather = null;
    let queryTimer = null;
    let locationController = null;
    let weatherController = null;
    let weatherRequest = 0;
    let locationRequest = 0;

    // Aplica traduções apenas aos elementos próprios do módulo de clima.
    document.querySelectorAll('[data-w-i18n]').forEach((element) => {
        const text = t[element.dataset.wI18n];
        if (text) element.textContent = text;
    });
    document.querySelectorAll('[data-w-placeholder]').forEach((element) => {
        const text = t[element.dataset.wPlaceholder];
        if (text) element.placeholder = text;
    });

    function numeric(value) {
        return typeof value === 'number' && Number.isFinite(value);
    }
    function numberText(value, unit = '', digits = 0) {
        if (!numeric(value)) return '--' + unit;
        return new Intl.NumberFormat(languageTag, {
            minimumFractionDigits: digits, maximumFractionDigits: digits
        }).format(value) + unit;
    }
    function text(id, value) {
        const element = byId(id);
        if (element) element.textContent = value;
    }
    const cityButton = byId('climate-default-city');
    if (cityButton) { cityButton.setAttribute('title',t.back_videira);cityButton.setAttribute('aria-label',t.back_videira); }
    function validCity(value) {
        return value && typeof value.name === 'string' && value.name.length < 150 &&
            numeric(value.latitude) && numeric(value.longitude) &&
            Math.abs(value.latitude) <= 90 && Math.abs(value.longitude) <= 180 &&
            (!value.timezone || (typeof value.timezone === 'string' && value.timezone.length < 100));
    }
    function readSavedCity() {
        try {
            const saved = JSON.parse(localStorage.getItem(CITY_STORAGE_KEY));
            return validCity(saved) ? saved : null;
        } catch (_) { return null; }
    }
    function saveCity(value) {
        try { localStorage.setItem(CITY_STORAGE_KEY, JSON.stringify(value)); } catch (_) { /* armazenamento opcional */ }
    }
    function cityDetail(value) {
        const locality = [value.admin1, value.country].filter(Boolean);
        return locality.join(' · ');
    }
    function cityLabel(value) {
        const region = value.country_code === 'BR' && value.admin1 === 'Santa Catarina'
            ? 'SC' : (value.admin1 || value.country || '');
        return [value.name, region].filter(Boolean).join(', ');
    }
    function condition(code) {
        if (code === 0 || code === 1) return 'sunny';
        if (code === 2) return 'partly';
        if (code === 3) return 'cloudy';
        if (code === 45 || code === 48) return 'foggy';
        if ([51, 53, 55, 56, 57].includes(code)) return 'drizzle';
        if ([61, 63, 65, 66, 67, 80, 81, 82].includes(code)) return 'rainy';
        if ([71, 73, 75, 77, 85, 86].includes(code)) return 'snowy';
        if ([95, 96, 99].includes(code)) return 'stormy';
        return 'unknown';
    }
    function sceneFor(code, day) {
        const conditionName = condition(code);
        let scene = 'partly';
        if (conditionName === 'sunny') scene = 'clear';
        if (conditionName === 'cloudy') scene = 'cloudy';
        if (conditionName === 'foggy') scene = 'fog';
        if (conditionName === 'drizzle' || conditionName === 'rainy') scene = 'rain';
        if (conditionName === 'snowy') scene = 'snow';
        if (conditionName === 'stormy') scene = 'storm';
        return scene + (day ? '-day' : '-night');
    }
    function iconMarkup(name, day = true) {
        const sun = '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M4.9 4.9l1.5 1.5m11.2 11.2 1.5 1.5M19.1 4.9l-1.5 1.5M6.4 17.6l-1.5 1.5"/>';
        const moon = '<path d="M20.5 15.7A8.5 8.5 0 0 1 8.3 3.5 8.5 8.5 0 1 0 20.5 15.7Z"/>';
        const cloud = '<path d="M6 18h12a4 4 0 0 0 .2-8 6.5 6.5 0 0 0-12.5 1.6A3.2 3.2 0 0 0 6 18Z"/>';
        const partial = (day ? '<circle cx="8" cy="7" r="3"/><path d="M8 1v2M2 7h2M3.5 2.5 5 4"/>' : '<path d="M11 2a5 5 0 0 0 4 7 5.5 5.5 0 1 1-4-7"/>') + '<path d="M6 20h12a3.8 3.8 0 0 0 0-7.6h-.5a5.9 5.9 0 0 0-11.1 1.2A3.3 3.3 0 0 0 6 20Z"/>';
        const outlines = {
            sunny: day ? sun : moon,
            partly: partial,
            cloudy: cloud,
            foggy: cloud + '<path d="M4 21h16M2 23h13"/>',
            drizzle: cloud + '<path d="m7 21-.5 1m5.5-1-.5 1m5.5-1-.5 1"/>',
            rainy: cloud + '<path d="m8 20-1 3m6-3-1 3m6-3-1 3"/>',
            stormy: cloud + '<path d="m13 18-3 4h3l-1 2"/>',
            snowy: cloud + '<path d="M7 21h.01M12 22h.01M17 21h.01"/>',
            unknown: cloud
        };
        return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + (outlines[name] || cloud) + '</svg>';
    }
    function renderScene() {
        const data = weather?.current || {};
        // Ao ficar sem internet, a foto ainda respeita o horário local aproximado.
        let isDay = data.is_day === 1 || data.is_day === true;
        if (data.is_day == null) {
            try {
                const localHour = Number(new Intl.DateTimeFormat('en-GB', {
                    hour: '2-digit', hourCycle: 'h23', timeZone: city.timezone || 'America/Sao_Paulo'
                }).format(new Date()));
                isDay = localHour >= 6 && localHour < 19;
            } catch (_) { isDay = true; }
        }
        // Condição meteorológica tem prioridade sobre calor. Em céu limpo ou
        // parcialmente nublado com 30 ºC ou mais, mostra a paisagem de calor.
        const kind = condition(data.weather_code);
        const isHot = isDay && numeric(data.temperature_2m) && data.temperature_2m >= 30 &&
            ['sunny', 'partly'].includes(kind);
        const realScene = isHot ? 'hot-day' : sceneFor(data.weather_code, isDay);
        sceneEl.dataset.scene = realScene;
        byId('climate-current-icon').innerHTML = iconMarkup(condition(data.weather_code), isDay);
    }
    function weekday(date, index) {
        if (index === 0) return t.today;
        // Usa UTC ao formatar uma data civil para não deslocar o dia no fuso do visitante.
        return new Intl.DateTimeFormat(languageTag, { weekday: 'short', timeZone: 'UTC' })
            .format(new Date(date + 'T12:00:00Z')).replace('.', '');
    }
    function chanceCurrentHour(dataset) {
        const currentTime = dataset.current?.time;
        const hourly = dataset.hourly;
        if (currentTime && Array.isArray(hourly?.time) && Array.isArray(hourly?.precipitation_probability)) {
            const hour = currentTime.slice(0, 13);
            const index = hourly.time.findIndex((time) => time.slice(0, 13) === hour);
            if (index >= 0 && numeric(hourly.precipitation_probability[index])) {
                return hourly.precipitation_probability[index];
            }
        }
        return Array.isArray(dataset.daily?.precipitation_probability_max)
            ? dataset.daily.precipitation_probability_max[0] : null;
    }
    function renderWeek(dataset) {
        const daily = dataset.daily || {};
        const grid = byId('climate-week-grid');
        grid.replaceChildren();
        if (!Array.isArray(daily.time)) return;
        daily.time.slice(0, 7).forEach((date, index) => {
            const kind = condition(daily.weather_code?.[index]);
            const card = document.createElement('article');
            card.className = 'climate-day';
            const day = document.createElement('span');
            day.className = 'climate-day-name';
            day.textContent = weekday(date, index);
            const dateLabel = document.createElement('span');
            dateLabel.className = 'climate-day-date';
            dateLabel.textContent = new Intl.DateTimeFormat(languageTag, { day: 'numeric', month: 'short', timeZone: 'UTC' })
                .format(new Date(date + 'T12:00:00Z'));
            const icon = document.createElement('span');
            icon.className = 'climate-day-icon';
            icon.innerHTML = iconMarkup(kind);
            icon.setAttribute('aria-label', t[kind]);
            const temps = document.createElement('div');
            temps.className = 'climate-day-temps';
            const highest = document.createElement('span');
            highest.textContent = numberText(daily.temperature_2m_max?.[index], '°C');
            const lowest = document.createElement('span');
            lowest.textContent = numberText(daily.temperature_2m_min?.[index], '°C');
            temps.append(highest, lowest);
            const rain = document.createElement('span');
            rain.className = 'climate-day-rain';
            rain.textContent = '☂ ' + numberText(daily.precipitation_probability_max?.[index], '%');
            rain.setAttribute('aria-label', t.rain_chance + ': ' + rain.textContent);
            card.append(day, dateLabel, icon, temps, rain);
            grid.appendChild(card);
        });
    }
    function renderHours(dataset) {
        const hourly = dataset.hourly || {};
        const grid = byId('climate-hour-grid');
        grid.replaceChildren();
        if (!Array.isArray(hourly.time)) return;
        // Open-Meteo retorna datas/hora local da cidade selecionada.
        const currentTime = dataset.current?.time || '';
        const index = Math.max(0, hourly.time.findIndex((value) =>
            value.slice(0, 13) === currentTime.slice(0, 13)));
        hourly.time.slice(index, index + 13).forEach((hour, offset) => {
            const idx = index + offset;
            const card = document.createElement('article');
            card.className = 'climate-hour';
            const hourName = document.createElement('span');
            hourName.className = 'climate-hour-time';
            hourName.textContent = offset === 0 ? t.now : hour.slice(11,13) + 'h';
            const icon = document.createElement('span');
            icon.className = 'climate-hour-icon';
            icon.innerHTML = iconMarkup(condition(hourly.weather_code?.[idx]),
                hourly.is_day?.[idx] === 1 || hourly.is_day?.[idx] === true);
            const temp = document.createElement('strong');
            temp.className = 'climate-hour-temp';
            temp.textContent = numberText(hourly.temperature_2m?.[idx], '°C');
            card.append(hourName, icon, temp);
            grid.appendChild(card);
        });
    }
    function displayWeather(dataset) {
        const current = dataset.current || {};
        text('climate-city-name', cityLabel(city));
        text('climate-search-city', cityLabel(city));
        text('climate-current-temperature', numberText(current.temperature_2m));
        text('climate-current-description', t[condition(current.weather_code)]);
        const max = dataset.daily?.temperature_2m_max?.[0];
        const min = dataset.daily?.temperature_2m_min?.[0];
        text('climate-max', numberText(max, '°C'));
        text('climate-min', numberText(min, '°C'));
        text('climate-feels', numberText(current.apparent_temperature, '°C'));
        text('climate-humidity', numberText(current.relative_humidity_2m, '%'));
        text('climate-wind', numberText(current.wind_speed_10m, ' km/h'));
        text('climate-rain', numberText(chanceCurrentHour(dataset), '%'));
        const local = typeof current.time === 'string' && current.time.includes('T')
            ? current.time.split('T')[1].slice(0, 5) : '--:--';
        text('climate-city-time', t.local_time + ' · ' + local);
        text('climate-last-update', t.updated + ' ' + (current.time ? current.time.replace('T', ' · ') : '--'));
        renderWeek(dataset);
        renderHours(dataset);
        renderScene();
    }
    async function loadWeather() {
        weatherRequest += 1;
        const requestId = weatherRequest;
        if (weatherController) weatherController.abort();
        weatherController = new AbortController();
        const selected = city;
        text('climate-city-name', cityLabel(selected));
        text('climate-search-city', cityLabel(selected));
        text('climate-current-description', t.loading);
        const params = new URLSearchParams({
            latitude: String(selected.latitude), longitude: String(selected.longitude),
            current: 'temperature_2m,relative_humidity_2m,apparent_temperature,is_day,weather_code,wind_speed_10m',
            hourly: 'temperature_2m,weather_code,is_day,precipitation_probability',
            daily: 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max',
            timezone: 'auto', forecast_days: '7'
        });
        try {
            const response = await fetch('https://api.open-meteo.com/v1/forecast?' + params, {
                signal: weatherController.signal
            });
            if (!response.ok) throw new Error('weather HTTP ' + response.status);
            const data = await response.json();
            if (!data.current || !data.daily || !Array.isArray(data.daily.time)) throw new Error('Invalid weather data');
            if (requestId !== weatherRequest) return;
            weather = data;
            displayWeather(data);
            status.textContent = '';
        } catch (error) {
            if (error.name === 'AbortError' || requestId !== weatherRequest) return;
            weather = null;
            text('climate-current-temperature', '--');
            text('climate-current-description', t.weather_error);
            text('climate-max', '--°C');
            text('climate-min', '--°C');
            ['climate-feels', 'climate-humidity', 'climate-wind', 'climate-rain'].forEach((id) => text(id, '--'));
            text('climate-last-update', t.awaiting_update);
            text('climate-city-time', '--:--');
            byId('climate-week-grid').replaceChildren();
            byId('climate-hour-grid').replaceChildren();
            renderScene();
            status.textContent = t.weather_error;
        }
    }
    function selectCity(result) {
        if (!validCity(result)) return;
        clearTimeout(queryTimer);
        if (locationController) locationController.abort();
        locationRequest += 1;
        city = {
            name: result.name, admin1: result.admin1 || '', country: result.country || '',
            country_code: result.country_code || '', latitude: result.latitude,
            longitude: result.longitude, timezone: result.timezone || ''
        };
        saveCity(city);
        search.value = '';
        results.hidden = true;
        results.replaceChildren();
        search.setAttribute('aria-expanded', 'false');
        status.textContent = '';
        loadWeather();
    }
    function renderCityOptions(items) {
        results.replaceChildren();
        items.forEach((item) => {
            const option = document.createElement('button');
            option.type = 'button';
            option.setAttribute('role', 'option');
            const name = document.createElement('strong');
            name.textContent = item.name;
            const detail = document.createElement('span');
            detail.textContent = cityDetail(item);
            option.append(name, detail);
            option.addEventListener('click', () => selectCity(item));
            results.appendChild(option);
        });
        results.hidden = items.length === 0;
        search.setAttribute('aria-expanded', String(items.length > 0));
    }
    async function findCities(query) {
        if (locationController) locationController.abort();
        locationRequest += 1;
        const requestId = locationRequest;
        if (query.trim().length < 2) {
            renderCityOptions([]);
            status.textContent = t.type_more;
            return;
        }
        locationController = new AbortController();
        status.textContent = t.searching;
        try {
            const params = new URLSearchParams({ name: query.trim(), count: '8', language: locale, format: 'json' });
            const response = await fetch('https://geocoding-api.open-meteo.com/v1/search?' + params,
                { signal: locationController.signal });
            if (!response.ok) throw new Error('geocoding HTTP ' + response.status);
            const data = await response.json();
            if (requestId !== locationRequest) return;
            const matches = (data.results || []).filter(validCity);
            renderCityOptions(matches);
            status.textContent = matches.length ? t.choose_city : t.no_city;
        } catch (error) {
            if (error.name === 'AbortError' || requestId !== locationRequest) return;
            renderCityOptions([]);
            status.textContent = t.city_error;
        }
    }
    search.addEventListener('input', () => {
        clearTimeout(queryTimer);
        const query = search.value;
        if (query.trim().length < 2) {
            if (locationController) locationController.abort();
            locationRequest += 1;
            renderCityOptions([]);
            status.textContent = query.trim() ? t.type_more : '';
            return;
        }
        queryTimer = setTimeout(() => findCities(query), 420);
    });
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        clearTimeout(queryTimer);
        findCities(search.value);
    });
    byId('climate-default-city').addEventListener('click', () => selectCity(DEFAULT_CITY));
    document.addEventListener('click', (event) => {
        if (!form.contains(event.target) && !results.contains(event.target)) {
            results.hidden = true;
            search.setAttribute('aria-expanded', 'false');
        }
    });
    search.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            results.hidden = true;
            search.setAttribute('aria-expanded', 'false');
        }
    });

    // Mantém os dados reais atualizados enquanto a página estiver aberta.
    setInterval(() => {
        if (!document.hidden) loadWeather();
    }, 15 * 60 * 1000);

    text('climate-city-name', cityLabel(city));
    text('climate-search-city', cityLabel(city));
    renderScene();
    loadWeather();
})();
