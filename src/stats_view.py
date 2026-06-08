import arcade
import arcade.gui


class StatsView(arcade.View):
    def __init__(self, stats, nb_drones: int):
        """
        Initialise la vue des statistiques.
        :param stats: L'objet SimulationStats rempli par la simulation.
        :param nb_drones: Le nombre total de drones (pour les moyennes).
        """
        super().__init__()
        self.stats = stats
        self.nb_drones = max(1, nb_drones)  # Évite la division par zéro

        # --- CALCUL DES MÉTRIQUES ---
        total_moves = sum(self.stats.moves_per_turn)
        self.avg_moves_per_turn = total_moves / max(1, self.stats.total_turns)

        total_active_turns = sum(self.stats.active_turns_per_drone.values())
        self.avg_turns_per_drone = total_active_turns / self.nb_drones

        # --- INTERFACE UTILISATEUR (Bouton) ---
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Création du bouton de retour au menu
        self.v_box = arcade.gui.UIBoxLayout()
        menu_button = arcade.gui.UIFlatButton(text="<- RETURN", width=150)
        self.v_box.add(menu_button)
        # Ce qui se passe quand on clique sur le bouton
        @menu_button.event("on_click")
        def on_click_menu(event):
            self.manager.disable()
            # Nettoyage du terminal
            print("\033[H\033[2J", end="")
            print("========================================")
            print("             MENU PRINCIPAL             ")
            print("========================================\n")

            # Retour au menu
            from src.menu_view import MenuView
            self.window.show_view(MenuView())

        anchor_layout = arcade.gui.UIAnchorLayout()

        anchor_layout.add(
            child=self.v_box,
            anchor_x="left",
            anchor_y="top",
            align_y=0
        )
        self.manager.add(anchor_layout)

    def on_show_view(self):
        """Appelé automatiquement quand cette vue s'affiche."""
        arcade.set_background_color(arcade.color.CATALINA_BLUE)

    def on_draw(self):
        """Dessine les textes à l'écran."""
        self.clear()

        center_x = self.window.width / 2
        start_y = self.window.height - 120

        # Titre
        arcade.draw_text("MISSION REPORT", center_x, start_y,
                         arcade.color.CARIBBEAN_GREEN, font_size=40, anchor_x="center", bold=True)

        arcade.draw_text("Simulation completed successfully.", center_x, start_y - 60,
                         arcade.color.LIGHT_GRAY, font_size=18, anchor_x="center")

        # --- AFFICHAGE DES STATS ---
        stats_text = (
            f"Final score (total number of turns) : {self.stats.total_turns}\n\n"
            f"Number of drones : {self.nb_drones}\n"
            f"Total path cost : {self.stats.total_path_cost}\n\n"
            f"Number of drones moved per turn : {self.avg_moves_per_turn:.2f}\n"
            f"Average number of turns per drone : {self.avg_turns_per_drone:.2f}"
        )

        arcade.draw_text(stats_text, center_x, start_y - 200,
                         arcade.color.CELESTE, font_size=22, anchor_x="center",
                         align="center", multiline=True, width=600)

        # Dessine le bouton
        self.manager.draw()
