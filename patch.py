with open("src/ui/components/filter_pane.py", "r") as f:
    content = f.read()

import re

# Find the common_rarities definition and usage, and replace it
pattern = r"""            # Rarity
            common_rarities = \[
                "Common", "Rare", "Super Rare", "Ultra Rare", "Secret Rare",
                "Ghost Rare", "Ultimate Rare", "Starlight Rare", "Collector's Rare"
            \]
            ui.select\(common_rarities, label='Rarity', with_input=True, clearable=True,"""

replacement = r"""            # Rarity
            ui.select(RARITY_RANKING, label='Rarity', with_input=True, clearable=True,"""

content = re.sub(pattern, replacement, content)

with open("src/ui/components/filter_pane.py", "w") as f:
    f.write(content)

print("Patch applied successfully.")
