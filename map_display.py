from pathlib import Path
import arcade
# --- TES IMPORTS DE PARSING ---
from loader import Loader
from parser import MapParser
from models import MapConfigModel
from simulation import Simulation


class MapView(arcade.View):
    def __init__(self, map_file_path: Path) -> None:
        super().__init__()
        self.map_file_path = map_file_path

        # --- REPRODUCTION STRICTE DE LA LOGIQUE DE CHARGEMENT ---
        loader = Loader()
        parser = MapParser()

        # On lit et on valide le fichier sélectionné par le menu
        raw_input = loader.load_file(str(self.map_file_path))
        raw_dict = parser.parse(raw_input)
        valid_map = MapConfigModel(**raw_dict)

        # On instancie ENFIN la simulation avec le bon objet Pydantic !
        self.sim = Simulation(valid_map)
        self.sim.display_status() # Optionnel : pour garder tes prints de débug

        # 1. ANALYSE TOPOGRAPHIQUE (Inchangé)
        x_coords = [zone.x for zone in self.sim.map_graph.zones.values()]
        y_coords = [zone.y for zone in self.sim.map_graph.zones.values()]

        self.min_x = min(x_coords) if x_coords else 0
        self.max_x = max(x_coords) if x_coords else 1
        self.min_y = min(y_coords) if y_coords else 0
        self.max_y = max(y_coords) if y_coords else 1

        map_width_units = self.max_x - self.min_x
        map_height_units = self.max_y - self.min_y

        if map_width_units == 0: map_width_units = 1
        if map_height_units == 0: map_height_units = 1

        # ... Tout le reste de ton code (current_width, icon_list, etc.) reste identique ...

        # --- IMPORTANT : LECTURE DES DIMENSIONS DE LA FENÊTRE ---
        # Comme nous sommes dans une View, la taille est dictée par la fenêtre principale
        current_width = self.window.width
        current_height = self.window.height

        arcade.set_background_color(arcade.color.CELESTE)

        # CHARGEMENT SÉCURISÉ DE L'IMAGE
        try:
            bg_sprite = arcade.Sprite("assets/ocean.jpg")
            bg_sprite.center_x = current_width / 2
            bg_sprite.center_y = current_height / 2
            # On utilise les nouvelles variables current_width/height
            bg_sprite.width = current_width
            bg_sprite.height = current_height

            bg_sprite.alpha = 70

            self.background_list = arcade.SpriteList()
            self.background_list.append(bg_sprite)
        except Exception as e:
            print(f"Attention : Impossible de charger le fond marin ({e}).")
            self.background_list = None

        # 4. CALCUL DES ÉCHELLES INTERNES
        padding_x = 100
        padding_y = 100

        # On utilise current_width et current_height ici aussi !
        self.scale_x = (current_width - (padding_x * 2)) / map_width_units
        self.scale_y = (current_height - (padding_y * 2)) / map_height_units

        map_center_x = (self.min_x + self.max_x) / 2
        map_center_y = (self.min_y + self.max_y) / 2

        self.offset_x = (current_width / 2) - (map_center_x * self.scale_x)
        self.offset_y = (current_height / 2) - (map_center_y * self.scale_y)

        # 5. CALCUL DYNAMIQUE DU RENDU VISUEL
        self.base_radius = max(8, min(25, int(min(self.scale_x, self.scale_y) / 4)))
        self.dynamic_font = max(7, min(12, int(self.scale_x / 8)))
        self.dynamic_text_width = max(45, int(self.scale_x * 0.9))

        # --- CHARGEMENT DES ICONES (SPRITES) ---
        self.icon_list = arcade.SpriteList()

        try:
            # On charge les 4 textures
            tex_skull = arcade.load_texture("assets/skull.png")
            tex_rock = arcade.load_texture("assets/reef.png")
            tex_treasure = arcade.load_texture("assets/treasure.png")
            tex_palm = arcade.load_texture("assets/palm.png")  # <-- Le Palmier

            for zone_name, zone_obj in self.sim.map_graph.zones.items():
                screen_x, screen_y = self._get_screen_coords(zone_obj.x, zone_obj.y)
                icon = None

                # Règle 1 : Le Trésor à l'arrivée
                if zone_obj.is_end:
                    icon = arcade.Sprite(tex_treasure)

                # Règle 2 : La Tête de Mort pour les impasses
                elif zone_obj.zone == "blocked" or "dead" in zone_name:
                    icon = arcade.Sprite(tex_skull)
                    icon.color = arcade.color.DIM_GRAY

                # Règle 3 : Le Rocher abrupt pour les zones ralenties
                elif zone_obj.zone == "restricted":
                    icon = arcade.Sprite(tex_rock)

                # Règle 4 : Le Palmier pour toutes les autres îles !
                # (On l'exclut juste du Hub de départ pour que le port d'attache reste bien lisible)
                elif not zone_obj.is_start:
                    icon = arcade.Sprite(tex_palm)

                if icon:
                    icon.center_x = screen_x
                    icon.center_y = screen_y

                    # ASTUCE : On réduit un tout petit peu le multiplicateur pour le palmier (1.1)
                    # afin qu'il ne masque pas complètement le beau fond couleur sable (WHEAT).
                    # Les autres icônes gardent leur taille imposante (1.4).
                    scale_multiplier = 1.1 if icon.texture == tex_palm else 1.4
                    icon.scale = (self.base_radius * scale_multiplier) / icon.width

                    self.icon_list.append(icon)

        except Exception as e:
            print(f"Info : Images d'icônes manquantes dans assets/. ({e})")

        # --- NOUVEAU : CHARGEMENT DE LA FLOTTE (SPRITES) ---
        self.ship_list = arcade.SpriteList()

        try:
            tex_ship = arcade.load_texture("assets/ship.png")

            # On cherche le port de départ pour y placer notre navire de test
            for zone_name, zone_obj in self.sim.map_graph.zones.items():
                if zone_obj.is_start:
                    screen_x, screen_y = self._get_screen_coords(zone_obj.x, zone_obj.y)

                    ship = arcade.Sprite(tex_ship)
                    ship.center_x = screen_x
                    ship.center_y = screen_y

                    target_width = max(55, self.base_radius * 6)
                    ship.scale = target_width / ship.width

                    self.ship_list.append(ship)
                    # On casse la boucle, un seul bateau de test nous suffit pour voir le rendu !
                    break

        except Exception as e:
            print(f"Info : Image du navire (ship.png) absente dans assets/. ({e})")

        # --- À RAJOUTER À LA FIN DE __init__ ---

        # 1. Gestionnaire d'interface pour la carte
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # --- BLOC DU BOUTON CORRIGÉ ---

        # 1. Gestionnaire d'interface pour la carte
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Layout d'ancrage pour positionner notre bouton de rebrousse-chemin
        self.anchor_layout = arcade.gui.UIAnchorLayout()

        button_style = {
            "normal": {
                "bg": arcade.color.COOL_GREY,       # Vrai bleu-gris doux campanule
                "fg": arcade.color.BLACK,           # Texte noir pour la lisibilité
            },
            "hover": {
                "bg": arcade.color.CORNFLOWER_BLUE, # Bleu un peu plus soutenu au survol
                "fg": arcade.color.WHITE,
            },
            "press": {
                "bg": arcade.color.DARK_BLUE,
                "fg": arcade.color.WHITE,
            }
        }

        # Création du bouton
        back_button = arcade.gui.UIFlatButton(text="<- Menu", width=180, style=button_style)

        # FIX : On lie le clic à une vraie méthode de classe via une fonction lambda
        back_button.on_click = lambda event: self.go_back_to_menu()

        # On l'ancre en haut à gauche
        self.anchor_layout.add(child=back_button, anchor_x="left", anchor_y="top", align_x=20, align_y=-20)
        self.manager.add(self.anchor_layout)

    def _get_screen_coords(self, zone_x: float, zone_y: float) -> tuple[float, float]:
        screen_x = zone_x * self.scale_x + self.offset_x
        screen_y = zone_y * self.scale_y + self.offset_y
        return screen_x, screen_y

    def go_back_to_menu(self) -> None:
        """Désactive l'interface de la carte et retourne au menu principal."""
        self.manager.disable()

        # Import local pour éviter l'import cyclique fatal
        from menu_view import MenuView

        # On bascule sur la vue du menu
        self.window.show_view(MenuView())

    def on_draw(self) -> None:
        """Méthode de rendu appelée à chaque frame (60 FPS)."""
        self.clear()

       # --- COUCHE 0 : L'ARRIÈRE-PLAN ---
        # Doit IMPÉRATIVEMENT être dessiné en premier !
        if getattr(self, "background_list", None):
            self.background_list.draw()

        # --- COUCHE 1 : LES ROUTES ---
        displayed_links = set()
        for zone_name in self.sim.map_graph.graph_adj:
            neighbors = self.sim.map_graph.get_neighbours(zone_name)
            zone_from = self.sim.map_graph.zones[zone_name]

            for neighbor_name in neighbors:
                link_key = tuple(sorted([zone_name, neighbor_name]))
                if link_key not in displayed_links:
                    zone_to = self.sim.map_graph.zones[neighbor_name]
                    start_x, start_y = self._get_screen_coords(zone_from.x, zone_from.y)
                    end_x, end_y = self._get_screen_coords(zone_to.x, zone_to.y)

                    arcade.draw_line(
                        start_x, start_y, end_x, end_y,
                        arcade.color.STEEL_BLUE, line_width=3
                    )
                    displayed_links.add(link_key)

        ## --- COUCHE 2 & 3 : LES ÎLES (CERCLES) ET LES TEXTES ---
        for zone_name, zone_obj in self.sim.map_graph.zones.items():
            screen_x, screen_y = self._get_screen_coords(zone_obj.x, zone_obj.y)

            # Assignation des couleurs (Palette "Archipel doux")
            if zone_obj.is_start:
                color = arcade.color.LAVENDER_PINK        # Végétation luxuriante (Départ)
                radius = self.base_radius
            elif zone_obj.is_end:
                color = arcade.color.GREEN_YELLOW     # Eaux calmes d'une lagune (Arrivée)
                radius = self.base_radius
            elif zone_obj.zone == "blocked" or "dead" in zone_name:
                color = arcade.color.LIGHT_SLATE_GRAY   # Rocher volcanique stérile (Impasse)
                radius = int(self.base_radius * 0.7)
            elif zone_obj.zone == "restricted":
                color = arcade.color.CADET_GREY        # Banc de corail dangereux (Restreint)
                radius = int(self.base_radius * 0.8)
            elif zone_obj.zone == "priority":
                color = arcade.color.AQUAMARINE         # Courant marin clair (Prioritaire)
                radius = int(self.base_radius * 0.8)
            else:
                color = arcade.color.WHEAT              # Sable chaud (Îlot standard)
                radius = int(self.base_radius * 0.8)

            # Remplacement de l'ONYX (noir pur agressif) par un gris sombre adouci
            outline_color = arcade.color.DIM_GRAY

            # Dessin du cercle parfait
            arcade.draw_circle_filled(screen_x, screen_y, radius, color)
            arcade.draw_circle_outline(screen_x, screen_y, radius, outline_color, 2)

            # Formatage du texte
            current_ships = self.sim.hub_occupancy[zone_name]
            display_name = zone_name.replace('_', '\n')

            if "dead" in zone_name or zone_obj.zone == "blocked":
                label_text = f"{display_name}"
            else:
                label_text = f"{display_name}\n({current_ships}s)"

            # Positionnement du texte (Alternance X)
            text_margin = radius + 6
            if int(zone_obj.x) % 2 == 0:
                text_y = screen_y + text_margin
                vertical_anchor = "bottom"
            else:
                text_y = screen_y - text_margin
                vertical_anchor = "top"

            # Rendu typographique (on utilise un gris sombre mat pour le texte)
            arcade.draw_text(
                label_text,
                x=screen_x,
                y=text_y,
                color=arcade.color.DARK_SLATE_GRAY,
                font_size=self.dynamic_font,
                anchor_x="center",
                anchor_y=vertical_anchor,
                multiline=True,
                width=self.dynamic_text_width,
                align="center"
            )

            # (Fin de la boucle for des zones et des textes...)

        # (Fin de ton code existant...)

        # --- COUCHE 4 : DESSIN DES ICONES (Palmiers, Trésors...) ---
        if hasattr(self, "icon_list"):
            self.icon_list.draw()

        # --- COUCHE 5 : LES BATEAUX ---
        # Impérativement à la fin pour qu'ils naviguent par-dessus l'eau et les îles !
        if hasattr(self, "ship_list"):
            self.ship_list.draw()

        if hasattr(self, "manager"):
            self.manager.draw()
