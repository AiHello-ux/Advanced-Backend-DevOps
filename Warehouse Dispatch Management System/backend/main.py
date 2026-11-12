from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
import functions
 
app = FastAPI(
    title = "Warehouse Dispatch Management System",
    description = "Warehouse Dispatches"
)
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)
 
VALID_STATUSES = ["pending", "received", "dispatched"]
VALID_BATCH_STATUSES = ["pending", "dispatched"]
 
@app.post("/packages", status_code=201)
def register_package(package_name: str, destination: str, weight: float, arrival_date: date, status: str):
    if status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid status.")
    return functions.register_package(package_name=package_name, destination=destination, weight=weight, arrival_date=arrival_date, status=status)
 
@app.get("/packages")
def search_packages(destination=None, status=None, arrival_date: date = None):
    if status and status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid status.")
    return functions.search_packages(destination=destination, status=status, arrival_date=arrival_date)
 
@app.get("/packages/statistics")
def get_statistics():
    return functions.get_statistics()
 
@app.get("/packages/{id}")
def get_one_package(id: int):
    result = functions.get_one_package(id=id)
    if not result:
        raise HTTPException(status_code=404, detail="Package not found")
    return result
 
@app.patch("/packages/{id}")
def update_package(id: int, package_name: str = None, destination: str = None, weight: float = None, arrival_date: date = None, status: str = None):
    if status and status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid status.")
    result = functions.update_package(id=id, package_name=package_name, destination=destination, weight=weight, arrival_date=arrival_date, status=status)
    if not result:
        raise HTTPException(status_code=404, detail="Package not found")
    return result
 
@app.delete("/packages/{id}")
def delete_package(id: int):
    package = functions.get_one_package(id=id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    if package["status"] == "dispatched":
        raise HTTPException(status_code=400, detail="Dispatched package cannot be deleted")
    return functions.delete_package(id=id)
 
@app.get("/batches")
def search_batches(destination=None, vehicle=None, dispatch_status=None):
    if dispatch_status and dispatch_status not in VALID_BATCH_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid dispatch status.")
    return functions.search_batches(destination=destination, vehicle=vehicle, dispatch_status=dispatch_status)


@app.post("/login")
def login(username:str,passward: str):
    result = functions.login(username=username,passward=passward)
    return result
