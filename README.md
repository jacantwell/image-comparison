# Image Comparison MVP

A full-stack web application for detecting and visualising differences between images.

## Quick Start

Ensure Docker is running, then:

```bash
docker compose up
```

Access the application at `http://localhost:3000`

## Features

### Core Functionality
- **Dual Comparison Methods**: Pixel-by-pixel and structural similarity (SSIM) algorithms
- **Multiple Visualisations**: Heatmap and contour-based difference highlighting
- **Adjustable Sensitivity**: Fine-tune detection threshold from 0-100%
- **Comparison History**: Access previous analyses via persistent storage

### Technical Implementation
- **Backend**: FastAPI with OpenCV and scikit-image for image processing
- **Frontend**: Next.js with React for responsive UI
- **Architecture**: RESTful API with in-memory database for rapid prototyping

## Architecture Decisions

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes and dependencies
│   │   ├── config/       # Settings and logging
│   │   ├── database/     # In-memory storage implementation
│   │   ├── lib/          # Core comparison and visualisation logic
│   │   └── models/       # Pydantic schemas and enums
│   └── Dockerfile
├── frontend/
│   ├── app/              # Next.js pages
│   ├── components/       # React components with shadcn/ui
│   └── Dockerfile
└── docker-compose.yml
```

### API Design
I deviated from the specification to follow REST best practices:
- Pluralised endpoint resources (`/comparisons` instead of `/comparison`)
- POST endpoint returns only the comparison ID (not the full result)
- Separate GET endpoint retrieves complete results with visualisations

### Deployment Model
The application assumes local deployment with single-instance usage. The in-memory database resets on restart, making it suitable for development and demonstration purposes rather than production environments.

### Library Structure
The comparison and visualisation modules are designed with extensibility in mind, allowing future implementations to be added without modifying existing code.

## Future Improvements

### Semantic Analysis
Integrate an LLM agent to generate natural language descriptions of visual changes (e.g., "User closed a browser tab" or "Button color changed from blue to red").

### Enhanced Configurability
Expose visualisation parameters through the API, giving users programmatic control over:
- Color schemes and opacity levels
- Contour detection thresholds
- Heatmap intensity ranges

### Performance Optimization
- Implement background job processing for large image comparisons
- Add caching layer for frequently accessed results
- Persistent database storage

## Technical Challenges

### Request/Response Handling
Typically I use Pydantic models for FastAPI request and response bodies, however they don't natively support binary image data due to serialisation limitations. Instead I opted for the `UploadFile` type as shown in the FastAPI docs for request bodies. For responses, because I wanted to return both the score and the image, I had to use base64 encoding rather than just a FastAPI Response with the content defined as a PNG image.


