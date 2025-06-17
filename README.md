# SuperDonor_dev

Analysis and metric-learning algorithm development for donor sibling registry duplicate sperm donor listing detection. 

Super-Donor is a (now retired) web app that detects distinct donors IDs in the Donor Sibling Registry most likely to represent the 
same person. Project built as part of the Insight Health Data Science program. Duplicate donor prediction uses Large Margin 
Nearest Neighbor metric-learning. The jupyter notebookk DSR_analysisexample_superdonor.ipynb in this directory walks through
descriptive analysis of the data set, data cleaning, and development of the detection algorithm and testing. 

Dependencies: Numpy, Pandas, metric-learn, sklearn, psycopg2, PostgreSQL 9.5

Nathan Vierling-Claassen, Ph.D. 2016
