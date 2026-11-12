from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
import functions

app = FastAPI(
    title="Warehouse Dispatch Management System",
    description="Warehouse Dispatches"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)

Valid_statuses = ["pending", "received", "dispatched"]
Valid_dispatch_batches = ["pending", "dispatched"]


class BatchCreate(BaseModel):
    destination: str
    vehicle: str
    dispatch_status: str
    package_ids: list[int]


@app.post("/packages", status_code=201)
def register_package(package_name: str, destination: str, weight: str, arrival_date: date, status: str):

    if status not in Valid_statuses:
        raise HTTPException(status_code=422, detail="Invalid status.")

    result = functions.register_package(
        package_name=package_name,
        destination=destination,
        weight=weight,
        arrival_date=arrival_date,
        status=status
    )

    return result


@app.get("/packages/{id}")
def get_one_package(id: int):

    result = functions.get_one_package(id=id)

    if result is None:
        raise HTTPException(status_code=404, detail="Package not found")

    return result


@app.patch("/packages/{id}")
def update_package(id: int, package_name: str = None, destination: str = None, weight: float = None, arrival_date: date = None, status: str = None):

    if status is not None and status not in Valid_statuses:
        raise HTTPException(status_code=422, detail="Invalid status.")

    result = functions.update_package(
        id=id,
        package_name=package_name,
        destination=destination,
        weight=weight,
        arrival_date=arrival_date,
        status=status
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Package not found")

    return result


@app.delete("/packages/{id}")
def delete_package(id: int):

    package = functions.get_one_package(id=id)

    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")

    if package["status"] == "dispatched":
        raise HTTPException(status_code=400, detail="Dispatched package cannot be deleted")

    functions.delete_package(id=id)

    return {"message": "Package deleted successfully"}


@app.get("/packages")
def search_packages(destination: str = None, status: str = None, arrival_date: date = None):

    if status is not None and status not in Valid_statuses:
        raise HTTPException(status_code=422, detail="Invalid status.")

    result = functions.search_packages(
        destination=destination,
        status=status,
        arrival_date=arrival_date
    )

    return result


@app.get("/batches")
def search_batches(destination: str = None, vehicle: str = None, dispatch_status: str = None):

    if dispatch_status is not None and dispatch_status not in Valid_dispatch_batches:
        raise HTTPException(status_code=422, detail="Invalid dispatch status.")

    result = functions.search_batches(
        destination=destination,
        vehicle=vehicle,
        dispatch_status=dispatch_status
    )

    return result



    if batch.dispatch_status not in Valid_dispatch_batches:
        raise HTTPException(status_code=422, detail="Invalid dispatch status.")

    for package_id in batch.package_ids:
        package = functions.get_one_package(id=package_id)

        if package is None:
            raise HTTPException(status_code=404, detail="Package not found")

        if package["batch_id"] is not None:
            raise HTTPException(status_code=400, detail="Package already assigned to a batch")

    result = functions.create_batch(
        destination=batch.destination,
        vehicle=batch.vehicle,
        dispatch_status=batch.dispatch_status,
        package_ids=batch.package_ids
    )

    return result