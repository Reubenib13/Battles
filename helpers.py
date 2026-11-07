from flask import redirect, render_template, request, session
from functools import wraps
import requests
from bs4 import BeautifulSoup
import re

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def error(msg, code=400):
    def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    
    return render_template("error.html", top=code, bottom=escape(msg)), code

        
def lookup(url):
    def escape(string):
        if string == '' or string is None:
            return None
        
        string = string.replace('(', '')
        string = string.replace(')', '')
        string = string.replace('\n', '')
        new_string = ''
        if '[' in string and ']' in string:
            flag = False
            for i in string:
                if i == '[':
                    flag = True
                elif i == ']':
                    flag = False
                elif not flag:
                    new_string += i
        else:
            new_string = string

        year = re.compile("\d\d\d\d")
        lst = [*new_string]
        while re.findall(year, new_string):
            start = re.search(year, new_string).start()
            end = re.search(year, new_string).end()
            del lst[start:end]
            lst.insert(start, "####")
            new_string = ''.join(lst)
            lst = [*new_string]

        return new_string

    info = {"name": None,
            "location": None,
            "result": None,
            "belligerents": None,
            "strength": None,
            "casulties": None
            }

    html = requests.get(url).text

    soup = BeautifulSoup(html, "html5lib")
    table = soup.find("table", {"class" : "infobox vevent"})
    if table:
        locationData = []

        data = table.find_all("tr")
        previous = None
        for i in data:
            if "class=\"summary\"" in str(i):
                info["name"] = escape(i.string)

            if i.find("table"):
                for j in i.find_all("tr"):
                    if j.find("div", {"class": "location"}):
                        if j.find("ul"):
                            a = [escape(k.string) for k in j.find_all("a")]
                            locationData += a
                        else:
                            for k in j.find("div", {"class": "location"}):
                                locationData.append(k.string) if k.string != ", " else None

                    try:
                        coordinates = (j.find("span", {"class": "latitude"}).string, table.find("span", {"class": "longitude"}).string)
                        locationData.append(coordinates)
                    except AttributeError:
                        pass

                    if j.find("td", {"class": "status"}):
                        if j.find("ul"):
                            results = []
                            for k in j.find_all("li"):
                                tmp = []
                                for m in k.find_all(text=True):
                                    tmp.append(escape(m.string))
                                tmp = ''.join(tmp)
                                results.append(tmp)
                                # if k.string:
                                #     results.append(escape(k.string))
                                # elif k.find("a").string:
                                #     results.append(escape(k.find("a").string))
                            # results = results[2:]
                            while "" in results: results.remove("")
                            info["result"] = results #''.join(results).split(".")
                        else:
                            info["result"] = [escape(j.find("td", {"class": "status"}).text)]
            try:
                if previous.find("th").string == "Belligerents":
                    left, right = i.find_all("td")[0], i.find_all("td")[1]
                    belligerents_left = []
                    for i in left.find_all(["a", "p"]):
                        if i.text is not None:
                            if not i.next_sibling is None:
                                if i.next_sibling.name is None:
                                    belligerents_left.append(escape(i.text + i.next_sibling.text))
                                else:
                                    belligerents_left.append(escape(i.text))
                            else:
                                belligerents_left.append(escape(i.text))

                    belligerents_right = []
                    for i in right.find_all(["a", "p"]):
                        if i.text is not None:
                            if not i.next_sibling is None:
                                if i.next_sibling.name is None:
                                    belligerents_right.append(escape(i.text + i.next_sibling.text))
                                else:
                                    belligerents_right.append(escape(i.text))
                            else:
                                belligerents_right.append(escape(i.text))
                    # tmp = []
                    # for i in belligerents_left:
                    #     if (not i is None) and (not i == ''):
                    #         tmp.append(i)
                    # belligerents_left = tmp[:]
                    belligerents_left = [i for i in belligerents_left if (not i is None) and (not i == '') and (not i == ' ')]
                    belligerents_right = [i for i in belligerents_right if (not i is None) and (not i == '') and (not i == ' ')]
                    info["belligerents"] = (belligerents_left, belligerents_right)
            except AttributeError:
                pass
            
            if not info["belligerents"] is None:
                if len(info["belligerents"][0]) == 1 and len(info["belligerents"][1]) == 1:
                    try:
                        if previous.find("th").string == "Strength" and i.find_all("ul") is None:
                            info["strength"] = (escape(i.find_all("td")[0].text), escape(i.find_all("td")[1].text))
                    except AttributeError:
                        pass

                    try:
                        if previous.find("th").string == "Casualties and losses" and i.find_all("ul") is None:
                            info["casulties"] = (escape(i.find_all("td")[0].text), escape(i.find_all("td")[1].text))
                    except AttributeError:
                        pass

            previous = i
        info["location"] = locationData

        return info
    else:
        return None
    


    