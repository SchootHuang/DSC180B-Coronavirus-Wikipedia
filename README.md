# Overview

COVID-19 has gained increasing attention since its breakout in China in the early 2020. At this stage where full understanding of the virus is still developing, information about COVID-19 may sometimes be misleading as there is diverging, even self-conflicting, news coverage from newspapers to Internet. In our study, we are investigating which one is the most trustworthy and unbiased information source regarding to COVID-19, whether it is a traditional newspaper, or it is Wikipedia.

# Dataset Overlook
There are three main datasets for our study.

## COVID-19 News Articles Dataset
Since we focused specifically on COVID-19, we restricted the temporal scope of the data to news since the beginning of the year 2020, which resulted in 230,000+ news coverage. And we generated our own COVID-19 News Dataset by filtering out the COVID-19 related articles. We applied filtering keywords such as ‘COVID’, ‘virus’, ‘stay-at-home’ on the headlines of each article. This resulted in a final dataset with approximately 45,000+ articles.

Currently, there are 20 publication sources in our COVID-19 news articles dataset:
 
 [1] "Business Insider"   "Buzzfeed News"      "CNBC"               "CNN"               
 [5] "Economist"          "Hyperallergic"      "Mashable"           "New Republic"      
 [9] "Politico"           "Refinery 29"        "Reuters"            "TechCrunch"        
[13] "The Hill"           "The New York Times" "The Verge"          "TMZ"               
[17] "Vice"               "Vox"                "Washington Post"    "Wired"   

The bar plot below shows the number of articles per day, which suggests that the attention shed on COVID-19 was accelerating since March. Also, the data shows a periodic pattern since newspapers publish less articles during the weekend. There is a decreasing trend after March 21, but this is more likely because more up to date news were parsed from the Internet and were therefore not included in the dataset.

![Image](/website-figures/NewsArticleDatatset.png)

##  Wikipedia Page Views Dataset
The data ingestion of the Wikipedia articles lead to the creation of thousands of csv files with the article title and pageviews for each of the articles as well as the domain code which is the language the article is written in. We narrowed down the scope of these articles by selecting the rows with titles that contain specific key words such as “covid”, “coronavirus”, “pandemic” etc. Using this much smaller subset of the data, we created bar charts to visualize the articles with the highest and lowest page views. We also created a histogram showing the distribution of the pages views for all the articles in the dataset.

![Image](/website-figures/WikipediaDataset.png)

##  Wikipedia Editing History Dataset
We are currently in the process of collecting all the edit histories for all the articles in the page views dataset. One we have the edit histories, we will perform the same topic modelling we performed on the News Articles Dataset by running the same script. This will allow us to produce sankey diagrams to visually represent the edit history of these Wikipedia articles. This will also allow us to compare the Wikipedia and the Media sources and evaluate the less biased source as well as draw key conclusions from our investigation.

# Results
In our experiments, we run STM on the combination of both wikipedia editing history as well as the news article dataset. We first plot the overall topic distribution(Shown below) of the combined corpus and make case studies for more fine-grained analysis. Then compare the topic distribution of each source to the overall topic distribution of the combined corpus.

![Image](/website-figures/STMplot.png)
![Image](/website-figures/COVID19-topic-distribution.png)

Here we define {T} as the set of topic distribution for a given corpus C, and  Ti is the topic distribution with topic i, which is defined by the number of documents that have the dominant topic i per day. This concept would work smoothly with our COVID-19 News article dataset. For the wikipedia part, we would take the number of page views as the analogue of the number of articles for our investigation. From our perspective, the topic distribution of each source is a simple yet efficient approach in investigating the variation of content.


##  Topic Distribution of Specific Topics
 ![Image](/website-figures/EventAnalysis.png)   


We then investigate each topic to see whether the given topic correctly reflects the ground truth regarding to COVID-19. Firstly, topic 11, given keywords of 'china','wuhan','outbreak','virus','case', highlighted in purple in Figure b, indeed correlate with the breakout of COVID-19 in China, as it surges on Jan 2020 and then decreases as the virus were gradually taken into control in China. Topic 17 on other hand, given keywords of 'market','stock','index','investor','dollar', highlighted in orange in Figure b, correlates with the attention on global economy as people are concerning on the virus’s effect on the economy and the resulting Market slip.


##  Topic Distribution of Specific Information Outlet
![Image](/website-figures/PlotBySource.png)

The two plots above are the topic distribution corresponding to  New York Times and Washington Post. Respectively. As one may observe, the Reuters is with the topic distribution that is the most similar to the combined corpus, whereas the topic distribution from New York TImes is more evenly distributed. This might be due to the overall corpus being made up of a large amount of Reuter’s coverage. In the final report, we will address this issue through random sampling strategies.

## Trustworthiness Measurement
![Image](/website-figures/TrustWorthinessResult.png)

# Conclusion
