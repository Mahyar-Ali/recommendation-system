# User-and-Product-Based-Recommednation-System
Recommendation system using clustering for Product based recommendation and Query/Candidate model for User based recommendation.

## Setup project

### Install dependency

- RUN | `pip install --upgrade pip`
- RUN | `pip install -r requirements.txt`
- RUN | `python install.py`

### How to run

- `uvicorn main:app` (optionally add `--reload` when on local, `uvicorn main:app --reload`)

`gunicorn -b 0.0.0.0:8080 -c gunicorn.conf.py app:app`

### Docker

- Build `docker build -t recommender-system .`

- Run `docker run -p 8080:8080 recommender-system`