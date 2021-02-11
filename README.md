eleven



Go into the highest directory (eleven), then install the dependencies with the following command:

pip install -r requirements.txt

then execture the following command:

python -m spacy download en_core_web_sm

also the following (assuming that you have homebrew already installed):

brew install wget && wget -c "https://s3.amazonaws.com/dl4j-distribution/GoogleNews-vectors-negative300.bin.gz"

This will provide you with all the packages necessary to run the files in this repository.



The workflow is as follows:

- First we scrape the reviews in order to get the data necessary to perform the topic modelling and sentiment analysis.
The data can be sourced either from the skytrax website, through the skytrax.py file, or from tripadvisor through the tripadvisor.py file. When either script is run, the data is automatically saved in the 'data' directory.

- Once we have the data we perform the sentiment analysis on the data with the code provided in the nlp_pipeline.py file. The processed data is saved in the 'data_processed' directory.

- Then, we utilize the processed data in order to get deeper insight by doing topic modelling. This can be done by executing the aggregate_aspects.py file. The deeper insight is directly saved in the 'results' directory




Always start from the highest directory

--no_reviews = number of reviews that you want to scrape from skytrax
Example (one review)

python -m scraping.scrapy_test.scrapy_test.skytrax --no_reviews 1

Saves the data in the directory labelled 'data'




--url = url of the airline company on the tripadvisor website
--no_reviews = number of reviews that you want to scrape from skytrax
Example (one review)

Example (scrape 2 pages of reviews of British Airways)

python -m scraping.scrapy_test.scrapy_test.tripadvisor --url https://www.tripadvisor.com/Airline_Review-d8729039-Reviews-British-Airways --no_reviews 1

This will save the output in the directory labelled 'data'




--path to the processed dataset
Example (takes a file from the directory labelled 'data')

--path = path to a dataset in the 'data' directory
python -m nlp_pipeline.nlp_pipeline --path /Users/mathieukremeth/Desktop/eleven/data/Allegiant.csv

Saves the processed file in the directory labelled 'data_processed'





--path = path to dataset in data_processed 
--topic (optional) = topic that you want an in-depth analysis for (file automatically saved in 'results')
--most_freq (int) = number of most frequent items, appearing in the sentiment analysis, that you want to see (in order to pick a topic and have its output saved)

Example (topic food for the processed data of the airline Allegiant)
python -m aggregate_aspects.aggregate_aspects --topic food --path /Users/mathieukremeth/Desktop/eleven/data_processed/nlp_pipeline_Allegiant.csv

Example (print the 10 most frequent items appearing in the sentiment analysis)
python -m aggregate_aspects.aggregate_aspects --most_freq 10





One full runthrough could look as follows:

python -m scraping.scrapy_test.scrapy_test.skytrax --no_reviews 1000 (saves output in 'data')
python -m nlp_pipeline.nlp_pipeline --path /Users/mathieukremeth/Desktop/eleven/data/skytrax-1k.csv (saves output in 'data_processed')
python -m aggregate_aspects.aggregate_aspects --topic food --path /Users/mathieukremeth/Desktop/eleven/data_processed/nlp_pipeline_skytrax-1k.csv (saves output in 'results')

Note, that a file has been added to 'data', 'data_processed' and 'results' to show an example of the working


