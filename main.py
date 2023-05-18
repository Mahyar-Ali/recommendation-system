import asyncio

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.config import app_env
from src.configurations.Requests import (
    Content_Moderation_Request,
    Recommendation_Product_Request,
    Recommendation_User_Request,
    Review_Calculation_Request,
)
from src.controllers.Get_Product_Recommendation import Recommend_Products
from src.controllers.Ratings_From_Review import Ratings_From_Review
from src.controllers.User_Based_Recommendation import User_Based_Recommendation
from src.Global_Locks import Product_Clusters_Model_Lock
from src.update_models.Product_Recommendation_Model_Update import Update_Product_Model
from src.update_models.User_Product_Recommendation_Model_Update import Update_User_Model
from src.utils.inappropriate_content import check_for_inappropriate_content

# TODO: prevent shutdown after each call https://stackoverflow.com/questions/65505710/why-is-my-fastapi-or-uvicorn-getting-shutdown (not sure why it's doing that)


app = FastAPI()


@app.post("/v1/recommend-user")
async def user_recommendation(request: Recommendation_User_Request):
    request_dict = request.dict()
    try:
        recommended_products = User_Based_Recommendation(
            user_id=request_dict["user_id"]
        )

        output = await recommended_products.recommended_products()

        return JSONResponse({"recommended_products": output})
    except Exception as e:
        return JSONResponse(content={"status": -1, "result": str(e)}, status_code=500)


@app.post("/v1/recommend-product")
async def product_recommendation(request: Recommendation_Product_Request):
    request_dict = request.dict()
    try:
        if Product_Clusters_Model_Lock.lock:
            asyncio.sleep(9)
        if Product_Clusters_Model_Lock.lock:
            return JSONResponse(
                content={"status": -1, "result": "server busy"}, status_code=503
            )

        recommended_products = Recommend_Products(
            product_id=request_dict["product_id"],
            num_responses=request_dict["num_responses"],
        )

        output = await recommended_products.recommend_product()

        return JSONResponse({"recommended_products": output})
    except Exception as e:
        return JSONResponse(content={"status": -1, "result": str(e)}, status_code=500)


@app.post("/v1/update-product-model")
async def update_product_model(request: Recommendation_Product_Request):
    request_dict = request.dict()

    product_model = Update_Product_Model(product_id=request_dict["product_id"])
    await product_model.update_model()


@app.get("/v1/update-user-model")
async def update_user_model():
    product_model = Update_User_Model()
    await product_model.update_model()


@app.post("/v1/moderate")
async def content_moderation(request: Content_Moderation_Request):
    request_dict = request.dict()
    text = request_dict["text"]
    title = request_dict["title"]

    output = await check_for_inappropriate_content(text=text + " " + title)
    return JSONResponse(output)


@app.post("/v1/calculate-ratings")
async def calculate_ratings(request: Review_Calculation_Request):
    request_dict = request.dict()
    ratings_controller = Ratings_From_Review(
        review_text=request_dict["review"],
        quantity=request_dict["quantity"],
        ratings=request_dict["ratings"],
    )
    new_ratings = await ratings_controller.update_ratings()
    return JSONResponse({"ratings": new_ratings})


# To log the RequestValidationError (/422 Unprocessable Entity)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.get("/version")
async def version():
    file = open("VERSION", "r")
    return {"APP_ENV": app_env, "version": file.read()}


if __name__ == "__main__":
    if app_env != "prod" and app_env != "dev":
        uvicorn.run(app="main:app")
