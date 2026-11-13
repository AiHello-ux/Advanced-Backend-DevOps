from fastapi import FastAPI, HTTPException, Header, Body
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
import functions
from pydantic import BaseModel

app = FastAPI(
    title = "Warehouse Dispatch Management System",
    description = "Warehouse Dispatches"
)

class UserRegister(BaseModel):
    username: str
    password: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)
 
VALID_STATUSES = ["pending", "received", "dispatched"]
VALID_BATCH_STATUSES = ["pending", "dispatched"]
 
@app.post("/packages")
def register_package(package_name: str, destination: str, weight: float, arrival_date: date, status: str, token=Header(None)):
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    if status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid status.")
    return functions.register_package(package_name=package_name, destination=destination, weight=weight, arrival_date=arrival_date, status=status)
 
 
@app.get("/packages/search")
def search_packages(destination: str = None, status: str = None, arrival_date: date = None, token=Header(None)):
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    if status and status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid status.")
    return functions.search_packages(destination=destination, status=status, arrival_date=arrival_date)
 
@app.patch("/packages/{id}")
def update_package(id: int, package_name: str = None, destination: str = None, weight: float = None, arrival_date: date = None, status: str = None, token=Header(None)):
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    if payload.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")

    if status and status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="invalid status.")
    result = functions.update_package(id=id, package_name=package_name, destination=destination, weight=weight, arrival_date=arrival_date, status=status)
    if not result:
        raise HTTPException(status_code=404, detail="package not found")
    return result
 
@app.delete("/packages/{id}")
def delete_package(id: int, token=Header(None)):
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    if payload.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")

    package = functions.get_one_package(id=id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    if package["status"] == "dispatched":
        raise HTTPException(status_code=400, detail="Dispatched package cannot be deleted")
    return functions.delete_package(id=id)

@app.get("/statistics")
def warehouse_statistics(token=Header(None)):
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    return functions.warehouse_statistics()

@app.post("/dispatch-batches")
def create_dispatch_batch(
    destination: str,
    vehicle: str,
    dispatch_status: str = "pending",
    package_ids: list[int] = Body(default=None),
    token=Header(None)
):
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    if payload.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")

    if dispatch_status not in VALID_BATCH_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid dispatch status.")
    return functions.create_dispatch_batch(destination=destination,vehicle=vehicle,dispatch_status=dispatch_status,package_ids=package_ids)

@app.get("/packages/{id}")
def get_one_package(id: int, token=Header(None)):
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    result = functions.get_one_package(id=id)
    if not result:
        raise HTTPException(status_code=404, detail="Package not found")
    return result

@app.get("/dispatch-batches")
def view_dispatch_batches(destination: str = None, vehicle: str = None, dispatch_status: str = None, token=Header(None)):
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    if dispatch_status and dispatch_status not in VALID_BATCH_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid dispatch status.")
    return functions.view_dispatch_batches(destination=destination, vehicle=vehicle, dispatch_status=dispatch_status)

@app.post("/login")
def login(username=Body(), password=Body()):
    tokens = functions.verify_login(username=username, password=password)

    if not tokens:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return tokens

@app.post("/refresh")
def refresh(refresh_token):
    payload = functions.verify_token(token=refresh_token, token_type="refresh")

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or Expired Token")

    username = payload.get("username")
    user_type = payload.get("user_type")

    access_token = functions.create_token(username=username, token_type="access", user_type=user_type)

    return {"access_token": access_token}

@app.post("/register")
def register_user(user: UserRegister):
    if functions.register_user(username=user.username, password=user.password):
        return {"message": "user registered successfully"}

    raise HTTPException(status_code=400, detail="Username already exists")
