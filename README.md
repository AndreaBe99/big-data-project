# big-data-project

Project of Big Data Computing, Sapienza University of Rome Department of Computer Science

## Data Acquisition: Spotify
Today Spotify is one of the most popular app for listening music (online & offline).
It counts around 1 billion of installations (reached in 2021 on Play Store).
In order to create our dataset we used the Spotify Dev API and a Python Program that makes request to the Spotify Server.

For data acquisition first we look for a dataset that has the genre associated with the song.
- After several searches we have not found an adequate dataset.

The Reason:
- Spotify does not associate the genre directly with the track but exclusively with the artists;
- An artist in most cases has multiple genres.

Therefore we decided to create a dataset from scratch using the Spotify Web API.

The Spotify Web API provides queries to get:
- the list of all genres classified by Spotify;
- a list of up to 100 recommended songs given a specific genre;
- the audio characteristics of a track given its Spotify ID;
- the playlists of the user given his Spotify ID.

We used these to create the two datasets.

## Description of the Dataset
Before the pre processing operations our dataset is composed by:
- around 80k rows;
- each row is described by 25 columns (features).

The preprocessing operations we did to the dataset led these numbers to grow significantly, reaching 100k rows and each row is described by 47 features.

## Supervised Learning 

### Classification

In our project we decided to test the following models:
- Decision Tree Classifier.
- Logistic Regression.
- Random Forest Classifier.
- Multi Layer Perceptron Network.

We have decided to separate the Training from the Pipeline for time and memory reasons in order to run each model independently

### K-Means Clustering

We decided to train k-means clustering algorithm by setting the number of clusters (k) equals to 12, that represents the “big-genres”.

We used the following parameters:
- distance measure: cosine similarity
- metric measure: silhouette

To evaluate k-means we print the silhouette score in order to find a local maxima.


## Recommender System
The idea is to recommend songs to the user, to be included in their own playlist.

Problem:
- Spotify Web Api does not provide data on other users
- It is possible to obtain a user's playlist only if they are public and if you know their Spotify ID in advance.

For these reasons we have chosen Content-based filtering to develop this system.

The algorithm can be divided into two steps:

1. Creating the summary vector;
2. Find the similarity and suggest the songs.
