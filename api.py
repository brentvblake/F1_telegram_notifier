import requests
import bs4
import asyncio
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

site = 'https://www.crash.net'
baseLink = 'https://www.crash.net/f1/results'
lastArticle = ''
output_image_path = "f1_table.png"

async def getLastArticle():
    # clearfix views-row views-row-1 views-row-odd views-row-first
    basePage = requests.get(baseLink)
    baseSoup = bs4.BeautifulSoup(basePage.text, 'html.parser')
    articleSoup = baseSoup.find("div", class_='clearfix views-row views-row-1 views-row-odd views-row-first')
    articleLink = articleSoup.find('a')['href']
    return site + articleLink

#
async def extractTable(link):
    page = requests.get(link)
    soup = bs4.BeautifulSoup(page.text, 'html.parser')
    table = soup.find('table', class_='crash-report')
    tableBody = table.find('tbody')
    print(tableBody)
    return tableBody

def visualize_table(table):
    rows = table.find_all('tr')
    header_row = rows[0]
    data_rows = rows[1:]

    header_cells = header_row.find_all(['th', 'td'])
    header_texts = [cell.get_text(strip=True) for cell in header_cells]

    data = []
    for row in data_rows:
        cells = row.find_all(['th', 'td'])
        row_data = [cell.get_text(strip=True) for cell in cells]
        data.append(row_data)

    # Ensure header_texts and data have the same number of elements
    while len(header_texts) < len(data[0]):
        header_texts.append("")  # Add empty cells to match data rows

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=data, colLabels=header_texts, loc='center')
    the_table.auto_set_font_size(True)  # Disable automatic font resizing
    the_table.set_fontsize(12)  # Set the font size
    the_table.scale(1.2, 1.2)  # Scale the table to increase the cell sizes

    plt.savefig(output_image_path)

def truncate_text(text, max_length):
    if len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text

lastArticle = asyncio.run(getLastArticle())

table_body = asyncio.run(extractTable(lastArticle))

# Create an image
img_width = 800
img_height = 600
img = Image.new("RGB", (img_width, img_height), "white")
draw = ImageDraw.Draw(img)

# Prepare and draw table content
font = ImageFont.load_default()
row_height = 20
y = 10

for row in table_body.find_all("tr"):
    x = 10
    for i, cell in enumerate(row.find_all(["th", "td"])):
        if i == 0:
            cell_text = cell.get_text()  # Don't truncate the first cell
        else:
            cell_text = truncate_text(cell.get_text(), 20)
        draw.text((x, y), cell_text, font=font, fill="black")
        x += 150  # Adjust cell width
    y += row_height

img.save(output_image_path)
