# Challenge-ML

## Overview

The `challenge-ml` project is a web scraping application built with Python, Selenium, and BeautifulSoup. It is designed to perform the following tasks:

1. **Extract Product Information:**

   - Scrapes product details from search pages on e-commerce platforms and marketplaces. (amazon in this example)
   - Structures the data into a Pandas DataFrame and saves it to a CSV file.
   - Includes insights on the number of products found in the search.

2. **Process Superfinanciera Colombia Data:**

   - Accesses the Superfinanciera Colombia website.
   - Extracts the first row of a table and downloads the PDF linked from this row.
   - Interprets the PDF using Tesseract and pdfplumber.

3. **Solve CAPTCHAs:**
   - **Image CAPTCHAs:** Downloads the image and uses 2captcha for solving.
   - **Audio CAPTCHAs:** Downloads the audio, then uses OpenAI's Whisper model API to transcribe the audio content.

## Getting Started

### Prerequisites

Ensure you have the following installed:

- Python 3.10 or higher
- Poetry (for managing dependencies)

### Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/challenge-ml.git
   cd challenge-ml
   ```

2. **Install Dependencies:**

   ```bash
   poetry install
   ```

3. **Activate the Virtual Environment:**

   ```bash
   poetry shell
   ```

### Configuration

1. **Environment Variables:**

   Set the following environment variables as needed:

   - 'HEADLESS': 'True'
   - 'OPEN_AI_API_KEY': ''
   - 'SOLVER_API_KEY': ''

   Example:

   ```bash
   export HEADLESS=True
   ```

2. **API Keys and Secrets:**

   Make sure you are using the correct API keys and secrets to services like 2captcha and OpenAI. Use the command above with the information provided privately to consume the services.

### Running the Project

1. **Start the Application:**

   Run the application using Poetry

   ```bash
   poetry run python src/start.py
   ```

## Project Structure

- `src/`: Contains the main application code.
  - `start.py`: Entry point for the application
  - `browser/`: Contains browser provider and scraping logic.
    - `providers/`: Contains the abstract browser class and the actions dictionary.
    - `scrapers/`: Contains specific scrapers for different tasks.
      - `configs/`: Stores the .json files containing the configurations for the execution.
  - `tools/`: Contains utility modules like CSV handler.

## Error Handling and Logging

- Common errors include file download issues and CAPTCHA solving failures. Ensure network connectivity and valid API keys.
