# Cancer Cell Detector Backend

## Overview

This project is a backend API for a Cancer Cell Detector application, built using [FastAPI](https://fastapi.tiangolo.com/). The API processes medical imaging data to detect cancer cells using machine learning models.

## Features

- High-performance API using FastAPI.
- Supports image upload for cancer cell detection.
- Integrates with machine learning models for prediction.
- Provides endpoints for image processing and prediction results.
- Automatic interactive API documentation.


## Installation

1. **Clone the repository:**

    * git clone git@github.com:AnojAryal/CancerCellDetector.git *or*
    * git clone https://github.com/AnojAryal/CancerCellDetector.git 
    

2. **Create the virtual environment:**

    * python3 -m venv venv
    * source venv/bin/activate


3. **Install the Dependencies**

    pip install -r requirements.txt


4. **Test the application**

    uvicorn app.main:app --reload


5. **Testing endpoints**

    *   /docs - test with swagger
    *  /redoc - test with redoc

## Contributing

If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.


## License
This project is licensed under the terms of the *MIT license*.


## Contact
For any questions or suggestions, feel free to reach out to *anoj1810@gmail.com*.
