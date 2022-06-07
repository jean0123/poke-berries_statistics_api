from flask import Flask, render_template, jsonify
from flask_restful import Resource, Api
import requests
import statistics
from matplotlib import pyplot as plt

app = Flask(__name__)
app.config.from_pyfile('config.py')
api = Api(app)

@app.route('/')
def index():
    pagetitle = "Api Berries"
    return render_template("berry_stats.html", mytitle=pagetitle)
class Berries(Resource):
    '''
    Class to return the response of the api
    '''
    def get(self):
        berries_list = []
        url = 'https://pokeapi.co/api/v2/berry/'
        try:
            berries_list = get_poke_berries(url, berries_list)
        except Exception as e:
            raise e
        else:
            response = get_estadistic(berries_list)
        finally:
            return jsonify(response)

def get_poke_berries(url, berries_list):
    '''
    Get all berries from the API
    '''
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
    for item in data['results']:
        berries_list.append({ item['name'] : requests.get(item.get('url')).json().get('growth_time') })
    if data['next'] != None:
        return get_poke_berries(str(data['next']), berries_list)
    else:
        return berries_list

def get_estadistic(berries_list):
    '''
    Get the statistics of the berries
    '''
    berries_names = []
    berries_values = []
    for berry in berries_list:
        for key, value in berry.items():
            berries_names.append(key)
            berries_values.append(value)
    # Get de minimum of the berries
    minimum = min(berries_values)
    # Get the median of the berries
    median = statistics.median(berries_values).__round__(2)
    # Get the maximum of the berries
    maximum = max(berries_values)
    # Get the variance of the berries
    variance = statistics.variance(berries_values).__round__(2)
    # Get the mean of the berries
    mean = statistics.mean(berries_values).__round__(2)
    # Get the frequency for each berry
    frequency = {}
    for berry in berries_values:
        frequency[berry] = frequency.get(berry, 0) + 1
    # Get the histogram of the berries
    histogram = berries_values.copy()
    histogram.sort()
    plt.hist(histogram, bins=len(histogram), range=(0, maximum+5), color='#0504aa', alpha=0.7, rwidth=0.85)
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('Frecuencia')
    plt.ylabel('Número de Berries')
    plt.title('Histograma de Berries')
    plt.savefig('static/images/histogram.png')
    plt.close()
    # return the statistics
    return {
        'berries_names': berries_names,
        'min_growth_time': minimum,
        'median_growth_time': median,
        'max_growth_time': maximum,
        'variance_growth_time': variance,
        'mean_growth_time': mean,
        'frequency_growth_time': frequency
    }

api.add_resource(Berries, '/allBerryStats', methods=['GET'])

if __name__ == '__main__':
    app.run()