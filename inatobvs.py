import urllib.request
import json


class INatObvs:
    def __init__(self, url):
        if not url.find('per_page'):
            raise Exception('GET request url needs to have a per_page parameter')
        if not url.find('&page='):
            raise Exception('GET request url needs to have a page parameter')
        self.url = url
        self.data = self.get_data()

    @staticmethod
    def _change_page(link, p) -> str:
        """
        Updates the page number of the link provided
        :param link: url containing '&page='
        :param p: integer page number
        :return: updated url
        """
        if p < 1:
            raise Exception('Page number must be greater than 0')

        pageIndex = link.find('&page=')
        splitLink = link[pageIndex + 1:].split('&', 1)
        newURL = link[: pageIndex] + '&page=' + str(p) + '&' + splitLink[1]
        return newURL

    @staticmethod
    def _ceildiv(a: int, b: int) -> int:
        """
        Takes the ceil of a / b, without having to import math. From https://stackoverflow.com/a/17511341
        """
        return -(-a // b)

    def _per_page(self):
        """
        Finds the number per page of the URL
        """
        pp_index = self.url.find('&per_page=') + len('&per_page=')
        next_param = self.url[pp_index:].find('&')

        pp = self.url[pp_index: pp_index + next_param]
        return int(pp)

    def get_data(self):
        """
        Makes the GET request and returns a subset of the data from each observation in a list
        :return:
        """
        print("Waiting to get number of total results...")
        response = urllib.request.urlopen(self.url).read()
        response = json.loads(response.decode('utf-8'))
        total_results = int(response['total_results'])
        pages = self._ceildiv(total_results, self._per_page())  # number of pages to cover all the results
        print("Total results:", total_results)
        print("Number of API calls needed:", pages)

        all_results = []
        for i in range(1, pages + 1):
            print("Called", i)
            response = urllib.request.urlopen(self._change_page(self.url, i)).read()
            response = json.loads(response.decode('utf-8'))
            print("Finished", i)

            for j, obs in enumerate(response['results']):
                response['results'][j] = {k: v for k, v in obs.items() if k in (
                    'observed_on', 'observed_on_details',
                    'created_at', 'created_at_details',
                    'geojson',
                    'place_ids', 'uri', 'user', 'location', 'place_guess', 'photos', 'id')}
            all_results.extend(response['results'])
        return all_results

    def download(self, folder: str, size: str):
        """
        Downloads all the images in the data to the folder specified.
        :param size: size of image. can be 'square', 'small', 'medium', or 'large'
        :param folder: 'foldername/'
        """
        for obs in self.data:
            for picture in obs['photos']:
                picUrl = picture['url'].replace('square', size)
                urllib.request.urlretrieve(picUrl, folder + str(picture['id']) + '.jpg')

if __name__ == '__main__':
    URL = 'https://api.inaturalist.org/v1/observations?taxon_id=48098&d1=2015-01-01&d2=2015-12-31&quality_grade=research&page=1&per_page=200&order=desc&order_by=observed_on'
    SAVE_FILE = 'data.json'  # file to save data to

    myDown = INatObvs(URL)
    with open(SAVE_FILE, 'w+') as fp:
        json.dump(myDown.data, fp, sort_keys=True, indent=4)
    myDown.download('2019/', 'medium')
