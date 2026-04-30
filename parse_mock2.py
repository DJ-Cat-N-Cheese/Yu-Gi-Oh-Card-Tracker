from bs4 import BeautifulSoup
import re

html_text = """
<!DOCTYPE html>
<html>
<head><title>Crystal God Tistina</title></head>
<body>
    <div class="labeled">
        <dt>Rarity</dt>
        <dd>
            <span class="icon" title="Quarter Century Secret Rare"></span>
        </dd>
    </div>
</body>
</html>
"""

soup = BeautifulSoup(html_text, 'html.parser')
dt_els = soup.select('dl.labeled dt')
print("Found dts:", len(dt_els))
