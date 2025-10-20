const backendHost = '';
//const backendHost = 'http://127.0.0.1:8081';
const apiRootUrl = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products";
const supportEmail = "placeholder@example.com"; //TODO Change email

const leafletInitCoords = [50.05, 14.46]; //TODO find users location
const leafletInitZoom = 10;

const timeFromHourCorrection = (7 * 24); //This amount of hours will be subtracted from today midnight

const maxLoadedFeatures = 100;

const offeredDatasets = [
    "SENTINEL-1",
    "SENTINEL-2"//,
    //"SENTINEL-3", //todo zatím jen S1 a S2
    //"SENTINEL-5P" //todo zatím jen S1 a S2
];

const status = {
    ERROR: "Error",
    WARNING: "Warning",
    SUCCESS: "Success"
}

// // All possible datasets:
// const offeredDatasets = [
// // Copernicus Sentinel Mission
// "SENTINEL-1",
// "SENTINEL-2",
// "SENTINEL-3",
// "SENTINEL-5P",
// "SENTINEL-6",
// "SENTINEL-1-RTC",
// // Complementary data...
// "GLOBAL-MOSAICS",
// "SMOS",
// "ENVISAT",
// "LANDSAT-5",
// "LANDSAT-7",
// "LANDSAT-8",
// "COP-DEM",
// "TERRAAQUA",
// "S2GLC"
// ]

/**********************************************************************************************************************/

/***************************************
 SETUP
 **************************************/

let leafletMap = L.map('map-div').setView(leafletInitCoords, leafletInitZoom);
L.control.scale().addTo(leafletMap);

let osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Base map (c) <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
    minZoom: 3,
    maxZoom: 19,
    opacity: 1,
}).addTo(leafletMap);

const hoverLayer = L.geoJSON(null, {
    style: {
        color: '#6997e5',
        weight: 2,
        fillOpacity: 0.2
    }
}).addTo(leafletMap);

const provider = new window.GeoSearch.OpenStreetMapProvider();
const searchControl = new window.GeoSearch.GeoSearchControl({
    provider: provider,
    style: 'bar',
    showMarker: true,
    retainZoomLevel: false,
    autoClose: true,
    searchLabel: 'Search address',
});

leafletMap.addControl(searchControl);

let isUserInteractingWithMap = true;

leafletMap.on('moveend', () => {
    if (isUserInteractingWithMap) {
        insertCoordinatesFromMap();
    }
});

leafletMap.on('zoomend', () => {
    if (isUserInteractingWithMap) {
        insertCoordinatesFromMap();
    }
});

insertCoordinatesFromMap();


let timeFrom = new Date();
timeFrom.setUTCHours(0);
timeFrom.setUTCHours(timeFrom.getUTCHours() - timeFromHourCorrection);
timeFrom.setUTCMinutes(0);
timeFrom.setUTCSeconds(0);

let timeFromInput = document.querySelector("#time-from-input");
timeFromInput.value = timeFrom.toISOString().substring(0, 16);

let timeTo = new Date();
timeTo.setUTCHours(23);
timeTo.setUTCMinutes(59);
timeTo.setUTCSeconds(59);

let timeToInput = document.querySelector("#time-to-input");
timeToInput.value = timeTo.toISOString().substring(0, 16);

sentinel2CloudCoverSliderToValue();

/***************************************
 LOGIC
 **************************************/

function insertCoordinatesFromMap() {
    let coordinatesNWInput = document.querySelector("#coordinates-nw-input");
    coordinatesNWInput.value = `${leafletMap.getBounds().getNorthWest().lat.toFixed(4)};${leafletMap.getBounds().getNorthWest().lng.toFixed(4)}`;

    let coordinatesSEInput = document.querySelector("#coordinates-se-input");
    coordinatesSEInput.value = `${leafletMap.getBounds().getSouthEast().lat.toFixed(4)};${leafletMap.getBounds().getSouthEast().lng.toFixed(4)}`;
}

function sentinel2CloudCoverSliderToValue() {
    let sentinel2CloudCoverSlider = document.querySelector("#sentinel-2-cloud-cover-range");
    let sentinel2CloudCoverValue = document.querySelector("#sentinel-2-cloud-cover-value");
    sentinel2CloudCoverValue.value = sentinel2CloudCoverSlider.value;
}

function updateOpacity(value) {
    window.currentSatelliteTiles.setOpacity(value);
}

document.querySelector("#sentinel-2-cloud-cover-value").addEventListener("input", function () {
    let sentinel2CloudCoverSlider = document.querySelector("#sentinel-2-cloud-cover-range");
    sentinel2CloudCoverSlider.value = this.value;
});

const generalChoicesSetup = {
    removeItemButton: true,
    shouldSort: true,
    placeholder: true,
    placeholderValue: " + ",
    position: 'bottom',
}

// const featureSelect = document.getElementById("available-features-select");
// const featureChoices = new Choices(featureSelect, {
//     searchEnabled: false,
//     shouldSort: true,
//     position: 'bottom',
//     itemSelectText: '',
// });

const s2BandChoices = new Choices('#sentinel-2-bands', generalChoicesSetup);

const s2LevelChoices = new Choices('#sentinel-2-levels', generalChoicesSetup);

const s1LevelChoices = new Choices('#sentinel-1-levels', generalChoicesSetup);

const s1SensingTypesChoices = new Choices('#sentinel-1-sensing-types', generalChoicesSetup);

const s1ProductTypesChoices = new Choices('#sentinel-1-product-types', generalChoicesSetup);

const s1PolarisationChoices = new Choices('#sentinel-1-polarisation', generalChoicesSetup);


const closeAlert = (alertDiv) => {
    alertDiv.style.animation = 'slide-out 0.7s forwards';
    alertDiv.addEventListener('animationend', () => {
        alertDiv.remove();
    });
}

const showAlert = async (status, message, appendContact=false) => {
    if (appendContact) {
        message += `<br>If this problem persists feel free to <a href=\"mailto:${supportEmail}\">contact us</a>.`;
    }

    await fetch('alert.html')
        .then(response => response.text())
        .then(data => {
            let alertDOM = new DOMParser().parseFromString(data, 'text/html');
            alertDOM.querySelector('#alert-headline').innerHTML = status;
            alertDOM.querySelector('#alert-message').innerHTML = message;

            const alertDiv = alertDOM.querySelector('#alert-div')
            alertDiv.classList.add(status.toLowerCase());
            document.querySelector('#alerts-div').appendChild(alertDiv);

            setTimeout(() => {
                closeAlert(alertDiv)
            }, 10000)
        });
}

const preparePolygon = (northWestLat, northWestLon, southEastLat, southEastLon) => {
    return `POLYGON((${northWestLon} ${northWestLat},${southEastLon} ${northWestLat},` +
        `${southEastLon} ${southEastLat},${northWestLon} ${southEastLat},${northWestLon} ${northWestLat}))`;
}

const fetchFeaturesFromCopernicus = async (endpoint) => {
    //console.log(endpoint)
    let features = [];

    while (true) {
        try {
            const response = await fetch(endpoint);
            const data = await response.json();
            //console.log(data);

            features = features.concat(data.value);

            if (features.length >= maxLoadedFeatures) {
                // Let's not load the whole collection
                break;
            }
            if (!('@odata.nextLink' in data)) {
                break;
            }

            endpoint = data['@odata.nextLink'];

        } catch (error) {
            console.error(`Error fetchig data! Error name: ${error.name}; Error message: ${error.message}`);
            break;
        }
    }

    return features;
};


let featuresGlobal = new Map();
let filtersGlobal = new Map();

let spinner = document.querySelector("#spinner-div");

const showSpinner = () => {
    spinner.style.display = "block";
};

const hideSpinner = () => {
    spinner.style.display = "none";
};

const parseCoordinates = async (coordinatesString) => {
    if (typeof coordinatesString !== 'string') {
        throw new Error('coordinatesString must be a string');
    }

    coordinatesString = coordinatesString.replace(/,/g, '.');

    const parts = coordinatesString.split(';');
    if (parts.length !== 2) {
        await showAlert(status.WARNING, "Coordinates must be in format [dd.dddd;dd.dddd]", false);
        return undefined;
    }

    const [latitude, longitude] = parts.map(Number);
    if (isNaN(latitude) || isNaN(longitude)) {
        alert("Coordinates must be valid numbers");
        return undefined;
    }

    return [latitude, longitude];
}

// const clearFeaturesSelection = () => {
//     featureChoices.removeActiveItems();
//     featureChoices.clearChoices();
//     hoverLayer.clearLayers();
//     showBorders();
// }

const fetchFeatures = async () => {
    showSpinner();
    disableUIElements();

    try {
        // TODO Ošetřit když není zadaná nějaká složka data
        let timeFrom = new Date(document.querySelector("#time-from-input").value + ":00Z");
        let timeTo = new Date(document.querySelector("#time-to-input").value + ":00Z");

        if (timeTo < timeFrom) {
            await showAlert(status.WARNING, "Time to must be after Time from!", false);
            return;
        }

        let tomorrow = new Date();
        tomorrow.setUTCDate(tomorrow.getUTCDate() + 1);
        tomorrow.setUTCHours(0, 0, 0, 0);

        if ((timeFrom > tomorrow) || (timeTo > tomorrow)) {
            await showAlert(status.WARNING, "Date could not be in the future!", false);
            return;
        }

        const coordinatesUserInputElements = document.getElementsByClassName("coordinate-user-input")
        let coordinatesUserInput = []
        for (let coordinatesElement of coordinatesUserInputElements) {
            if (coordinatesElement.value === "") {
                continue;
            }

            const coordinates = await parseCoordinates(coordinatesElement.value);
            if (coordinates) {
                coordinatesUserInput.push(coordinates);
            } else {
                return; // Stop the loop if coordinates are not valid
            }
        }

        if (coordinatesUserInput.length <= 0) {
            insertCoordinatesFromMap();
            await fetchFeatures(); // Coordinates inserted into input boxes, thus we can load it in second run of this function
            return; // Features fetched, in second run of fetchFeatures() above. We can exit the first run.
        }

        let polygon = preparePolygon(
            coordinatesUserInput[0][0],
            coordinatesUserInput[0][1],
            coordinatesUserInput[1][0],
            coordinatesUserInput[1][1]
        );

        const datasetsSelectedNodes = document.querySelectorAll('input[name="dataset"]:checked');
        const datasetsSelected = Array.from(datasetsSelectedNodes).map(checkbox => checkbox.value);
        if (datasetsSelected.length <= 0) {
            await showAlert(status.WARNING, "Please choose dataset.", false);
            return;
        }

        filtersGlobal = new Map();
        let obtainedFeatures = [];
        for (let dataset in datasetsSelected) {
            let filters = [];

            const datasetFilter = `Collection/Name eq '${datasetsSelected[dataset]}'`;

            switch (datasetsSelected[dataset]) {
                case "SENTINEL-1": {
                    const s1LevelSelected = s1LevelChoices.getValue(true);
                    const s1SensingTypesSelected = s1SensingTypesChoices.getValue(true);
                    const s1ProductTypesSelected = s1ProductTypesChoices.getValue(true);
                    const s1PolarisationSelected = s1PolarisationChoices.getValue(true);

                    if (s1LevelSelected.length <= 0 || s1SensingTypesSelected.length <= 0 || s1ProductTypesSelected.length <= 0) {
                        await showAlert(status.WARNING, "Not enough parameters specified!", false);
                    }

                    let selectedFilters = new Map();

                    selectedFilters.set('levels', s1LevelSelected);
                    let levelsApiCall = undefined;
                    if (s1LevelSelected.length > 0) {
                        levelsApiCall = `(${s1LevelSelected.map(
                            level => `Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'processingLevel' and att/OData.CSC.StringAttribute/Value eq '${level}')`
                        ).join(' or ')})`;
                    }

                    selectedFilters.set('sensing_types', s1SensingTypesSelected);
                    let sensingTypesApiCall = undefined;
                    if (s1SensingTypesSelected.length > 0) {
                        sensingTypesApiCall = `(${s1SensingTypesSelected.map(
                            sensingType => `Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'operationalMode' and att/OData.CSC.StringAttribute/Value eq '${sensingType}')`
                        ).join(' or ')})`;
                    }

                    selectedFilters.set('product_types', s1ProductTypesSelected);
                    let productTypesApiCall = undefined;
                    if (s1ProductTypesSelected.length > 0) {
                        productTypesApiCall = `(${s1ProductTypesSelected.map(
                            productType => `Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq '${productType}')`
                        ).join(' or ')})`;
                    }

                    selectedFilters.set('polarisation_channels', s1PolarisationSelected);
                    let polarisationChannelsApiCall = undefined;
                    if (s1PolarisationSelected.length > 0) {
                        polarisationChannelsApiCall = `(${s1PolarisationSelected.map(
                            polarisationChannel => `Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'polarisationChannels' and att/OData.CSC.StringAttribute/Value eq '${polarisationChannel.replace('&', '%26')}')`
                        ).join(' or ')})`;
                    }


                    filtersGlobal.set(datasetsSelected[dataset], selectedFilters);
                    filters += `${datasetFilter} and (${levelsApiCall} and ${sensingTypesApiCall} and ${productTypesApiCall} and ${polarisationChannelsApiCall})`;

                    break;
                }

                case "SENTINEL-2": {
                    const s2CloudCoverSelected = document.querySelector('#sentinel-2-cloud-cover-value').value;
                    const s2LevelsSelected = s2LevelChoices.getValue(true);
                    const s2BandsSelected = s2BandChoices.getValue(true);

                    if (s2LevelsSelected.length <= 0 || s2BandsSelected.length <= 0) {
                        await showAlert(status.WARNING, "Not enough parameters specified!", false);
                    }

                    let selectedFilters = new Map();

                    selectedFilters.set('cloud_cover', s2CloudCoverSelected);
                    let cloudCoverApiCall = `Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value le ${s2CloudCoverSelected}.00)`;


                    selectedFilters.set('levels', s2LevelsSelected);
                    let levelsApiCall = undefined;
                    if (s2LevelsSelected.length > 0) {
                        levelsApiCall = `(${s2LevelsSelected.map(
                            level => `Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq '${level}')`
                        ).join(' or ')})`;
                    }

                    selectedFilters.set('bands', s2BandsSelected);
                    // Bands not filtered in Copernicus API call

                    filtersGlobal.set(datasetsSelected[dataset], selectedFilters)
                    filters += `${datasetFilter} and (${cloudCoverApiCall} and ${levelsApiCall})`;

                    break;
                }

                case "SENTINEL-3": {
                    //TODO do budoucna přidělat zpracování S3 a S5P
                    break;
                }

                case "SENTINEL-5P": {
                    //TODO do budoucna přidělat zpracování S3 a S5P
                    break;
                }

                default: {
                    await showAlert(status.WARNING, "Unexpected datasource chosen!", false);
                    return;
                }
            }


            let filtersQuery = `OData.CSC.Intersects(area=geography'SRID=4326;${polygon}')`;
            filtersQuery += ` and ${filters}`;
            filtersQuery += ` and (ContentDate/Start ge ${timeFrom.toISOString()} and ContentDate/Start le ${timeTo.toISOString()})`;

            const endpoint = new URL(`?$filter=(${filtersQuery})`, apiRootUrl);

            let currentFeatures = await fetchFeaturesFromCopernicus(endpoint.href);
            for (let currentFeature of currentFeatures) {
                currentFeature['platform'] = datasetsSelected[dataset];
            }

            obtainedFeatures = obtainedFeatures.concat(currentFeatures);
        }

        const obtainedFeaturesMap = new Map();
        obtainedFeatures.forEach(obtainedFeature => {
            obtainedFeaturesMap.set(obtainedFeature.Id, obtainedFeature);
        });

        const featuresIds = new Set(obtainedFeatures.map(item => item.Id));

        let finalFeatures = [];
        for (let featureId of featuresIds) {
            finalFeatures.push(obtainedFeaturesMap.get(featureId));
        }

        featuresGlobal = new Map();
        document.getElementById("product-tile-list").innerHTML = "";

        for (const feature of finalFeatures) {
            featuresGlobal.set(feature.Id, feature);
            showProductDetail(feature);
        }

        document.addEventListener('mouseover', function (e) {
            const item = e.target.closest('.choices__item--choice');
            if (item && item.dataset.value) {
                const feature = featuresGlobal.get(item.dataset.value);
                hoverLayer.clearLayers();
                if (feature?.GeoFootprint) {
                    hoverLayer.addData(feature.GeoFootprint);
                }
            }
        });

        document.addEventListener('mouseout', function (e) {
            if (e.target.closest('.choices__item--choice')) {
                hoverLayer.clearLayers();
            }
        });

        if (obtainedFeatures.length > 0) {
            enableUIElements()
            toggleFeaturesControl();
        } else {
            enableUIElements()
            await showAlert(status.WARNING, "No features found for selected filters!", false);
        }

    } catch (error) {
        await showAlert(status.WARNING, `Internal application error occurred. Please check console for further information.`, true);
        console.error(`Error fetching tiles!  Error name: ${error.name}; Error message: ${error.message}`);
    } finally {
        hideSpinner();
    }
};

const disableUIElements = () => {
    // document.querySelector("#open-product-button-div").classList.add("disabled-element");
    document.querySelector("#map-div").classList.add("disabled-element");
}

const enableUIElements = () => {
    // document.querySelector("#open-product-button-div").classList.remove("disabled-element");
    document.querySelector("#map-div").classList.remove("disabled-element");
}

function togglePanel(activeId) {
    const panels = ["features-panel", "preselection-panel", "visualization-panel"];
    panels.forEach(id => {
        const panel = document.querySelector(`#${id}`);
        if (panel) {
            panel.classList.toggle("hidden-element", id !== activeId);
        }
    });
}

const toggleFeaturesControl = () => togglePanel("features-panel");
const togglePreselectionControl = () => togglePanel("preselection-panel");
const toggleVisualizationControl = () => togglePanel("visualization-panel");


class VisualizationRequest {
    constructor(featureId, status, processedFiles) {
        this.featureId = featureId;
        this.status = status;
        this.processedFiles = processedFiles;
    }

    isInitialized() {
        return (this.featureId !== undefined)
            && (this.status !== undefined)
            && (this.processedFiles !== undefined);
    }

    getProcessedFiles() {
        return this.processedFiles;
    }
}

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

const fetchWithTimeout = async (url, options = {}, timeout = 5000) => {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    console.log("Requesting:", url, options); // todo smazat

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });

        console.log("Response:", response); // todo smazat

        if (!response.ok) {
            throw new Error(`Backend error: ${response.statusText}`);
        }

        return response;
    } catch (error) {
        if (error.name === 'AbortError') {
            // Timeout specific handling
            console.error('Request timed out');
        } else {
            // Other error handling (network issues, etc.)
            console.error(`Error name: ${error.name}; Error message: ${error.message}`);
        }

        throw error; // Re-throw the error after logging
    } finally {
        clearTimeout(id); // Clean up timeout
    }
};

const openFeature = () => {
    const selectedValue = document.querySelector("#processed-products-select").value;

    if (selectedValue) {
        const selectedValueJSON = JSON.parse(selectedValue);

        const requestHash = encodeURIComponent(selectedValueJSON.requestHash);
        let file = encodeURIComponent(selectedValueJSON.file);

        if (window.currentSatelliteTiles) {
            leafletMap.removeLayer(window.currentSatelliteTiles);
        }

        //const tileUrlTemplate = `${backendHost}/api/get_tile/{z}/{x}/{y}.jpg?request_hash=${requestHash}&selected_file=${file}`;

        file = file.split('.').slice(0,-1).join('.');
        const tileUrlTemplate = `${backendHost}/data/${requestHash}/${file}/{z}/{x}/{y}.jpg`;

        const satelliteTiles = L.tileLayer(tileUrlTemplate, {
            attribution: 'Satellite imagery (c) <a href="https://www.copernicus.eu/">Copernicus programme</a>',
            minZoom: 8,
            maxZoom: 19,
            tileSize: 256,
            opacity: document.querySelector("#opacity-slider").value,
        });

        satelliteTiles.addTo(leafletMap);

        window.currentSatelliteTiles = satelliteTiles;
    }
}

const visualize = async (featureId) => {
    let visualizationRequest = await requestVisualization(featureId)

    let processedProductsSelect = document.querySelector("#processed-products-select");
    processedProductsSelect.innerHTML = '';

    for (const requestHash in visualizationRequest.getProcessedFiles()) {
        for (const file of visualizationRequest.getProcessedFiles()[requestHash]) {
            let option = document.createElement("option");
            option.value = `{"requestHash":"${requestHash}", "file":"${file}"}`;
            option.textContent = file;
            processedProductsSelect.appendChild(option);
        }
    }

    openFeature();
    enableUIElements();
}

const downloadImage = async () => {
    const selectedValue = document.querySelector("#processed-products-select").value;
    if (!selectedValue) {
        showAlert(status.WARNING, "No image selected for download!");
    }

    try {
        const selectedValueJSON = JSON.parse(selectedValue);
        const requestHash = encodeURIComponent(selectedValueJSON.requestHash);
        const filename = encodeURIComponent(selectedValueJSON.file);

        const response = await fetch(`${backendHost}/api/download_image/${requestHash}/${filename}`);

        if (!response.ok) {
            showAlert(status.ERROR, `Download failed with status ${response.status}`);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();

    } catch (error) {
        showAlert(status.ERROR, "Failed to download image. Please try again later.", true);
        console.error(`Error downloading image: ${error.message}`);
    }

}

const requestVisualization = async (featureId) => {
    showSpinner();

    const repeatRequestAfter = 5 * 1000 // millisecs
    const totalTimeout = 120 // secs // TODO timeout of backend processing after 120 sec. Enough?
    const backendReplyTimeout = 30 * 1000;  // 1 sec = 1 000 millisecs // TODO timeout of backend call after 30 sec. Enough?

    const platform = featuresGlobal.get(featureId).platform;
    const filters = Object.fromEntries(filtersGlobal.get(platform));

    const method = 'POST';
    const headers = {
        'Content-Type': 'application/json',
    }
    const bodyJson = JSON.stringify(
        {
            feature_id: featureId,
            platform: platform,
            filters: filters
        }
    );

    let visualizationRequest = new VisualizationRequest(
        undefined,
        undefined,
        undefined,
        undefined
    );

    try {
        let url = `${backendHost}/api/request_processing`
        console.log(url);

        let timeEnd = new Date()
        timeEnd.setUTCSeconds(timeFrom.getUTCSeconds() + totalTimeout);

        do {
            const response = await fetchWithTimeout(url, {
                method: method,
                headers: headers,
                body: bodyJson,
            }, backendReplyTimeout);

            const data = await response.json();

            visualizationRequest = new VisualizationRequest(
                data.feature_id,
                data.status,
                data.processed_files
            );

            console.log(visualizationRequest);
            //todo tyhle status message by to chtělo jako nějakej enum
            if (visualizationRequest.status === "failed") {
                e = new Error("Backend visualization request failed!");
                e.name = 'VisualizationFailedError'
                throw e;
            }

            if (visualizationRequest.status !== "completed") {
                if (new Date() > timeEnd) {
                    e = new Error();
                    e.name = 'AbortError';
                    throw e;
                }
                await delay(repeatRequestAfter);
            }
        } while (visualizationRequest.status !== "completed");

    } catch (error) {
        if (error.name === 'AbortError') {
            await showAlert(status.WARNING, "Request timed out!", false);
        } else if (error.message.includes('NetworkError')) {
            await showAlert(status.WARNING, `Network error - connection to backend failed! Please try again later.`, true);
        } else {
            await showAlert(status.ERROR, `Internal application error occurred! Please check console for more information.`, true);
            console.error(`Error name: ${error.name}; Error message: ${error.message}`);
        }
    } finally {
        hideSpinner();
    }

    if (visualizationRequest.isInitialized() !== true) {
        throw new Error("Request is not initialized!"); // todo proper exception
    }

    if (visualizationRequest.status === "completed") {
        toggleVisualizationControl();
    }

    return visualizationRequest;
};

const transposeCoordinates = (coordinatesArray) => {
    let newCoordinatesArray = [];

    for (let coordinates of coordinatesArray) {
        newCoordinatesArray.push([coordinates[1], coordinates[0]]);
    }

    return newCoordinatesArray;
}

const showBorders = () => {
    if (window.selectedFeaturePolygon) {
        window.selectedFeaturePolygon.remove()
    }

    const selectedFeatureId = document.getElementById("available-features-select").value;
    if (!selectedFeatureId) {
        return;
    }

    let coordinates = transposeCoordinates(featuresGlobal.get(selectedFeatureId).GeoFootprint.coordinates[0]);

    const selectedFeaturePolygon = L.polygon(coordinates, {
        color: 'black', //obrys
        fillColor: 'black', //vypln
        fillOpacity: 0.3
    }).addTo(leafletMap);

    isUserInteractingWithMap = false;
    leafletMap.fitBounds(selectedFeaturePolygon.getBounds());
    leafletMap.once('moveend', () => {
        isUserInteractingWithMap = true;
    });

    window.selectedFeaturePolygon = selectedFeaturePolygon;
};

document.querySelectorAll(".mission-filter-button").forEach((filterButton) => {
    filterButton.addEventListener("click", async function () {
        await toggleMissionFiltersDiv(filterButton);
    });
});

const toggleMissionFiltersDiv = async (filterButton) => {
    const mission = filterButton.value;
    const missionAdditionalFiltersDivId = `mission-additional-filters-${mission.toLowerCase()}`;

    const missionAdditionalFiltersActiveStatus = document.querySelector(`#${missionAdditionalFiltersDivId}`).classList.contains("active")

    document.querySelectorAll(".additional-filters").forEach((additionalFilter) => {
        additionalFilter.classList.remove("active");
    })
    document.querySelectorAll(".mission-filter-button").forEach((button) => {
        button.innerHTML = "Open filter"
    });

    if (offeredDatasets.includes(mission)) {
        if (!missionAdditionalFiltersActiveStatus) {
            document.querySelector(`#${missionAdditionalFiltersDivId}`).classList.add("active");
            filterButton.innerHTML = "Close filter"
        }
    } else {
        await showAlert(status.ERROR, `Unexpected mission selected`, false);
    }
}

const toggleSentinel2Checkbox = () => {
    if (
        s2BandChoices.getValue("true").length === 0 ||
        s2LevelChoices.getValue("true").length === 0
    ) {
        document.querySelector("#mission-filter-checkbox-sentinel-2").checked = false;
    } else {
        document.querySelector("#mission-filter-checkbox-sentinel-2").checked = true;
    }
}

const toggleSentinel1Checkbox = () => {
    if (
        s1ProductTypesChoices.getValue("true").length === 0 ||
        s1LevelChoices.getValue("true").length === 0 ||
        s1SensingTypesChoices.getValue("true").length === 0 ||
        s1PolarisationChoices.getValue("true").length === 0
    ) {
        document.querySelector("#mission-filter-checkbox-sentinel-1").checked = false;
    } else {
        document.querySelector("#mission-filter-checkbox-sentinel-1").checked = true;
    }
}

const showProductDetail = (metadata) => {
    const template = document.getElementById("product-tile-template");
    const tileListDiv = document.getElementById("product-tile-list");
    const product = template.content.cloneNode(true);
    product.querySelector(".product-name").textContent = metadata.Name;
    product.querySelector(".product-mission").textContent = metadata.platform;
    product.querySelector(".product-time").textContent = metadata.ContentDate.Start;
    // product.querySelector(".product-size").textContent = metadata.ContentLength;

    productDiv = product.querySelector(".product-tile");
    productDiv.addEventListener("mouseenter", async function (e) {
        const feature = featuresGlobal.get(metadata.Id);
        hoverLayer.clearLayers();
        if (feature?.GeoFootprint) {
            hoverLayer.addData(feature.GeoFootprint);
        }
    });

    productDiv.addEventListener("mouseleave", async function (e) {
        hoverLayer.clearLayers();
    });

    product.querySelector(".visualize-btn").addEventListener("click", async function () {
        visualize(metadata.Id);
    })

    product.querySelector(".download-link-btn").addEventListener("click", async function () {
        const url = "https://download.dataspace.copernicus.eu/odata/v1/Products(" + metadata.Id + ")/$value";
        await navigator.clipboard.writeText(url);
        showAlert(status.SUCCESS, "URL copied to clipboard.");
    })

    tileListDiv.appendChild(product);
}
