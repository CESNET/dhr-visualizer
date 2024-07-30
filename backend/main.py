import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# TODO odebrat na produkci
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

db = {}  # TODO Daatabase needed


class ReqeustedFeature(BaseModel):
    feature_id: str = None

    def start_map_tile_generation(self):
        # Todo Generovat tilu
        """
        Stažení tily identifikované pomocí feature_id z copernicus dataspace
        Pravděpodobně z jejich s3 na loklání uložiště. Poté spustit processing dané tily
        Po dokončení processingu zápis do DB ohledně dokončení generování

        Na stav se bude ptát peridociky forntend voláním /api/check_visualization_status
        """

        import time
        time.sleep(10)


        db[self.feature_id] = {
            "feature_id": self.feature_id,
            "status": "completed",
            "href": f"http://cesnet.cz/tile/{self.feature_id}"
        }


@app.post("/api/request_visualization")
async def request_visualization(background_tasks: BackgroundTasks,
                                requested_feature: ReqeustedFeature = ReqeustedFeature()):
    db[requested_feature.feature_id] = {
        "feature_id": requested_feature.feature_id,
        "status": "processing",
        "href": ""
    }
    background_tasks.add_task(requested_feature.start_map_tile_generation)

    return db[requested_feature.feature_id]


@app.get("/api/check_visualization_status")
async def check_visualization_status(feature_id: str):
    if feature_id in db:
        return db[feature_id]
    else:
        return HTTPException(status_code=404, detail=f"{feature_id} not found!")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
