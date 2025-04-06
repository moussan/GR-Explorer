# GR Explorer

An interactive educational tool for exploring General Relativity concepts, including tensor calculus, Einstein Field Equations, and black hole dynamics.

## Project Goal

To provide an accessible, Docker-based application for students and researchers to visualize and compute fundamental quantities in GR.

## Architecture

- **Frontend:** React (served on port 3000)
- **Backend:** Python (FastAPI) with SymPy/NumPy/SciPy (API on port 5000)
- **Deployment:** Docker Compose

## Setup & Running

1.  Ensure Docker and Docker Compose are installed.
2.  Clone the repository.
3.  Run the application:
    ```bash
    docker-compose up --build
    ```
4.  Access the frontend at `http://localhost:3000`.
5.  The backend API is accessible at `http://localhost:5000` (e.g., `http://localhost:5000/docs` for FastAPI docs).

## Development

- Backend code is in `./backend/app`.
- Frontend code is in `./frontend/src`.
- Saved scenarios are stored in the `./data` directory (mounted into the backend container).

## TODO

- Implement core GR calculation logic in `backend/app/core`.
- Define API endpoints in `backend/app/api`.
- Build out frontend components for metric input, results display, visualization, etc.
- Add unit and integration tests.
- Refine educational content integration.
