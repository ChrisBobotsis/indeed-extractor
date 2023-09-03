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

-q represents the "What"

-r Within X Kilometers

-l represents the "Where"

-m The maximum number of results you would like extracted

Below is an example of what these extraction criteria represent on the actual indeed website:

[![alt text](/images/indeed.png " ")](/images/indeed.png)

The file will be saved in `./data/csv/`.

### Constants File

The default URL to search for is `https://ca.indeed.com`. You can change the URL in `constants.py`.

### Geckodriver

Please not that this repository uses selenium with firefox to extract the job description data from indeed. You will need to place a `geckodriver` (used for firefox) in a location accessible by Python. 

One example is to place the `geckodriver` in `/usr/local/bin`

```
/usr/local/bin/geckodriver
```


