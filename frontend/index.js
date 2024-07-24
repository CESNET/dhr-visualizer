let leafletMap = L.map('mapDiv').setView([50.05, 14.46], 10);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data © <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
    maxZoom: 19,
}).addTo(leafletMap);


var timeFrom = new Date();
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

const apiRoot = "https://catalogue.dataspace.copernicus.eu";

const fetchData = async (endpoint) => {
    let features = [];
    let shouldContinueWhileLoop = true;

    while (shouldContinueWhileLoop) {
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

            shouldContinueWhileLoop = foundNextPage;

        } catch (error) {
            console.error("Error fetching data:", error);
            shouldContinueWhileLoop = false;
        }
    }

    return features;
};

let features = new Map();
let spinner = document.querySelector("#spinnerDiv");

const fetchFeatures = async () => {
    spinner.style.display = "block";

    let timeFrom = new Date(document.querySelector("#timeFromInput").value + ":00Z");
    let timeTo = new Date(document.querySelector("#timeToInput").value + ":00Z");

    if (timeTo < timeFrom) {
        alert("Time to must be after Time from!");
        return;
    }

    let polygon = preparePolygon(
        leafletMap.getBounds().getNorthWest().lat,
        leafletMap.getBounds().getNorthWest().lng,
        leafletMap.getBounds().getSouthEast().lat,
        leafletMap.getBounds().getSouthEast().lng
    );

    let bbox = prepareBbox(
        leafletMap.getBounds().getNorthWest().lat,
        leafletMap.getBounds().getNorthWest().lng,
        leafletMap.getBounds().getSouthEast().lat,
        leafletMap.getBounds().getSouthEast().lng
    );

    let dataset = document.querySelector("#datasetsSelect").value;

    let endpoint = new URL(["stac", "collections", dataset, "items"].join("/"), apiRoot);
    endpoint.searchParams.set("bbox", bbox);
    endpoint.searchParams.set("datetime", [timeFrom.toISOString(), timeTo.toISOString()].join("/"));
    endpoint.searchParams.set("limit", "100");

    try {
        obtainedFeatures = await fetchData(endpoint.href);
    } catch (error) {
        console.error("Error in fetchTiles:", error);
    }

    features = new Map()

    var availableFeaturesSelect = document.querySelector("#availableFeaturesSelect")
    availableFeaturesSelect.innerHTML = '';

    for (const feature of obtainedFeatures) {
        features.set(feature.id, feature)

        let option = document.createElement("option")
        option.value = feature.id
        option.textContent = feature.id

        availableFeaturesSelect.appendChild(option)
    }

    showBorders()

    document.querySelector("#visualizeFeatureButton").disabled = false
    spinner.style.display = "none";
};

class VisualizationRequest {
    constructor(featureId, status, href) {
        this.featureId = featureId;
        this.status = status;
        this.href = href;
    }
}

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

const requestVisualization = async () => {
    spinner.style.display = "block";

    featureId = document.querySelector("#availableFeaturesSelect").value

    setTimeout(async () => {
        featureId = document.querySelector("#availableFeaturesSelect").value

        try {
            const response = await fetch('http://127.0.0.1:8000/api/request_visualization', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    feature_id: featureId,
                }),
            });

            const data = await response.json();
            let visualizationRequest = new VisualizationRequest(
                data.feature_id,
                data.status,
                data.href
            );

            while (visualizationRequest.status !== "completed") {
                await delay(5000);
                visualizationRequest = await checkVisualizationStatus(visualizationRequest.featureId);
                console.log(visualizationRequest);
            }
        } catch (error) {
            console.error('Error:', error);
        } finally {
            spinner.style.display = "none";
        }
    }, 500);
}

const checkVisualizationStatus = async (featureId) => {
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/check_visualization_status?feature_id=${featureId}`, {
            method: 'GET',
        });
        const data = await response.json();
        return new VisualizationRequest(
            data.feature_id,
            data.status,
            data.href
        );
    } catch (error) {
        console.error('Error:', error);
    }
}

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