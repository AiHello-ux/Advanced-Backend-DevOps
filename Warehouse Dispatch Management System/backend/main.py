from fastapi import FastAPI, HTTPException,Header
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
 
@app.post("/packages")
def register_package(package_name: str, destination: str, weight: float, arrival_date: date, status: str):
    if status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid status.")
    return functions.register_package(package_name=package_name, destination=destination, weight=weight, arrival_date=arrival_date, status=status)
 
 
@app.get("/packages/{id}")
def get_one_package(id: int):
    result = functions.get_one_package(id=id)
    if not result:
        raise HTTPException(status_code=404, detail="Package not found")
    return result
 
@app.patch("/packages/{id}")
def update_package(id: int, package_name: str = None, destination: str = None, weight: float = None, arrival_date: date = None, status: str = None):
    if status and status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="invalid status.")
    result = functions.update_package(id=id, package_name=package_name, destination=destination, weight=weight, arrival_date=arrival_date, status=status)
    if not result:
        raise HTTPException(status_code=404, detail="package not found")
    return result
 
@app.delete("/packages/{id}")
def delete_package(id: int,token = Header(None)):
    token = functions.verify_token(token=token)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    package = functions.get_one_package(id=id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    if package["status"] == "dispatched":
        raise HTTPException(status_code=400, detail="Dispatched package cannot be deleted")
    return functions.delete_package(id=id)
 
@app.post("/login")
def login(username:str,password:str):
    tokens = functions.login(username=username,password=password)
    if tokens is None:
        raise HTTPException(status_code=401,detail="Invalid credentials")
    return tokens

@app.post("/refresh")
def refresh(refresh_token):
    username = functions.verify_token(token=refresh_token,token_type="refresh")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired Token")
    access_token = functions.create_token(username=username,token_type="access")
    return {"access_token":access_token}

@app.get("/packages/search")
def search_packages(destination: str = None, status: str = None, arrival_date: date = None):
    if status and status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid status.")
    return functions.search_packages(destination=destination, status=status, arrival_date=arrival_date)

@app.get("/dispatch-batches")
def view_dispatch_batches(destination: str = None, vehicle: str = None, dispatch_status: str = None):
    if dispatch_status and dispatch_status not in VALID_BATCH_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid dispatch status.")
    return functions.view_dispatch_batches(destination=destination, vehicle=vehicle, dispatch_status=dispatch_status)