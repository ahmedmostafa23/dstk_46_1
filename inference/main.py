import os
import json
from typing import List

from fastapi import FastAPI, Request, Depends, Security, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status
from dotenv import load_dotenv

load_dotenv()

from src.inference_code import model_inference, batch_inference, load_model

from data_models.api_resonse_schema import APIResponse
from data_models.employee_data_schema import EmployeeData
from data_models.model_inference_response_schema import ModelInferenceResponseSchema

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # "*" allows all origins (IPs) (not recommended for production)
    allow_credentials=True,
    allow_methods=["*"], # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Allow all headers
)

def get_api_key():
    return os.environ["API_KEY"] 

api_key_header = APIKeyHeader(
    name="API_KEY",
    auto_error=True
)

def authenticate(request_api_key: str = Security(api_key_header), api_key=Depends(get_api_key)):
    if request_api_key != api_key:
        raise HTTPException(
            status_code=403,
            detail="The API_KEY provided in the headers is incorrect."
        )
    
model = load_model()
def get_model():
    return model


@app.get("/health")
async def health_handler():
    return APIResponse(
            detail="healthy",
    )

@app.post("/model/inference", status_code=status.HTTP_200_OK, response_model=APIResponse[ModelInferenceResponseSchema])
async def model_inference_handler(employee_data: EmployeeData, request: Request, model = Depends(get_model), authentication = Security(authenticate)):
    return APIResponse(
        detail="Successful inference.",
        result=model_inference(model, employee_data.model_dump())
    )

def load_config():
    # 1. default config
    with open("config/default_inference_config.json", "r") as f:
        default_config = json.load(f)
    # 2. custom config
    try:
        with open("config/inference_config.json", "r") as f:
            custom_config = json.load(f)
    except Exception:
        custom_config = {}
    
    # take custom config if key exists, else take default
    config = {}
    all_keys = set(default_config.keys()).union(set(custom_config.keys()))
    for key in all_keys:
        if key in custom_config:
            config[key] = custom_config[key]
        else:
            config[key] = default_config[key]
    
    # override with environment variables if provided
    for env_var in os.environ:
        if env_var.startswith("APP_"):
            config[env_var.removeprefix("APP_").lower()] = os.environ[env_var]

    return config
    
config = load_config()
def get_config():
    global config
    return config

async def limit_batch_inference(request: Request, config=Depends(get_config)):
    request_json = await request.json()
    if len(request_json) > int(config["max_batch_items"]):
        raise HTTPException(
            status_code=413,
            detail=f"The maximum number of employees to batch process is {config['max_batch_items']}."
        )

@app.post("/model/batch_inference", status_code=status.HTTP_200_OK)
async def model_batch_inference_handler(list_of_employee_data: List[EmployeeData], request: Request, model = Depends(get_model), authentication = Security(authenticate), validate_request_input=Depends(limit_batch_inference)):
    return batch_inference(model, [item.model_dump() for item in list_of_employee_data])
