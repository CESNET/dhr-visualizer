const backendHost = 'http://127.0.0.1:8000';
const apiRoot = "https://catalogue.dataspace.copernicus.eu";
const supportEmail = "placeholder@example.com"; //TODO Change email

let leafletMap = L.map('mapDiv').setView([50.05, 14.46], 10);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data (c) <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
    maxZoom: 19,
}).addTo(leafletMap);
insertCoordinatesFromMap();

let timeFrom = new Date();
timeFrom.setUTCMonth(timeFrom.getUTCMonth() - 1);
timeFrom.setUTCHours(0);
timeFrom.setUTCMinutes(0);
timeFrom.setUTCSeconds(0);

let timeFromInput = document.querySelector("#timeFromInput");
timeFromInput.value = timeFrom.toISOString().substring(0, 16);

let timeTo = new Date();
timeTo.setUTCHours(23);
timeTo.setUTCMinutes(59);
timeTo.setUTCSeconds(59);

let timeToInput = document.querySelector("#timeToInput");
timeToInput.value = timeTo.toISOString().substring(0, 16);

const offeredDatasets = [
    "SENTINEL-1",
    "SENTINEL-2"
];

const prepareDatasetSelect = () => {
    /*
        // All possible datasets:
            const offeredDatasets = [
            // Copernicus Sentinel Mission
            "SENTINEL-1",
            "SENTINEL-2",
            "SENTINEL-3",
            "SENTINEL-5P",
            "SENTINEL-6",
            "SENTINEL-1-RTC",
            // Complementary data...
            "GLOBAL-MOSAICS",
            "SMOS",
            "ENVISAT",
            "LANDSAT-5",
            "LANDSAT-7",
            "LANDSAT-8",
            "COP-DEM",
            "TERRAAQUA",
            "S2GLC"
            ]
     */

    let datasetsSelect = document.getElementById('datasetsSelect');
    for (let dataset of offeredDatasets) {
        let option = document.createElement("option");
        option.value = dataset;
        option.innerHTML = dataset;
        datasetsSelect.appendChild(option);
    }
}


function insertCoordinatesFromMap() {
    let coordinatesNWInput = document.querySelector("#coordinatesNWInput");
    coordinatesNWInput.value = `${leafletMap.getBounds().getNorthWest().lat.toFixed(4)};${leafletMap.getBounds().getNorthWest().lng.toFixed(4)}`;

    let coordinatesSEInput = document.querySelector("#coordinatesSEInput");
    coordinatesSEInput.value = `${leafletMap.getBounds().getSouthEast().lat.toFixed(4)};${leafletMap.getBounds().getSouthEast().lng.toFixed(4)}`;
}

const closeAlert = (alertDiv) => {
    alertDiv.style.animation = 'slideOut 0.7s forwards';
    alertDiv.addEventListener('animationend', () => {
        alertDiv.remove();
    });
}

const showAlert = async (headline, message) => {
    await fetch('alert.html')
        .then(response => response.text())
        .then(data => {
            let alertDOM = new DOMParser().parseFromString(data, 'text/html');
            alertDOM.getElementById('alertHeadline').innerHTML = headline;
            alertDOM.getElementById('alertMessage').innerHTML = message;

            document.getElementById('alertsDiv').appendChild(alertDOM.getElementById('alertDiv'));
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

const fetchFeaturesFromCopernicus = async (endpoint) => {
    let features = [];

    while (true) {
        let foundNextPage = false;

        try {
            const response = await fetch(endpoint);
            const data = await response.json();

            features = features.concat(data.features);

            for (const link of data.links) {
                if (link.rel === "next") {
                    endpoint = link.href;
                    foundNextPage = true;
                    break;
                }
            }

            if (!foundNextPage) {
                break;
            }

        } catch (error) {
            console.error(`Error fetchig data! Error name: ${error.name}; Error message: ${error.message}`);
            break;
        }
    }

    return features;
};


let features = new Map();
let spinner = document.querySelector("#spinnerDiv");

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
        await showAlert("Warning!", "Coordinates must be in format [dd.dddd;dd.dddd]");
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
    let availableFeaturesSelect = document.getElementById('availableFeaturesSelect');
    availableFeaturesSelect.innerHTML = '';
}

const fetchFeatures = async () => {
    showSpinner();
    document.querySelector("#visualizeFeatureButtonDiv").classList.add("disabledElement");
    clearAvailableFeaturesSelect();

    try {
        // TODO Ošetřit když není zadaná nějaká složka data
        let timeFrom = new Date(document.querySelector("#timeFromInput").value + ":00Z");
        let timeTo = new Date(document.querySelector("#timeToInput").value + ":00Z");

        if (timeTo < timeFrom) {
            await showAlert("Warning!", "Time to must be after Time from!");
            return;
        }

        let tomorrow = new Date();
        tomorrow.setUTCDate(tomorrow.getUTCDate() + 1);
        tomorrow.setUTCHours(0, 0, 0, 0);

        if ((timeFrom > tomorrow) || (timeTo > tomorrow)) {
            await showAlert("Warning!", "Date could not be in the future!");
            return;
        }

        const coordinatesUserInputElements = document.getElementsByClassName("coordinateUserInput")
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

        /*
        let polygon = preparePolygon(
            leafletMap.getBounds().getNorthWest().lat,
            leafletMap.getBounds().getNorthWest().lng,
            leafletMap.getBounds().getSouthEast().lat,
            leafletMap.getBounds().getSouthEast().lng
        );
         */

        /*
        let bbox = prepareBbox(
            leafletMap.getBounds().getNorthWest().lat,
            leafletMap.getBounds().getNorthWest().lng,
            leafletMap.getBounds().getSouthEast().lat,
            leafletMap.getBounds().getSouthEast().lng
        );
        */

        let bbox = prepareBbox(
            coordinatesUserInput[0][0],
            coordinatesUserInput[0][1],
            coordinatesUserInput[1][0],
            coordinatesUserInput[1][1]
        );

        let dataset = document.querySelector("#datasetsSelect").value;

        let endpoint = new URL(["stac", "collections", dataset, "items"].join("/"), apiRoot);
        endpoint.searchParams.set("bbox", bbox);
        endpoint.searchParams.set("datetime", [timeFrom.toISOString(), timeTo.toISOString()].join("/"));
        endpoint.searchParams.set("limit", "100");

        let obtainedFeatures = await fetchFeaturesFromCopernicus(endpoint.href);

        console.log(obtainedFeatures)

        let availableFeaturesSelect = document.querySelector("#availableFeaturesSelect");
        availableFeaturesSelect.innerHTML = '';

        obtainedFeatures.sort((a, b) => a.id.toLowerCase().localeCompare(b.id.toLowerCase()));

        features = new Map();

        for (const feature of obtainedFeatures) {
            features.set(feature.id, feature);

            let option = document.createElement("option");
            option.value = feature.id;
            option.textContent = feature.id;

            availableFeaturesSelect.appendChild(option);
        }

        showBorders();

        if (obtainedFeatures.length > 0) {
            document.querySelector("#visualizeFeatureButtonDiv").classList.remove("disabledElement");
        }
    } catch (error) {
        console.error(`Error fetching tiles!  Error name: ${error.name}; Error message: ${error.message}`);
    } finally {
        hideSpinner();
    }
};

const clearCoordinates = () => {
    document.querySelector("#coordinatesNWInput").value = ""
    document.querySelector("#coordinatesSEInput").value = ""
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
        var response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        return response;

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

    const featureId = document.querySelector("#availableFeaturesSelect").value;

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
                    await showAlert("Warning!", "Request timed out!");
                } else if (error.message.includes('NetworkError')) {
                    await showAlert("Warning!", `Network error - connection to backend failed!   Please try again later. If this problem persists please <a href=\"mailto:${supportEmail}\">contact us</a>.`);
                } else {
                    await showAlert("Warning!", "Unknown error! Please check console for more information.");
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

let showedPolygon = null

const showBorders = () => {
    let featureId = document.querySelector("#availableFeaturesSelect").value;
    let coordinates = transposeCoordinates(features.get(featureId).geometry.coordinates[0]);

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
