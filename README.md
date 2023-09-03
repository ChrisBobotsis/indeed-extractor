# indeed-extractor
A repository allowing the downloading of job postings from indeed for the purpose of job search analytics.

## Setup

### Python and Requirements

Please use Python 3.9.0 for this repository (see Pyenv for details).

Create a virtual environment and install the `requirements.txt` file.

```
python -m venv env

source env/bin/activate

pip install -r requirements.txt
```

### Running the Script

You can run the script in the following manner:

```
python indeed.py  python indeed.py -q '<search_query>' -r <within x kilometers> -l '<location>' -m <max_results>
```

The file will be saved in `./data/csv/`.

### Constants File

The default URL to search for is `https://ca.indeed.com`. You can change the URL in `constants.py`.


