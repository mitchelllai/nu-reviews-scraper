To test the script:
1. Download python and ensure that installation contains the pip package manager.
2. Download pipenv (https://pipenv.pypa.io/en/latest/).
3. Clone this repository, change into the directory.
4. Run command the following command to create the virtual environment and install dependencies:
```
pipenv install
```
5. Ensure that you have a Chrome browser installed.
6. Download a chromedriver executable (https://chromedriver.chromium.org/downloads) that matches your version of Chrome, and place the executable in a file that is in your system PATH. 
7. Copy a .env file that connects to a MongoDB cluster into the root directory of this repo.
8. Run the script from the root of this directory as follows:
```
python scraper.py
```
