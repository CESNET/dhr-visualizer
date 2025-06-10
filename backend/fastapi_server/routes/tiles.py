from fastapi import APIRouter, HTTPException

import fastapi_server.fastapi_shared as fastapi_shared

import io
from PIL import Image
import mercantile

router = APIRouter()

@router.get("/tiles/{z}/{x}/{y}.jpg")
def generate_tile(z: int, x: int, y: int, request_hash: str = Query(..., description="RequestHash")):
    print(request_hash)

    if fastapi_shared.database.get(request_hash) is None:
        return HTTPException(status_code=404, detail="Feature not found in database!")

    tile_bounds = mercantile.bounds(x, y, z)

    left, top = coords_to_pixel(tile_bounds.west, tile_bounds.north)
    right, bottom = coords_to_pixel(tile_bounds.east, tile_bounds.south)

    if right <= left or bottom <= top:
        return Response(status_code=204)  # Empty tile

    if left > img_width or top > img_height or right < 0 or bottom < 0:
        return Response(status_code=204)  # Tile outside image bounds

    # Crop and resize tile
    cropped = image.crop((left, top, right, bottom))
    if cropped.width < 256 or cropped.height < 256:
        try:
            fallback = Image.open("RES_LOW.jpg")
        except FileNotFoundError:
            return Response(status_code=204)
        resized = fallback
    else:
        resized = cropped.resize((256, 256), resample=Image.LANCZOS)

    img_bytes = io.BytesIO()
    resized.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return StreamingResponse(img_bytes, media_type="image/jpeg")