import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
data = []
app_res = []
def check_data(name):
  arr = []
  for i in op_data:
    if i['name_in_website'] == name:
      arr.append(i)
  for i in data:
     if i['name_in_website'] == name:
      arr.append(i)
  return None

def get_info(name):
    
    url = "https://app.apollo.io/api/v1/mixed_people/search"

    data = {
        "api_key": "PIm4pmrVCxqBb4J8MjJ06Q",
        "q_person_name": name
    }
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json'
    }
    time.sleep(3)
    response = requests.request("POST", url, headers=headers, json=data)
    print(response.status_code)
    if response.status_code == 200:
        app_res.append((response.json(),name))
        return response.json()

    print(response.status_code, 'res', response.text)
    return None




def process_json_to_csv(name_in_website, df, json_data):
    people_list = json_data.get("people", [])

    data_to_append = []

    for person in people_list:
        # Extracting data using .get() method
        linkedin_url = person.get("linkedin_url")
        name = person.get("name")
        title = person.get("title")
        facebook_url = person.get("facebook_url")
        twitter_url = person.get("twitter_url")
        github_url = person.get("github_url")
        email = person.get("email")
        state = person.get("state")
        city = person.get("city")
        country = person.get("country")
        organization_name = person.get("organization", {}).get("name")
        phone_numbers = person.get("phone_numbers", [])

        # Extracting employment history
        employment_history = person.get("employment_history", [])
        employment_str = "->".join([f"{emp.get('organization_name')}|{emp.get('title')}" for emp in employment_history])

        # Adding data to the list for later concatenation
        data_for = {
             "name_in_website": name_in_website,
            "name": name,
            "linkedin_url": linkedin_url,
            "title": title,
            "facebook_url": facebook_url,
            "twitter_url": twitter_url,
            "github_url": github_url,
            "email": email,
            "state": state,
            "city": city,
            "country": country,
            "organization_name": organization_name,
            "phone_numbers": "|".join([pn.get("raw_number") for pn in phone_numbers]),
            "employment_history": employment_str,
        }
        data.append(data_for)
        data_to_append.append(data_for)

    # Concatenate the new data with the existing DataFrame
    df = pd.concat([df, pd.DataFrame(data_to_append)], ignore_index=True)

    return df

# Sample DataFrame
columns = ["name_in_website", "name", "linkedin_url", "title", "facebook_url", "twitter_url", "github_url",
           "email", "state", "city", "country", "organization_name", "phone_numbers", "employment_history"]
df = pd.DataFrame(columns=columns)

for i in range(1, 14):
    res = requests.get(f'https://venture.angellist.com/capitalx/syndicate?render=lps&page={i}')
    print(res.status_code,res ,i)
    soup = BeautifulSoup(res.json()['html'], 'html.parser')
    for name in soup.find_all('div', {'class': "u-fontSize14 u-fontWeight500 s-vgTop1"}):
        name_in_website = str(name.text).strip()
        res = get_info(name_in_website)
        is_present = check_data(name)
        if is_present:
          df = pd.concat([df, pd.DataFrame(is_present)], ignore_index=True)
          continue 
        if res:
            df = process_json_to_csv(name_in_website, df, res)
        else:
            # add name_in_website with blank
            df = process_json_to_csv(name_in_website, df, {"people": []})

# Save DataFrame to CSV
df.to_csv("sample_output.csv", index=False)
