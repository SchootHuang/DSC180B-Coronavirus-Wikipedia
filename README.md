# DSC180B Final Project: Investigating the Biaseness of Wikipedia and the Media in the Scope of COVID-19
Which is the most unbiased source of COVID-19 information: A analysis of 20 News agency and Wikipedia

##Overview
COVID-19 has gained increasing attention since its breakout in China in the early 2020. At this stage where full understanding of the virus is still developing, information related to COVID-19 in the media coverage may sometimes be misleading. There is diverging, even self-conflicting, news coverage from newspapers. It is becoming increasingly difficult to find out to figure out which statements being thrown at us are facts that we should be listening to or simple just rumors we should ignore. Wikipedia viewing and editing data is a record of people’s information-seeking and engagement behavior that could be used as an unbiased indicator of public opinion. It might reveal what people actually learn from the media coverage and how people react to the COVID-19. On the other hand, it could be seen as a platform where “random people” get to contribute and therefore making it a biased and untrustworthy source. We defined the trustworthiness of a source through a topic distribution matrix. Since we can divide the broad topic of COVID-19 into sub topics such as origins of the virus, symptoms, economic implications, how it spreads etc, we will measure how trustworthy a source is by how many of these subtopics it covers. Specifically, we wanted to answer the question, “How biased are certain popular news outlets in how they cover the effects and the spread of COVID-19?"

## Usage
```
launch-scipy-ml.sh
git clone git@github.com:SchootHuang/DSC180B-Coronavirus-Wikipedia.git
cd DSC180B
python run.py test-project
```

## Sources

Link to our Project Website: https://schoothuang.github.io/DSC180B-Coronavirus-Wikipedia/ 

Wiki-Media Dumps dataset Used: https://dumps.wikimedia.org/enwiki/20200101/

Wiki-Monitor Lightdump information: http://wwm.phy.bme.hu/

All the News 2.0 dataset: https://components.one/datasets/all-the-news-2-news-articles-dataset/ 
