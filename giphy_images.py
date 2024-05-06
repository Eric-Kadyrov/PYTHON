import requests

def search_gifs(query):
    api_key = 'YOUR_GIPHY_API_KEY'  # Replace with my actual Giphy API key - in progress 
    url = 'https://api.giphy.com/v1/gifs/search'
    params = {
        'api_key': api_key,
        'q': query,
        'limit': 5,  # Number of results to return
        'offset': 0,
        'rating': 'G',
        'lang': 'en'
    }
    response = requests.get(url, params=params)
    gifs = response.json()
    
    for gif in gifs['data']:
        print(gif['url'])

if __name__ == '__main__':
    query = input("Enter a search word for GIFs: ")
    search_gifs(query)
