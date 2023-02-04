import os
import requests 
import pandas as pd 
import time
import itertools
import networkx as nx

# Use the Twitter API to download our tweets

def create_url(query, start_time, end_time, max_results, expansions, tweet_fields, user_fields, place_fields, endpoint, sort_order='recency'):
    
    search_url = endpoint #Change to the endpoint you want to collect data from

    #change params based on the endpoint you are using
    #also can request different fields, e.g ids of users ... 
    query_params = {'query': query,
                    'end_time': end_time,
                    'start_time': start_time,
                    'max_results': max_results,
                    'sort_order': sort_order,
                    'expansions': expansions,
                    'tweet.fields': tweet_fields,
                    'user.fields': user_fields,
                    'place.fields': place_fields}

    return (search_url, query_params)

def connect_to_endpoint(url, headers, params, next_token = None):
    #only change the default value of next_token if it is a real value returned in the response
    if next_token is not None and next_token != '':
        params['next_token'] = next_token
    
    #create a "GET" request to the specified url, add headers and parameters
    response = requests.request("GET", url, headers = headers, params = params)
    if response.status_code != 200:
        #if something goes wrong, we need to know
        raise Exception(response.status_code, response.text)
    #otherwise, we want the payload of our response, which contains our tweet(s)
    return response.json()

def get_data(query, start_time, end_time, max_results, expansions, tweet_fields, user_fields, place_fields, endpoint, next_token=""):
  
    results = []

    while next_token is not None:
        try:    
            url = create_url(query, start_time, end_time, max_results, expansions, tweet_fields, user_fields, place_fields, endpoint)
            json_response = connect_to_endpoint(url[0], headers, url[1], next_token)
            #if we have results, they will be in the field 'data' of our response
            if "data" in json_response:
                results.extend(json_response["data"])
                print(str(len(json_response["data"])) + " Tweets downloaded in this batch.")
            #the next_token is added to the field 'meta' of our response
            if "meta" in json_response:
                if "next_token" in json_response["meta"].keys():
                    next_token = json_response["meta"]["next_token"]          
                else:
                    next_token = None
            else:
                next_token = None


            #to control the rate limit we need to slow down our download
            time.sleep(20)

        except Exception as e:
            print("Error occured", e)
            print("Next token value", next_token)
            return(results, next_token)

    print("Done")

    return results

def create_url_counts(keyword, start_date, end_date, endpoint):
    search_url = endpoint
    query_params = {'query': keyword,
                  'start_time': start_date,
                  'end_time': end_date,
    }
    return (search_url, query_params)  


def connect_to_endpoint_counts(url, headers, params, next_token = None):
    #print(next_token)
    if next_token is not None and next_token != '':
         params['next_token'] = next_token
    response = requests.request("GET", url, headers = headers, params = params)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def get_data_counts(keyword, start_time, end_time, next_token, endpoint):
    results = 0
    result_count = {}

    while next_token is not None:
    try:     
        url = create_url_counts(keyword, start_time, end_time, endpoint)
        json_response = connect_to_endpoint_counts(url[0], headers, url[1], next_token) 
        if "data" in json_response:
        for date in json_response["data"]:
            result_count[date["start"]] = date["tweet_count"]      
        if "meta" in json_response:
        if "next_token" in json_response["meta"].keys():
            next_token = json_response["meta"]["next_token"]
        else:
            next_token = None
        if "total_tweet_count" in json_response["meta"].keys():
            results += int(json_response["meta"]["total_tweet_count"])
        else:
            next_token = None
    except Exception as e:
        print("Error occured", e)
        
    return (results, next_token, result_count)