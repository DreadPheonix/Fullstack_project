import uvicorn

from Fullstack_project.app import CONFIG, app


if __name__ == "__main__":
    app_config = CONFIG["app"]
    uvicorn.run(
        "Fullstack_project.app:app",
        host=app_config["host"],
        port=app_config["port"],
        reload=False,
    )
