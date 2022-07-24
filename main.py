import requests
from bs4 import BeautifulSoup, element
import asyncio

# table count size
WIKI_TABLE_SIZE = 7
# cell num 0 -> animal name
WIKI_TABLE_ANIMAL_NAME = 0
# cell num 5 -> animal name
WIKI_TABLE_ANIMAL_ADJECTIVE = 5


async def connect_to_wikitables():
    # Create a URL
    url = 'https://en.wikipedia.org/wiki/List_of_animal_names'

    # Create object page
    page = requests.get(url).text

    # Obtain page's information
    doc = BeautifulSoup(page, 'html.parser')

    # isolate tables from html by HTML class wikitable
    return doc.find_all('table', class_="wikitable")


async def iterate_over_tables(tables : element.ResultSet):
    animals = {}

    # loop through the tables
    for table in tables:
        body = table.tbody
        trs = body.contents
        # loop through the rows of the tables except the headers 
        for tr in trs[1:]:
            # bs4 return Tag / NavigableString object
            # incase of an empty NavigableString continue
            if isinstance(tr, element.NavigableString):
                continue
            else:

                ### we got a tag with the row data
                ### tr.contents return WIKI_TABLE_SIZE*2 -> foreach cell add '\n'
                ### at the second wiki table there are rows which contains only 1 character
                ### so we want to avoid those rows and only use the actual table

                # remove '\n' from list 
                row = list(filter(lambda x: x != "\n", tr.contents))
                # only incase valid row with WIKI_TABLE_SIZE cells
                if len(row) == WIKI_TABLE_SIZE:
                    # get animal name
                    name = row[WIKI_TABLE_ANIMAL_NAME].string
                    if name == None:
                        name = row[WIKI_TABLE_ANIMAL_NAME].contents[0].string
                    # get animal adjective
                    adjectives = row[WIKI_TABLE_ANIMAL_ADJECTIVE]
                    
                    # incase there are multiple adjectives
                    if '<br/>' in str(adjectives):
                        # list of adjectives 
                        adjectives = str(adjectives).split('<br/>')
                         
                        # remove <td> from the first element
                        adjectives[0] = adjectives[0].strip('<td>')
                        # remove </td> from the first element
                        adjectives[-1] = adjectives[-1].strip('</td>')

                        # remove <sup> tag from the adjectives
                        if '<sup' in adjectives[0]:
                            adjectives[0] = adjectives[0].split('<sup')[0]
                        if '<sup' in adjectives[-1]:
                            adjectives[-1] = adjectives[-1].split('<sup')[0]
                    else:
                        adjectives = row[WIKI_TABLE_ANIMAL_ADJECTIVE].string
                    # add new adjectives to animal
                    animals[name] = adjectives      
    return animals


def export_animals_to_html(animals : dict):
    # reading template file i created
    with open("template.html", "r") as f:
        doc = BeautifulSoup(f, "html.parser")
    
    # get the body of the table
    tbody = doc.find('tbody')
    
    for name,adjective in animals.items():
        # create new tr per item at animals
        new_row = doc.new_tag('tr')
        new_cell_name = doc.new_tag('td')
        new_cell_adjective = doc.new_tag('td')

        # set the data to the new tags
        new_cell_name.string , new_cell_adjective.string = name ,str(adjective)

        # append to row
        new_row.append(new_cell_name)
        new_row.append(new_cell_adjective)

        # append to table
        tbody.append(new_row)

    # create new file with data
    with open ("index.html", "w") as file:
        file.write(str(doc.prettify()))
    

async def main():
    tables = await connect_to_wikitables()
    animals = await iterate_over_tables(tables)
    export_animals_to_html(animals)


asyncio.run(main())
