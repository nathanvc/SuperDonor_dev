# SuperDonor_dev

Analysis and metric-learning algorithm development for donor sibling registry duplicate sperm donor listing detection. 

Super-Donor is a web app that detects distinct donors IDs in the Donor Sibling Registry most likely to represent the 
same person. Project built as part of the Insight Health Data Science program. Duplicate donor prediction uses Large Margin 
Nearest Neighbor metric-learning. The jupyter notebookk DSR_analysisexample_superdonor.ipynb in this directory walks through
descriptive analysis of the data set, data cleaning, and development of the detection algorithm and testing. The learning matrix 
produced by this notebook is slightly different than that running in the app due to different randomized word ordering but 
performance is very similar.

See search web-site at http://super-donor.com and code for the web interface at nathanvc/super-donor

Dependencies: Numpy, Pandas, metric-learn, sklearn, psycopg2, PostgreSQL 9.5

Nathan Vierling-Claassen, Ph.D. 2016
