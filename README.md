# Image Comparison

## Usage

This application can be ran loaclly using Docker.

Ensure your Docker Daemon is running and simply run:

```bash
docker compose up
```

The app will now be availble at `http://localhost:3000/`

## Assumptions

I made a couple of deviations from the spec to ensure the backend application follows RestAPI best practices. This includes plurasing the endpoint resources and only returning an ID from the POST endpoint.

This implementation assumes that usage will be via local deployment on users device as the local database only has a single "table" that lists all comparisons that have been created on that server instance. Stopping the server deletes all data.

I designed the library functions under the assumption that there may be different comparison of visualisation implementatison added in the furture.

## Improvements

A cool feature would be semantic comparison using an llm agent, it could take input images and generated visualisations to create a text description of what has changed e.g "User has close a tab"

Currently the visualisation parameters are just set internally, exposing these via the api would give the user greater control on what the output image looked like.

## Challenges

Typically I use pydantic models for FastAPI Request and Reponse bodies however I struggled to using them with encoded images within. Instead I opted for the UploadFile type as shown in the FastAPI docs for request bodies. For response, because I wanted to return the score and the image i had to use base64 encoding rather than just a fastAPI Response with the content defined as a png image.
