# ReliabilityRadar

**ReliabilityRadar** is a Natural Language Processing (NLP) project that analyzes user-generated content from Reddit and automotive forums to uncover insights into car brand popularity, common mechanical issues, and overall reliability. It uses structured and unstructured data sources to identify trends, extract topics, and rank brands based on real user experiences.

---

## 📊 Project Goals

- Analyze large-scale public discussions related to vehicles.
- Identify frequently mentioned car brands and models.
- Detect recurring issues and common problems.
- Compare sentiment and reliability perceptions between different brands.
- Present ranked lists of issues, brands, and models based on frequency and discussion context.

---

## 🧠 What to Run and When

The project has three main parts, each for a key step in the data workflow. Here’s what to run depending on your goal:

1. **Data Collection (Scraping):**  
   Run the scripts in `src/scraping` to gather or update raw data from Reddit and Car Talk forums. These scripts fetch posts and comments, saving them as JSON files with the latest user content.

2. **Text Processing and Analysis (NLP):**  
   After collecting data, run scripts in `src/nlp` to clean and preprocess text (tokenization, stopword removal, etc.). This folder also has sentiment analysis and topic modeling scripts to find insights about car brands, models, and common problems.

3. **Visualization and Reporting:**  
   Use scripts in `src/visualize` to create charts, word clouds, brand rankings, and other visuals to help interpret and present your analysis results.

**Note:** All outputs and processed data are saved in the `data` folder.

In short:  
- Run **scraping** scripts to get data  
- Run **NLP** scripts to process and analyze text  
- Run **visualize** scripts to make reports and graphs  