import copy
import time

from src.config import openai_api
from src.controllers.utils.openai_review_classification import data, prompt
from src.utils.call_apis_async import call_api


class Ratings_From_Review:
    def __init__(self, review_text, quantity, ratings) -> None:
        self.review_text = review_text
        self.quantity = quantity
        self.ratings = ratings
        self.tries = 1
        self.prompt = copy.deepcopy(prompt)
        self.data = copy.deepcopy(data)

    async def use_openai_to_calculate_ratings(self):
        self.prompt[-1]["content"] = str(
            self.prompt[-1]["content"].replace("{REVIEW_TEXT}", self.review_text)
        )

        self.data["messages"] = self.prompt
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api}",
        }
        for _ in range(self.tries):
            json_response, response_status_code = await call_api(
                url, self.data, headers=headers
            )

            if response_status_code == 200:
                response_from_model = json_response["choices"][0]["message"][
                    "content"
                ].strip()

                if response_from_model != "":
                    break

            # we will try again if the response status code is not 200 or the response is empty
            if response_status_code != 200 or response_from_model == "":
                # we will wait for 2 seconds before trying again
                time.sleep(2)

        if response_status_code != 200:
            raise Exception("OPENAI Error", json_response)

        return response_from_model

    async def update_ratings(self):
        call_openai = True
        updated_ratings = self.ratings
        if call_openai:
            response_from_model = await self.use_openai_to_calculate_ratings()
            try:
                updated_ratings = (self.ratings + int(response_from_model)) / (
                    self.quantity + 1
                )
            except:
                pass

        return updated_ratings
