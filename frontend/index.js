const backendHost = 'http://127.0.0.1:8000';
const apiRootUrl = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products";
const supportEmail = "placeholder@example.com"; //TODO Change email

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

let leafletMap = L.map('map-div').setView([50.05, 14.46], 10);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data (c) <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
    maxZoom: 19,
}).addTo(leafletMap);
insertCoordinatesFromMap();


let timeFrom = new Date();
timeFrom.setUTCHours(timeFrom.getUTCHours() - 24);
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

const showAlert = async (headline, message) => {
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
    console.log(endpoint)
    let features = [];

    while (true) {
        try {
            const response = await fetch(endpoint);
            const data = await response.json();
            console.log(data);

            features = features.concat(data.value);

            if (features.length >= 100) {
                // let's not load the whole collection
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
        await showAlert("Warning", "Coordinates must be in format [dd.dddd;dd.dddd]");
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
            await showAlert("Warning", "Time to must be after Time from!");
            return;
        }

        let tomorrow = new Date();
        tomorrow.setUTCDate(tomorrow.getUTCDate() + 1);
        tomorrow.setUTCHours(0, 0, 0, 0);

        if ((timeFrom > tomorrow) || (timeTo > tomorrow)) {
            await showAlert("Warning", "Date could not be in the future!");
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
        //console.log(datasetsSelected);
        if (datasetsSelected.length <= 0) {
            await showAlert("Warning", "Please choose dataset.");
            return;
        }

        // let endpoint = new URL(["stac", "collections", dataset, "items"].join(""), apiRootUrl);
        // endpoint.searchParams.set("bbox", bbox);
        // endpoint.searchParams.set("datetime", [timeFrom.toISOString(), timeTo.toISOString()].join("/"));
        // endpoint.searchParams.set("limit", "100");

        //console.log(polygon);

        let endpoint = undefined;
        let obtainedFeatures = [];
        for (let dataset in datasetsSelected) {
            switch (datasetsSelected[dataset]) {
                case "SENTINEL-1":
                    const levelsSelectedNodes = document.querySelectorAll('input[name="sentinel-1-levels"]:checked');
                    const levelsSelected = Array.from(levelsSelectedNodes).map(checkbox => checkbox.value);
                    const sensingTypesSelectedNodes = document.querySelectorAll('input[name="sentinel-1-sensing-types"]:checked');
                    const sensingTypesSelected = Array.from(sensingTypesSelectedNodes).map(checkbox => checkbox.value);
                    const dataTypesSelectedNodes = document.querySelectorAll('input[name="sentinel-1-data-types"]:checked');
                    const dataTypesSelected = Array.from(dataTypesSelectedNodes).map(checkbox => checkbox.value);

                    if (levelsSelected.length <= 0 || sensingTypesSelected.length <= 0 || dataTypesSelected.length <= 0) {
                        showAlert("Warning", "Not enough parameters specified!");
                    }

                    //todo
                    endpoint = new URL(
                        `?$filter=OData.CSC.Intersects(area=geography'SRID=4326;${polygon}') and`
                        + ` Collection/Name eq '${datasetsSelected[dataset]}' and ContentDate/Start ge ${timeFrom.toISOString()}`
                        + ` and ContentDate/Start le ${timeTo.toISOString()}`,
                        apiRootUrl
                    );

                    break;
                case "SENTINEL-2":
                    break;
                case "SENTINEL-3":
                //TODO do budoucna přidělat zpracování S3 a S5P
                //break;
                case "SENTINEL-5P":
                //TODO do budoucna přidělat zpracování S3 a S5P
                //break;
                default:
                    showAlert("Warning", "Unexpected datasource chosen!");
                    return;
            }



            let currentFeatures = await fetchFeaturesFromCopernicus(endpoint.href);
            obtainedFeatures = obtainedFeatures.concat(currentFeatures);
        }

        /*
        let filterCondition = datasetsSelected
            .map(source => `Collection/Name eq '${source}'`)
            .join(' or ');

        let endpoint = new URL(`?$filter=OData.CSC.Intersects(area=geography'SRID=4326;${polygon}') and`
            + ` (${filterCondition}) and ContentDate/Start ge ${timeFrom.toISOString()}`
            + ` and ContentDate/Start le ${timeTo.toISOString()}`, apiRootUrl);
        console.log(endpoint.href);

        let obtainedFeatures = await fetchFeaturesFromCopernicus(endpoint.href);
        */

        let availableFeaturesSelect = document.querySelector("#available-features-select");
        availableFeaturesSelect.innerHTML = '';

        obtainedFeatures.sort((a, b) => a.Id.toLowerCase().localeCompare(b.Id.toLowerCase()));

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
            document.querySelector("#visualize-feature-button-div").classList.remove("disabled-element");
        }
    } catch (error) {
        console.error(`Error fetching tiles!  Error name: ${error.name}; Error message: ${error.message}`);
    } finally {
        hideSpinner();
    }
};

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
                    await showAlert("Warning", "Request timed out!");
                } else if (error.message.includes('NetworkError')) {
                    await showAlert("Warning", `Network error - connection to backend failed! Please try again later. <br>If this problem persists please <a href=\"mailto:${supportEmail}\">contact us</a>.`);
                } else {
                    await showAlert("Warning", "Unknown error! Please check console for more information.");
                }

                throw error;
            }

        } while (visualizationRequest.status !== "completed");
    } catch (error) {
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
    let featureId = document.querySelector("#available-features-select").value;
    let coordinates = transposeCoordinates(features.get(featureId).GeoFootprint.coordinates[0]);

    if (showedPolygon) {
        showedPolygon.remove()
    }

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
        await showAlert("Unknown mission!", `Unexpected mission selected. Please <a href=\"mailto:${supportEmail}\">contact us</a>.`);
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
