# CrushedIce

Collecting and summarizing news articles from rss feeds

## Setup

CrushedIce runs as a Twisted server, connecting to a MongoDB database to store the summarized articles and
a S3 bucket to store the image files. Internally, the articles are summarized using statistical text analysis. 
Some functionality (tokenization and stemming) uses NLTK (Python natural language toolkit).

Setup requirements in a virtual environment
 
    virtualenv venv
    venv/bin/activate
    pip install -r requirements.txt

To download the required nltk modules, run this code in the python interpreter. CrushedIce expects the nltk
files to be in a subfolder `nltk_data`.

    import nltk
    nltk.download('punkt')
    nltk.download('rslp')
    nltk.download('stopwords')
    
## Configuration 

Create the file `config.py` in the main directory according to the sample file `config.sample.py`. The configuration
file must contain the credentials to MongoDB and S3.