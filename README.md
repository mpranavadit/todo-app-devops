# To-Do App: Flask + SQLite with a Jenkins CI/CD Pipeline

A task manager that is built, tested and deployed automatically. A push to GitHub triggers Jenkins, which builds a Docker image, runs the tests, pushes the image to Docker Hub and deploys it to an AWS EC2 instance.

## Features
- Add, view, edit, complete and delete tasks (full CRUD on SQLite)
- Filters (all, to do, done), progress bar, clear completed
- Stats page and About page
- `/health` endpoint used by the pipeline to verify each deploy
- 13 automated tests

## Tech stack
Flask, SQLite, pytest, Docker, Jenkins, GitHub, Docker Hub, AWS EC2

## Project structure
```
todo-app/
├── app.py              # routes, database logic
├── templates/          # base, index, edit, stats, about
├── static/style.css    # styling (light and dark mode)
├── test_app.py         # pytest suite
├── requirements.txt
├── Dockerfile
├── Jenkinsfile         # pipeline definition
└── README.md
```

## Run locally
```
python -m venv venv
venv\Scripts\Activate.ps1        # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
pytest
python app.py
```
Open http://localhost:5000. The database file `todo.db` is created automatically.

## Run with Docker
```
docker build -t todo-app:local .
docker run -d --name todo -p 5000:5000 -v todo-data:/data -e DB_PATH=/data/todo.db todo-app:local
```
The `todo-data` volume keeps tasks across container restarts and redeploys.

## Pipeline stages
1. **Checkout** the code from GitHub
2. **Build** the Docker image, tagged with the build number and `latest`
3. **Test** by running pytest inside the image
4. **Push** the image to Docker Hub
5. **Deploy** over SSH to the app server (replaces the running container)
6. **Verify** by calling `/health`

## Release flow
Change `APP_VERSION` in `app.py`, commit and push. Jenkins starts a build through the GitHub webhook, and the new version goes live with no manual steps.
