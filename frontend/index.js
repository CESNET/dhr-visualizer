const backendHost = 'http://127.0.0.1:8000';
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
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data (c) <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
    maxZoom: 19,
}).addTo(leafletMap);
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

/***************************************
 LOGIC
 **************************************/

function insertCoordinatesFromMap() {
    let coordinatesNWInput = document.querySelector("#coordinates-nw-input");
    coordinatesNWInput.value = `${leafletMap.getBounds().getNorthWest().lat.toFixed(4)};${leafletMap.getBounds().getNorthWest().lng.toFixed(4)}`;

    let coordinatesSEInput = document.querySelector("#coordinates-se-input");
    coordinatesSEInput.value = `${leafletMap.getBounds().getSouthEast().lat.toFixed(4)};${leafletMap.getBounds().getSouthEast().lng.toFixed(4)}`;
}

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
            alertDOM.getElementById('alert-headline').innerHTML = headline;
            alertDOM.getElementById('alert-message').innerHTML = message;

            document.getElementById('alerts-div').appendChild(alertDOM.getElementById('alert-div'));
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
            console.log(data);

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


let features = new Map();
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
}

const fetchFeatures = async () => {
    showSpinner();
    document.querySelector("#visualize-feature-button-div").classList.add("disabled-element");
    clearAvailableFeaturesSelect();

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

        let filters = [];
        let obtainedFeatures = [];
        for (let dataset in datasetsSelected) {
            const datasetFilter = `Collection/Name eq '${datasetsSelected[dataset]}'`;

            switch (datasetsSelected[dataset]) {
                case "SENTINEL-1": {
                    //TODO NOT WORKING!
                    const levelsSelectedNodes = document.querySelectorAll('input[name="sentinel-1-levels"]:checked');
                    const levelsSelected = Array.from(levelsSelectedNodes).map(checkbox => checkbox.value);

                    const sensingTypesSelectedNodes = document.querySelectorAll('input[name="sentinel-1-sensing-types"]:checked');
                    const sensingTypesSelected = Array.from(sensingTypesSelectedNodes).map(checkbox => checkbox.value);

                    const productTypesSelectedNodes = document.querySelectorAll('input[name="sentinel-1-product-types"]:checked');
                    const productTypesSelected = Array.from(productTypesSelectedNodes).map(checkbox => checkbox.value);

                    if (levelsSelected.length <= 0 || sensingTypesSelected.length <= 0 || productTypesSelected.length <= 0) {
                        await showAlert("Warning", "Not enough parameters specified!", false);
                    }

                    for (let level of levelsSelected) {
                        let levelFilter = `Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'processingLevel' and att/OData.CSC.StringAttribute/Value eq '${level}')`;
                        for (let sensingType of sensingTypesSelected) {
                            let sensingTypeFilter = `Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'swathIdentifier' and att/OData.CSC.StringAttribute/Value eq '${sensingType}')`;
                            for (let productType of productTypesSelected) {
                                let productTypeFilter = `Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq '${productType}')`;

                                filters.push(`${datasetFilter} and (${levelFilter} and ${sensingTypeFilter} and ${productTypeFilter})`);
                                //filters.push(`${datasetFilter}`);
                            }
                        }
                    }

                    //filters += ` and (${advancedFilters.join(' or ')})`;

                    /*
                    let levels = undefined;
                    if (levelsSelected.length > 0) {
                        levels = `(${levelsSelected.map(
                            level => `Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'processingLevel' and att/OData.CSC.StringAttribute/Value eq '${level}')`
                        ).join(' or ')})`;
                    }

                    let sensingTypes = undefined;
                    if (sensingTypesSelected.length > 0) {
                        sensingTypes = `(${sensingTypesSelected.map(
                            sensingType => `Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'swathIdentifier' and att/OData.CSC.StringAttribute/Value eq '${sensingType}')`
                        ).join(' or ')})`;
                    }

                    let productTypes = undefined;
                    if (productTypesSelected.length > 0) {
                        productTypes = `(${productTypesSelected.map(
                            productType => `Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq '${productType}')`
                        ).join(' or ')})`;
                    }

                    filters += ` and (${levels} and ${sensingTypes} and ${productTypes})`;
                    */

                    break;
                }

                case "SENTINEL-2": {
                    //TODO NOT WORKING!
                    const levelsSelectedNodes = document.querySelectorAll('input[name="sentinel-2-levels"]:checked');
                    const levelsSelected = Array.from(levelsSelectedNodes).map(checkbox => checkbox.value);

                    const bandsSelectedNodes = document.querySelectorAll('input[name="sentinel-2-bands"]:checked');
                    const bandsSelected = Array.from(bandsSelectedNodes).map(checkbox => checkbox.value);

                    if (levelsSelected.length <= 0 || bandsSelected.length <= 0) {
                        await showAlert("Warning", "Not enough parameters specified!", false);
                    }

                    for (let level of levelsSelected) {
                        let levelFilter = `Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'processingLevel' and att/OData.CSC.StringAttribute/Value eq '${level}')`;

                        filters.push(`${datasetFilter} and (${levelFilter})`);
                        //filters.push(`${datasetFilter}`);
                    }

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
        }

        for (let filter of filters) {
            console.log(filter);

            let filtersQuery = `OData.CSC.Intersects(area=geography'SRID=4326;${polygon}')`;
            filtersQuery += ` and ${filter}`;
            filtersQuery += ` and (ContentDate/Start ge ${timeFrom.toISOString()} and ContentDate/Start le ${timeTo.toISOString()})`;

            const endpoint = new URL(`?$filter=(${filtersQuery})`, apiRootUrl);

            console.log(endpoint.href);
            let currentFeatures = await fetchFeaturesFromCopernicus(endpoint.href);
            obtainedFeatures = obtainedFeatures.concat(currentFeatures);
        }

        let availableFeaturesSelect = document.querySelector("#available-features-select");
        availableFeaturesSelect.innerHTML = '';

        obtainedFeatures.sort((a, b) => a.Name.toLowerCase().localeCompare(b.Name.toLowerCase()));
        console.log(obtainedFeatures)

        features = new Map();

        for (const feature of obtainedFeatures) {
            features.set(feature.Id, feature);

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
}

const enableUIElements = () => {
    document.querySelector("#visualize-feature-button-div").classList.remove("disabled-element");
    document.querySelector("#available-features-select-div").classList.remove("disabled-element");
}


const clearCoordinates = () => {
    document.querySelector("#coordinates-nw-input").value = ""
    document.querySelector("#coordinates-se-input").value = ""
}

class VisualizationRequest {
    constructor(featureId, status, href) {
        this.featureId = featureId;
        this.status = status;
        this.href = href;
    }

    isInitialized() {
        return (this.featureId !== undefined)
            && (this.status !== undefined)
            && (this.href !== undefined);
    }
}

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

const fetchWithTimeout = async (url, options = {}, timeout = 5000) => {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
        return await fetch(url, {
            ...options,
            signal: controller.signal
        });

    } catch (error) {
        console.error(`Error name: ${error.name}; Error message: ${error.message}`)

        throw error;
    } finally {
        clearTimeout(id);
    }
};


const visualize = async () => {
    let visualizationRequest = await requestVisualization()

}

const requestVisualization = async () => {
    showSpinner();

    const featureId = document.querySelector("#available-features-select").value;

    let visualizationRequest = new VisualizationRequest(undefined, undefined, undefined);

    try {
        let url = `${backendHost}/api/request_visualization`
        do {
            try {
                const response = await fetchWithTimeout(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        feature_id: featureId,
                    }),
                }, 30000); // TODO timeout after 30 sec. Enough?

                const data = await response.json();
                console.log(data)
                visualizationRequest = new VisualizationRequest(
                    data.feature_id,
                    data.status,
                    data.href
                );

                if (visualizationRequest.status !== "completed") {
                    console.log(visualizationRequest);
                    await delay(5000);
                }

            } catch (error) {
                if (error.name === 'AbortError') {
                    await showAlert("Warning", "Request timed out!", false);
                } else if (error.message.includes('NetworkError')) {
                    await showAlert("Warning", `Network error - connection to backend failed! Please try again later.`, true);
                } else {
                    await showAlert("Warning", "Unknown error! Please check console for more information.", true);
                }

                throw error;
            }

        } while (visualizationRequest.status !== "completed");
    } catch (error) {
        await showAlert("Error", `Internal application error occurred! Please check console for more information.`, true);
        console.error(`Error name: ${error.name}; Error message: ${error.message}`);
    } finally {
        hideSpinner();
    }

    if (visualizationRequest.isInitialized() !== true) {
        throw new Error("Request is not initialized!") // todo proper exception
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

    let coordinates = transposeCoordinates(features.get(featureId).GeoFootprint.coordinates[0]);

    showedPolygon = L.polygon(coordinates, {
        color: 'black', //obrys
        fillColor: 'black', //vypln
        fillOpacity: 0.3
    }).addTo(leafletMap);

    // To fit the map view to the polygon bounds
    leafletMap.fitBounds(showedPolygon.getBounds());
}

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
    //todo - same as in toggleSentinel1Checkbox()
    document.querySelector("#mission-filter-checkbox-sentinel-2").checked = true;
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
