import logging
from nicegui import ui

logger = logging.getLogger(__name__)

class DeckDragDropHandler:
    def __init__(self, page):
        """
        Initialize the handler with a reference to the DeckBuilderPage.
        :param page: The DeckBuilderPage instance.
        """
        self.page = page

    async def handle_deck_change(self, e):
        """
        Handles the custom 'deck_change' event from SortableJS.
        Manages deck state updates and performs surgical DOM updates to prevent flashing.
        """
        args = e.args.get('detail', {})
        to_zone = args.get('to_zone')
        to_ids_str = args.get('to_ids')
        from_zone = args.get('from_zone')
        from_ids_str = args.get('from_ids')

        # Convert strings to ints
        try:
            to_ids = [int(x) for x in to_ids_str] if to_ids_str else []
            from_ids = [int(x) for x in from_ids_str] if from_ids_str else []
        except ValueError:
            return

        # Check for no-op moves to prevent unnecessary saves
        new_index = args.get('new_index')
        old_index = args.get('old_index')

        # 1. Gallery to Gallery (micro-drag in gallery)
        if from_zone == 'gallery' and to_zone == 'gallery':
            return

        # 2. Same zone, same index (drop in place)
        if from_zone == to_zone and new_index == old_index:
            return

        deck = self.page.state['current_deck']
        if not deck: return

        # Validate zones
        valid_zones = ['main', 'extra', 'side']

        # Update 'to' zone
        if to_zone in valid_zones:
            setattr(deck, to_zone, to_ids)

        # Update 'from' zone if it's a valid deck zone and different from 'to'
        if from_zone in valid_zones and from_zone != to_zone:
             setattr(deck, from_zone, from_ids)

        await self.page.save_current_deck()

        # Refresh UI
        if from_zone == 'gallery':
             # Surgically add the new card component to avoid full refresh/flashing
             await self._perform_surgical_update(to_zone, to_ids, new_index)
        else:
             # Intra-deck moves logic remains same (skip refresh)
             pass

        self.page.update_zone_headers()

    async def _perform_surgical_update(self, to_zone, to_ids, new_index):
        """
        Surgically adds a new card component to the deck grid to avoid full refresh/flashing.
        Calculates the correct usage/owned state for the specific card instance.
        """
        try:
            card_id = to_ids[new_index]

            owned_total = 0
            if self.page.state['reference_collection']:
                for c in self.page.state['reference_collection'].cards:
                    if c.card_id == card_id:
                        owned_total = c.total_quantity
                        break

            # Calculate usage count up to this point (for opacity logic)
            usage_count = to_ids[:new_index].count(card_id)

            if to_zone not in self.page.deck_grids:
                logger.error(f"Target zone {to_zone} grid not found")
                self.page.refresh_zone(to_zone)
                return

            grid = self.page.deck_grids[to_zone]
            with grid:
                new_card = self.page._render_deck_card(
                    card_id,
                    to_zone,
                    usage_counter={card_id: usage_count},
                    owned_map={card_id: owned_total}
                )

            if new_card:
                new_card.move(grid, index=new_index)

                # Remove the SortableJS client-side "ghost" element.
                # Since we stripped IDs in onClone, the ghost likely has no ID or just data-id.
                # We remove elements with matching data-id but NO ID attribute to avoid removing the new real card.
                await ui.run_javascript(f'''
                var container = document.getElementById("deck-{to_zone}");
                if (container) {{
                    Array.from(container.children).forEach(c => {{
                        if (c.getAttribute("data-id") == "{card_id}" && !c.getAttribute("id")) {{
                            c.remove();
                        }}
                    }});
                }}
                ''')
        except Exception as ex:
            logger.error(f"Error in surgical update: {ex}")
            self.page.refresh_zone(to_zone)
