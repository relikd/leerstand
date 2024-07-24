const DATA_ROOT = '/data/';
let MAP = null;
let LAYER = null;
let CITIES = {};
let PLACES = {};
const DEFAULT_CENTER = [51.2, 9];
const DEFAULT_ZOOM = 6;

// ---------------------
//  Load data
// ---------------------

async function loadJson(url) {
    const res = await fetch(url);
    return await res.json();
}

async function loadCities() {
    CITIES = {};
    for (const city of await loadJson(DATA_ROOT + 'cities.json')) {
        CITIES[city.id] = city;
    }
}

async function loadCity(cityId) {
    PLACES = {};
    for (const place of await loadJson(DATA_ROOT + cityId + '/data.json')) {
        if (since(place.until) > 0) {
            continue; // not vacant anymore
        }
        PLACES[place.id] = place;
    }
    updateCounter();
}

// ---------------------
//  Helper
// ---------------------

function getCityId(slug) {
    for (const city of Object.values(CITIES)) {
        if (city.slug === slug) {
            return city.id;
        }
    }
    return null;
}

function since(date) {
    if (!date) {
        return 0;
    }
    const [y, m] = (date + '-01').split('-');
    const diff = Date.now() - new Date(y, m - 1);
    return Math.floor(diff / (1000 * 60 * 60 * 24));
}

function makeIcon(className) {
    return L.divIcon({
        className: className,
        html: '<svg><use href="/icons.svg#mark"></use></svg>',
        iconSize: [34, 55],
        iconAnchor: [17, 55],
        popupAnchor: [0, -20],
        tooltipAnchor: [0, -20],
        offset: [10, 20],
    });
}

function makeMarker(place) {
    const vacantYears = Math.floor(since(place.since) / 365);
    return L.marker(L.latLng(place.loc), {
        pid: place.id,
        title: place.addr,
        icon: makeIcon('pin fc' + Math.min(vacantYears, 7)),
    }).on('click', clickPin);
}

function clickPin(pin) {
    setPlace(pin.target.options.pid);
}

function closePopup(e) {
    setPlace(null)
}

function makeCityMarker(city) {
    return L.marker(L.latLng(city.loc), {
        pid: city.id,
        title: city.name,
        icon: makeIcon('pin pin-city'),
    }).on('click', cityPinClick);
}

async function cityPinClick(pin) {
    await showCity(pin.target.options.pid);
}

// ---------------------
//  UI updates
// ---------------------

function setPlace(placeId) {
    const hide = !placeId;
    const place = hide ? {} : PLACES[placeId];
    const div = document.getElementById('popup');
    div.hidden = hide;
    div.querySelector('img').src = place.img || '';
    div.querySelector('h3').innerText = place.addr || '';
    div.querySelector('#_since').innerText = place.until
        ? 'von ' + place.since + ' bis ' + place.until
        : place.since ? 'seit ' + place.since : '???';
    div.querySelector('#_desc').innerText = place.desc || '';

    location.hash = location.hash.split('|')[0] + (hide ? '' : '|' + placeId);
    document.title = document.title.split(' "', 1)[0] + (hide ? '' : ' "' + place.addr + '"');
}

function setCity(city) {
    document.getElementById('city-select').value = city ? city.id : '';
    location.hash = city ? city.slug : '';
    document.title = document.title.split(' in ', 1)[0] + (city ? ' in ' + city.name : '');
}

function updateCounter() {
    const total = Object.keys(PLACES).length;
    const counter = document.getElementById('city-counter');
    counter.innerText = total;
    counter.hidden = total === 0;
}

// ---------------------
//  Initialize
// ---------------------

function initMap() {
    const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: [
            '<svg class="fc0"><rect/></svg> &lt; 1 Jahr',
            '<svg class="fc1"><rect/></svg> 1–3 J.',
            '<svg class="fc3"><rect/></svg> 3–5 J.',
            '<svg class="fc5"><rect/></svg> 5–7 J.',
            '<svg class="fc7"><rect/></svg> 7+ Jahre',
            '© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            '<a href="/imprint.html">Impressum</a>',
        ].join(' | '),
    });
    MAP = L.map('map', {
        layers: [osm], center: DEFAULT_CENTER, zoom: DEFAULT_ZOOM,
        zoomSnap: 0.5,
    });
    LAYER = L.layerGroup([]).addTo(MAP);
    L.control.locate({ showPopup: false }).addTo(MAP);
}

function initCities() {
    const select = document.getElementById('city-select');
    while (select.options.length > 1) {
        select.options.remove(1);
    }
    for (const city of Object.values(CITIES)) {
        const opt = document.createElement('option');
        opt.value = city.id;
        opt.innerText = city.name;
        select.add(opt);
    }
    select.hidden = false;
}

// ---------------------
//  Interactive
// ---------------------

function showCityOverview() {
    LAYER.clearLayers();
    MAP.setView(DEFAULT_CENTER, DEFAULT_ZOOM);
    setCity(null);
    PLACES = {};
    updateCounter();

    for (const city of Object.values(CITIES)) {
        makeCityMarker(city).addTo(LAYER);
    }
}

async function showCity(cityId) {
    const city = CITIES[cityId];
    LAYER.clearLayers();
    MAP.setView(city.loc, city.zoom);
    setCity(city);
    await loadCity(cityId);

    var bounds = L.latLngBounds();
    for (const place of Object.values(PLACES)) {
        const marker = makeMarker(place).addTo(LAYER);
        bounds.extend(marker.getLatLng());
    }
    // adjust bounds & zoom
    if (bounds.isValid()) {
        MAP.fitBounds(bounds, { padding: [50, 50] });
    }
}

async function start() {
    initMap();
    await loadCities();
    initCities();

    const [city_slug, place_id] = location.hash.substring(1).split('|');
    const city_id = city_slug ? getCityId(city_slug) : null;
    if (city_id) {
        await showCity(city_id);
        if (place_id) {
            setPlace(place_id);
        }
    } else {
        const available_cities = Object.keys(CITIES);
        if (available_cities.length === 1) {
            await showCity(available_cities[0]);
        } else {
            showCityOverview();
        }
    }
    document.getElementById('loading').hidden = true;
}
