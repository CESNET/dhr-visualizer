const backendHost = 'http://195.113.151.147:8081';
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
    attribution: 'Map data (c) <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
    maxZoom: 19,
}).addTo(leafletMap);

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

document.querySelector("#sentinel-2-cloud-cover-value").addEventListener("input", function () {
    let sentinel2CloudCoverSlider = document.querySelector("#sentinel-2-cloud-cover-range");
    sentinel2CloudCoverSlider.value = this.value;
});

const closeAlert = (alertDiv) => {
    alertDiv.style.animation = 'slide-out 0.7s forwards';
    alertDiv.addEventListener('animationend', () => {
        alertDiv.remove();
    });
}

const showAlert = async (headline, message, appendContact) => {
    if (appendContact) {
        message += `<br>If this problem persists feel free to <a href=\"mailto:${supportEmail}\">contact us</a>.`;
    }

    await fetch('alert.html')
        .then(response => response.text())
        .then(data => {
            let alertDOM = new DOMParser().parseFromString(data, 'text/html');
            alertDOM.querySelector('#alert-headline').innerHTML = headline;
            alertDOM.querySelector('#alert-message').innerHTML = message;

            const alertDiv = alertDOM.querySelector('#alert-div')
            document.querySelector('#alerts-div').appendChild(alertDiv);

            setTimeout(() => {
                closeAlert(alertDiv)
            }, 10000)
        });
}

/*
const preparePolygon = (northWestLat, northWestLon, southEastLat, southEastLon) => {
    let polygon = [
        [northWestLon, northWestLat],
        [northWestLon, southEastLat],
        [southEastLon, southEastLat],
        [southEastLon, northWestLat],
        [northWestLon, northWestLat]
    ];

    return polygon;
};
*/

/*
const prepareBbox = (northWestLat, northWestLon, southEastLat, southEastLon) => {
    let coordArray = [
        northWestLon.toString(),
        northWestLat.toString(),
        southEastLon.toString(),
        southEastLat.toString()
    ];

    let bbox = coordArray.join(",");
    return bbox;
};
*/

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
        await showAlert("Warning", "Coordinates must be in format [dd.dddd;dd.dddd]", false);
        return undefined;
    }

    const [latitude, longitude] = parts.map(Number);
    if (isNaN(latitude) || isNaN(longitude)) {
        alert("Coordinates must be valid numbers");
        return undefined;
    }

    return [latitude, longitude];
}

const clearAvailableFeaturesSelect = () => {
    let availableFeaturesSelect = document.getElementById('available-features-select');
    availableFeaturesSelect.innerHTML = '';
    disableUIElements();
}

const fetchFeatures = async () => {
    showSpinner();
    clearAvailableFeaturesSelect();
    disableUIElements();

    try {
        // TODO Ošetřit když není zadaná nějaká složka data
        let timeFrom = new Date(document.querySelector("#time-from-input").value + ":00Z");
        let timeTo = new Date(document.querySelector("#time-to-input").value + ":00Z");

        if (timeTo < timeFrom) {
            await showAlert("Warning", "Time to must be after Time from!", false);
            return;
        }

        let tomorrow = new Date();
        tomorrow.setUTCDate(tomorrow.getUTCDate() + 1);
        tomorrow.setUTCHours(0, 0, 0, 0);

        if ((timeFrom > tomorrow) || (timeTo > tomorrow)) {
            await showAlert("Warning", "Date could not be in the future!", false);
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
            await showAlert("Warning", "Please choose dataset.", false);
            return;
        }

        filtersGlobal = new Map();
        let obtainedFeatures = [];
        for (let dataset in datasetsSelected) {
            let filters = [];

            const datasetFilter = `Collection/Name eq '${datasetsSelected[dataset]}'`;

            switch (datasetsSelected[dataset]) {
                case "SENTINEL-1": {
                    const levelsSelectedNodes = document.querySelectorAll('input[name="sentinel-1-levels"]:checked');
                    const levelsSelected = Array.from(levelsSelectedNodes).map(checkbox => checkbox.value);

                    const sensingTypesSelectedNodes = document.querySelectorAll('input[name="sentinel-1-sensing-types"]:checked');
                    const sensingTypesSelected = Array.from(sensingTypesSelectedNodes).map(checkbox => checkbox.value);

                    const productTypesSelectedNodes = document.querySelectorAll('input[name="sentinel-1-product-types"]:checked');
                    const productTypesSelected = Array.from(productTypesSelectedNodes).map(checkbox => checkbox.value);

                    const polarisationChannelsSelectedNodes = document.querySelectorAll('input[name="sentinel-1-polarisation-channels"]:checked');
                    const polarisationChannelsSelected = Array.from(polarisationChannelsSelectedNodes).map(checkbox => checkbox.value);
                    const combinedPolarisationChannelsSelectedNodes = document.querySelectorAll('input[name="sentinel-1-combined-polarisation-channels"]:checked');
                    const combinedPolarisationChannelsSelected = Array.from(combinedPolarisationChannelsSelectedNodes).map(checkbox => checkbox.value);

                    if (levelsSelected.length <= 0 || sensingTypesSelected.length <= 0 || productTypesSelected.length <= 0) {
                        await showAlert("Warning", "Not enough parameters specified!", false);
                    }

                    let selectedFilters = new Map();

                    selectedFilters.set('levels', levelsSelected);
                    let levelsApiCall = undefined;
                    if (levelsSelected.length > 0) {
                        levelsApiCall = `(${levelsSelected.map(
                            level => `Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'processingLevel' and att/OData.CSC.StringAttribute/Value eq '${level}')`
                        ).join(' or ')})`;
                    }

                    selectedFilters.set('sensing_types', sensingTypesSelected);
                    let sensingTypesApiCall = undefined;
                    if (sensingTypesSelected.length > 0) {
                        sensingTypesApiCall = `(${sensingTypesSelected.map(
                            sensingType => `Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'operationalMode' and att/OData.CSC.StringAttribute/Value eq '${sensingType}')`
                        ).join(' or ')})`;
                    }

                    selectedFilters.set('product_types', productTypesSelected);
                    let productTypesApiCall = undefined;
                    if (productTypesSelected.length > 0) {
                        productTypesApiCall = `(${productTypesSelected.map(
                            productType => `Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq '${productType}')`
                        ).join(' or ')})`;
                    }

                    selectedFilters.set('polarisation_channels', polarisationChannelsSelected);
                    selectedFilters.set('polarisation_channels_combined', combinedPolarisationChannelsSelected);
                    /*
                    // It seems like it is not possible to search OData using polarisationChannels
                    let polarisationChannelsApiCall = undefined;
                    if (polarisationChannelsSelected.length > 0) {
                        polarisationChannelsApiCall = `(${polarisationChannelsSelected.map(
                            polarisationChannel => `Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'polarisationChannels' and att/OData.CSC.StringAttribute/Value eq '${polarisationChannel}')`
                        ).join(' or ')})`;
                    }
                    */

                    filtersGlobal.set(datasetsSelected[dataset], selectedFilters);
                    filters += `${datasetFilter} and (${levelsApiCall} and ${sensingTypesApiCall} and ${productTypesApiCall})`; //and ${polarisationChannelsApiCall})`;

                    break;
                }

                case "SENTINEL-2": {
                    const cloudCover = document.querySelector('#sentinel-2-cloud-cover-value').value;

                    const levelsSelectedNodes = document.querySelectorAll('input[name="sentinel-2-levels"]:checked');
                    const levelsSelected = Array.from(levelsSelectedNodes).map(checkbox => checkbox.value);

                    const bandsSelectedNodes = document.querySelectorAll('input[name="sentinel-2-bands"]:checked');
                    const bandsSelected = Array.from(bandsSelectedNodes).map(checkbox => checkbox.value);

                    if (levelsSelected.length <= 0 || bandsSelected.length <= 0) {
                        await showAlert("Warning", "Not enough parameters specified!", false);
                    }

                    let selectedFilters = new Map();

                    selectedFilters.set('cloud_cover', cloudCover);
                    let cloudCoverApiCall = `Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value le ${cloudCover}.00)`;


                    selectedFilters.set('levels', levelsSelected);
                    let levelsApiCall = undefined;
                    if (levelsSelected.length > 0) {
                        levelsApiCall = `(${levelsSelected.map(
                            level => `Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq '${level}')`
                        ).join(' or ')})`;
                    }

                    selectedFilters.set('bands', bandsSelected);
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
                    await showAlert("Warning", "Unexpected datasource chosen!", false);
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

        let availableFeaturesSelect = document.querySelector("#available-features-select");
        availableFeaturesSelect.innerHTML = '';

        const obtainedFeaturesMap = new Map();
        obtainedFeatures.forEach(obtainedFeature => {
            obtainedFeaturesMap.set(obtainedFeature.Id, obtainedFeature);
        });

        const featuresIds = new Set(obtainedFeatures.map(item => item.Id));

        let finalFeatures = [];
        for (let featureId of featuresIds) {
            finalFeatures.push(obtainedFeaturesMap.get(featureId));
        }

        finalFeatures.sort((a, b) => a.Name.toLowerCase().localeCompare(b.Name.toLowerCase()));

        featuresGlobal = new Map();

        for (const feature of finalFeatures) {
            featuresGlobal.set(feature.Id, feature);

            let option = document.createElement("option");
            option.value = feature.Id;
            option.textContent = feature.Name;
            availableFeaturesSelect.appendChild(option);
        }

        showBorders();

        if (obtainedFeatures.length > 0) {
            enableUIElements()
        } else {
            enableUIElements()
            await showAlert("Warning", "No features found for selected filters!", false);
        }

    } catch (error) {
        await showAlert('Error', `Internal application error occurred. Please check console for further information.`, true);
        console.error(`Error fetching tiles!  Error name: ${error.name}; Error message: ${error.message}`);
    } finally {
        hideSpinner();
    }
};

const disableUIElements = () => {
    document.querySelector("#visualize-feature-button-div").classList.add("disabled-element");
    document.querySelector("#available-features-select-div").classList.add("disabled-element");
    document.querySelector("#processed-products-select-div").classList.add("disabled-element");
    document.querySelector("#open-product-button-div").classList.add("disabled-element");
}

const enableUIElements = () => {
    document.querySelector("#visualize-feature-button-div").classList.remove("disabled-element");
    document.querySelector("#available-features-select-div").classList.remove("disabled-element");
    document.querySelector("#processed-products-select-div").classList.remove("disabled-element");
    document.querySelector("#open-product-button-div").classList.remove("disabled-element");
}


const clearCoordinates = () => {
    document.querySelector("#coordinates-nw-input").value = ""
    document.querySelector("#coordinates-se-input").value = ""
}

class VisualizationRequest {
    constructor(featureId, status, hrefs) {
        this.featureId = featureId;
        this.status = status;
        this.hrefs = hrefs;
    }

    isInitialized() {
        return (this.featureId !== undefined)
            && (this.status !== undefined)
            && (this.hrefs !== undefined);
    }

    getHrefs() {
        return this.hrefs;
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
        window.open(selectedValue, '_blank');
    }
}

const visualize = async () => {
    let visualizationRequest = await requestVisualization()

    let processedProductsSelect = document.querySelector("#processed-products-select");
    processedProductsSelect.innerHTML = '';

    visualizationRequest.getHrefs().forEach(processedProduct => {
        console.log(processedProduct);
        let option = document.createElement("option");
        option.value = processedProduct;
        const processedProductParst = processedProduct.split('/')
        option.textContent = processedProductParst[processedProductParst.length - 1];
        processedProductsSelect.appendChild(option);
    });

    enableUIElements()
}

const requestVisualization = async () => {
    showSpinner();

    const repeatRequestAfter = 5 * 1000 // millisecs
    const totalTimeout = 120 // secs // TODO timeout of backend processing after 120 sec. Enough?
    const backendReplyTimeout = 30 * 1000;  // 1 sec = 1 000 millisecs // TODO timeout of backend call after 30 sec. Enough?

    const featureId = document.querySelector("#available-features-select").value;
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

    let visualizationRequest = new VisualizationRequest(undefined, undefined, undefined);

    try {
        let url = `${backendHost}/api/request_visualization`
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
                data.hrefs
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
            await showAlert("Warning", "Request timed out!", false);
        } else if (error.message.includes('NetworkError')) {
            await showAlert("Warning", `Network error - connection to backend failed! Please try again later.`, true);
        } else {
            await showAlert("Error", `Internal application error occurred! Please check console for more information.`, true);
            console.error(`Error name: ${error.name}; Error message: ${error.message}`);
        }
    } finally {
        hideSpinner();
    }

    if (visualizationRequest.isInitialized() !== true) {
        throw new Error("Request is not initialized!"); // todo proper exception
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

let showedPolygon = null;

const showBorders = () => {
    if (showedPolygon) {
        showedPolygon.remove()
    }

    let featureId = document.querySelector("#available-features-select").value;
    if (!featureId) {
        return;
    }

    let coordinates = transposeCoordinates(featuresGlobal.get(featureId).GeoFootprint.coordinates[0]);

    showedPolygon = L.polygon(coordinates, {
        color: 'black', //obrys
        fillColor: 'black', //vypln
        fillOpacity: 0.3
    }).addTo(leafletMap);

    isUserInteractingWithMap = false;
    leafletMap.fitBounds(showedPolygon.getBounds());
    leafletMap.once('moveend', () => {
        isUserInteractingWithMap = true;
    });
};

const showExampleGeoTiff = async () => {
    spinner.style.display = "block";

    await fetch("http://127.0.0.1:8080/example.tif")
        .then(response => response.arrayBuffer())
        .then(arrayBuffer => {
            parseGeoraster(arrayBuffer).then(georaster => {
                console.log("georaster:", georaster);

                /*
                    GeoRasterLayer is an extension of GridLayer,
                    which means can use GridLayer options like opacity.

                    Just make sure to include the georaster option!

                    Optionally set the pixelValuesToColorFn function option to customize
                    how values for a pixel are translated to a color.

                    https://leafletjs.com/reference.html#gridlayer
                */
                var layer = new GeoRasterLayer({
                    georaster: georaster,
                    opacity: 0.75,
                    resolution: 256 // optional parameter for adjusting display resolution
                });
                layer.addTo(leafletMap);

                leafletMap.fitBounds(layer.getBounds());

                spinner.style.display = "none";
            });
        });
}

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
        await showAlert("Unknown mission!", `Unexpected mission selected`, false);
    }
}

const toggleSentinel1HHHV = () => {
    if (document.querySelector("#sentinel-1-combined-hhhv-checkbox").checked) {
        document.querySelector("#sentinel-1-hh-checkbox").checked = true;
        document.querySelector("#sentinel-1-hv-checkbox").checked = true;
    }
}

const toggleSentinel1VVVH = () => {
    if (document.querySelector("#sentinel-1-combined-vvvh-checkbox").checked) {
        document.querySelector("#sentinel-1-vv-checkbox").checked = true;
        document.querySelector("#sentinel-1-vh-checkbox").checked = true;
    }
}

const toggleSentinel1CombinedHHHV = () => {
    if (document.querySelector("#sentinel-1-combined-hhhv-checkbox").checked) {
        if (
            !document.querySelector("#sentinel-1-hh-checkbox").checked ||
            !document.querySelector("#sentinel-1-hv-checkbox").checked
        ) {
            document.querySelector("#sentinel-1-combined-hhhv-checkbox").checked = false;
        }
    }
}

const toggleSentinel1CombinedVVVH = () => {
    if (document.querySelector("#sentinel-1-combined-vvvh-checkbox").checked) {
        if (
            !document.querySelector("#sentinel-1-vv-checkbox").checked ||
            !document.querySelector("#sentinel-1-vh-checkbox").checked
        ) {
            document.querySelector("#sentinel-1-combined-vvvh-checkbox").checked = false;
        }
    }
}

const toggleSentinel1Checkbox = () => {
    if (
        document.querySelectorAll('input[name="sentinel-1-levels"]:checked').length <= 0
        && document.querySelectorAll('input[name="sentinel-1-sensing-types"]:checked').length <= 0
        && document.querySelectorAll('input[name="sentinel-1-data-types"]:checked').length <= 0
    ) {
        document.querySelector("#mission-filter-checkbox-sentinel-1").checked = false;
    } else {
        document.querySelector("#mission-filter-checkbox-sentinel-1").checked = true;
    }
}

const toggleSentinel2Checkbox = () => {
    if (
        document.querySelectorAll('input[name="sentinel-2-levels"]:checked').length <= 0
        && document.querySelectorAll('input[name="sentinel-2-bands"]:checked').length <= 0
        && document.querySelectorAll('input[name="sentinel-2-misc"]:checked').length <= 0
    ) {
        document.querySelector("#mission-filter-checkbox-sentinel-2").checked = false;
    } else {
        document.querySelector("#mission-filter-checkbox-sentinel-2").checked = true;
    }
}

const toggleSentinel1AdditionalCheckboxes = () => {
    if (!document.querySelector("#mission-filter-checkbox-sentinel-1").checked) {
        document.querySelectorAll("#mission-filters-sentinel-1-div input[type=checkbox]").forEach((checkbox) => {
            checkbox.checked = false;
        })
    } else {
        document.querySelectorAll("#mission-filters-sentinel-1-div input[type=checkbox]").forEach((checkbox) => {
            checkbox.checked = true;
        })
    }
}

const toggleSentinel2AdditionalCheckboxes = () => {
    if (!document.querySelector("#mission-filter-checkbox-sentinel-2").checked) {
        document.querySelectorAll("#mission-filters-sentinel-2-div input[type=checkbox]").forEach((checkbox) => {
            checkbox.checked = false;
        })
    } else {
        document.querySelectorAll("#mission-filters-sentinel-2-div input[type=checkbox]").forEach((checkbox) => {
            checkbox.checked = true;
        })
    }
}

const toggleSentinel2RGBCheckbox = () => {
    if (document.querySelector("#sentinel-2-rgb-checkbox").checked) {
        if (
            !document.querySelector("#sentinel-2-b2-checkbox").checked ||
            !document.querySelector("#sentinel-2-b3-checkbox").checked ||
            !document.querySelector("#sentinel-2-b4-checkbox").checked
        ) {
            document.querySelector("#sentinel-2-rgb-checkbox").checked = false;
        }
    }
}

const toggleSentinel2RGBBandsCheckboxes = () => {
    if (document.querySelector("#sentinel-2-rgb-checkbox").checked) {
        document.querySelector("#sentinel-2-b2-checkbox").checked = true;
        document.querySelector("#sentinel-2-b3-checkbox").checked = true;
        document.querySelector("#sentinel-2-b4-checkbox").checked = true;
    }
}
