import json
import math
import datetime

# gen_frames.py
# Generates a svg for every day in the provided final observation json

# ======== CONSTANTS ========= #
circle = '<circle style=\"{}\" id=\"{}\" cx=\"{}\" cy=\"{}\" r=\"{}\" />\n'
MAP_WIDTH = 1000.0
MAP_HEIGHT = 902.0
with open('starter.svg', 'r') as fp:  # top of the svg file before inserted circles
    starter = fp.read()
with open('ender.svg', 'r') as fp:  # bottom of svg files after inserted circles
    ender = fp.read()


# ======== FUNCTIONS ========= #
def make_date(date):
    """
For a date string, returns a datetime object
    :param date: YEAR-MM-DD
    :return: datetime
    """
    date = date.split('-')
    return datetime.date(int(date[0]), int(date[1]), int(date[2]))


def daterange(start_date, end_date):
    """
Used to iterate over date range.
Credit: Ber https://stackoverflow.com/a/1060330
    :param start_date: date object, ex. date(2013, 1, 1)
    :param end_date: date object
    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


def addText(text):
    """
Updates the textbox in the corner of the svg. Ugly but works for current situation
    :param text: text needed to be updated
    :return:
    """
    return '<text xml:space="preserve" style="font-style:normal;font-weight:normal;font-size:9.75123596px;line-height:1.25;' \
           'font-family:sans-serif;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;stroke-' \
           'width:0.02437809" x="314.22992" y="323.82281" id="text4456"><tspan sodipodi:role="line" id="tspan4454" x="314.22992" ' \
           'y="323.82281" style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:' \
           '5.85074186px;font-family:Arial;-inkscape-font-specification:Arial;stroke-width:0.02437809">' \
           + text + '</tspan></text>'


def makeSVG(obvs_list, current_date, save_folder, day_count=0):
    """
Generate an svg based on the list of observations provided
    :param days:
    :param obvs_list: list of observations
    :return:
    """
    print(current_date)
    obv_date = make_date(current_date)
    next_date = obv_date + datetime.timedelta(days=day_count)
    filename = str(next_date)  # ex. 5 -> '005'

    with open(save_folder + filename + '.svg', 'w+') as sf:
        sf.write(starter)
        for obv in obvs_list:
            lat = obv['location'][0]
            lon = obv['location'][1]
            # print(obv['id'], obv['location'][1], obv['location'][1])
            color = str(obv['color'][:3])
            r = 2
            obv_id = obv['id']
            if obv['color'][3] > .1:
                obv['color'][3] -= 0.1
            else:
                obvs_list.remove(obv)
                continue

            opacity = str(obv['color'][3])
            style = "fill:rgb(" + color[1:-1] + ");fill-opacity:1;stroke:rgb(" + color[
                                                                                 1:-1] + ");stroke-width:0.71433073;stroke-linecap:square;stroke-linejoin:miter;" \
                                                                                         "stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1;opacity:" + opacity
            cx = (lon + 180) * (MAP_WIDTH / 360)
            cy = (MAP_HEIGHT / 2) - (
                    MAP_WIDTH * math.log(math.tan((math.pi / 4) + ((lat * math.pi / 180) / 2))) / (2 * math.pi))
            sf.write(circle.format(style, str(obv_id), str(cx), str(cy), str(r)))
        sf.write(addText(str(next_date)))
        sf.write(ender)
        return obvs_list


def date_diff(start, end):
    """
Returns the number of days between the start and end date
    :param startDate: date object
    :param endDate: date object
    :return: int
    """
    start_date = make_date(start)
    end_date = make_date(end)
    return sum(1 for _ in daterange(start_date, end_date))


def make_frames(observations, save_folder):
    observations.reverse()  # into chronological order
    all_obvs = []
    today_obvs = []
    today = observations[0]['observed_on']

    for obv in observations:
        obv['color'].append(1.1)  # add extra value for opacity
        print(obv['id'])
        if obv['observed_on'] != today:
            change_count = date_diff(today, obv['observed_on'])
            # print(change_count)
            all_obvs.extend(today_obvs)
            all_obvs = makeSVG(all_obvs, today, save_folder)
            if change_count > 1:
                for i in range(1, change_count):
                    # print(all_obvs)
                    all_obvs = makeSVG(all_obvs, today, save_folder, i)
            today_obvs = []
            today_obvs.append(obv)
            today = obv['observed_on']
        else:
            today_obvs.append(obv)

    all_obvs.extend(today_obvs)
    all_obvs = makeSVG(all_obvs, today, save_folder)


if (__name__ == '__main__'):
    SAVE_FOLDER = 'final2017frames/'  # where to save the generated frames
    GEN_FINAL = '../2017/2017final.json'  # final observation file, generated by <LeafColors>.observation_colors()
    with open(GEN_FINAL, 'r') as fp:
        obvs = json.load(fp)

    make_frames(obvs, SAVE_FOLDER)
