from pathlib import Path
import arcade
import arcade.gui
from map_display import MapView

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_list = None

        # --- GESTIONNAIRE D'INTERFACE ---
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.anchor_layout = arcade.gui.UIAnchorLayout()
        self.manager.add(self.anchor_layout)

        # --- LA VRAIE PALETTE HAUTE VISIBILITÉ (Clés 'bg' et 'fg' valides) ---
        self.button_style = {
            "normal": {
                "bg": arcade.color.ANTIQUE_BRASS,          # Vrai Or ambré
                "fg": arcade.color.BLACK,          # Texte noir pour le contraste
            },
            "hover": {
                "bg": arcade.color.BRONZE,           # Éclat doré au survol
                "fg": arcade.color.BLACK,
            },
            "press": {
                "bg": arcade.color.BROWN_NOSE,     # Bronze foncé lors du clic
                "fg": arcade.color.WHITE,
            }
        }

        self.show_main_menu()

    def on_show_view(self):
        """Appelé automatiquement quand le menu s'affiche."""
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        try:
            bg_sprite = arcade.Sprite("assets/menu_background.jpeg")
            bg_sprite.center_x = self.window.width / 2
            bg_sprite.center_y = self.window.height / 2
            bg_sprite.width = self.window.width
            bg_sprite.height = self.window.height

            self.background_list = arcade.SpriteList()
            self.background_list.append(bg_sprite)
        except Exception as e:
            print(f"Attention : Impossible de charger le fond du menu ({e}).")
            self.background_list = None

    def show_main_menu(self):
        """Affiche les boutons de difficulté alignés en bas."""
        self.anchor_layout.clear()

        h_box = arcade.gui.UIBoxLayout(vertical=False, space_between=20)
        difficulties = ["easy", "medium", "hard", "challenger"]

        for diff in difficulties:
            button = arcade.gui.UIFlatButton(text=diff.capitalize(), width=180, height=50, style=self.button_style)
            button.on_click = lambda event, d=diff: self.show_map_menu(d)
            h_box.add(button)

        # Alignement horizontal centré, calé tout en bas
        self.anchor_layout.add(child=h_box, anchor_x="center_x", anchor_y="bottom", align_y=60)

    def show_map_menu(self, difficulty: str):
        """Affiche les sous-cartes également en bas."""
        self.anchor_layout.clear()
        h_box = arcade.gui.UIBoxLayout(vertical=False, space_between=15)

        map_dir = Path("maps") / difficulty
        map_files = [f for f in map_dir.iterdir() if not f.name.startswith(".")] if map_dir.exists() else []

        if not map_files:
            label = arcade.gui.UILabel(text="Aucune carte trouvée", font_size=16, font_color=arcade.color.WHITE)
            h_box.add(label)
        else:
            for map_path in sorted(map_files):
                button = arcade.gui.UIFlatButton(text=map_path.stem, width=180, height=45, style=self.button_style)
                button.on_click = lambda event, p=map_path: self.start_simulation(p)
                h_box.add(button)

        # Bouton Retour (Rouge vif pour casser le style et sauter aux yeux)
        back_style = {
            "normal": {"bg_color": (190, 40, 40), "font_color": arcade.color.WHITE},
            "hover": {"bg_color": (255, 60, 60), "font_color": arcade.color.WHITE},
            "press": {"bg_color": (100, 20, 20), "font_color": arcade.color.WHITE}
        }

        back_button = arcade.gui.UIFlatButton(text="<- Retour", width=150, height=45, style=back_style)
        back_button.on_click = lambda event: self.show_main_menu()
        h_box.add(back_button)

        self.anchor_layout.add(child=h_box, anchor_x="center_x", anchor_y="bottom", align_y=60)

    def start_simulation(self, map_path: Path):
        self.manager.disable()
        simulation_view = MapView(map_file_path=map_path)
        self.window.show_view(simulation_view)

    def on_draw(self):
        self.clear()

        if self.background_list:
            self.background_list.draw()

        # --- LE TITRE MAJESTUEUX DÉCALÉ À GAUCHE ---
        arcade.draw_text(
            "Fly-In",
            x=80,
            y=self.window.height - 140,
            color=arcade.color.WHITE,
            font_size=80,
            anchor_x="left",
            bold=True,
            font_name=("Garamond", "Palatino", "serif")
        )

        self.manager.draw()
