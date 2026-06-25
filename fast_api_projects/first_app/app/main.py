from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from typing import Any

app = FastAPI()
db={
    1:{"name":"order1","status":"delivered"},
    2:{"name":"order2","status":"pending"},
    3:{"name":"order3","status":"delivered"},
    4:{"name":"order4","status":"pending"},
  
}

@app.get('/shipment/{id}')
def get_shipment_byid(id:int|float)->dict[str,str]:
    return db[id]


@app.get('/shipment')
def get_shipment():
    return{"message": "order deliveredooo"}

@app.get("/scalar",include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
    title="Scaler API",
    
    )