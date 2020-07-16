# DataProject
An Application of generating tags for market attitudes and predictions




download zip files from 
target_web='https://www.sec.gov/dera/data/financial-statement-data-sets.html'
and store all financial text data into sqlite3

find all the words related to 'finance' using machine learning algorithm


(at most 100 words)

The user can choose how many words at most to find, the algorithm will generate the optimal study rate 
  and output the 'finance' related words

(study rate refers to how many words to be added in each iteration)


Download_zip.py has already realized hierarchical clustering without using any python packages


The test pdfs files are from:  https://www.txtgroup.com/investors/financial-reports/


Command line:
  cd /Users/gumenghan/Desktop/Spyder programs/try/Data_Projects
  
  python pdfTxt.py xxxx.pdf xxxx.txt
  
  python final.py xxxx.txt
  
  currently at most use 1 zip from target_web due to CPU (With GPU, algorithms support as many pdfs as possible)
  use the top 1000 words that occurs the most frequently
