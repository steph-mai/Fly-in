""" Sprite Sample Program """

import arcade

# --- Constants ---
SPRITE_SCALING_BOX = 0.5
SPRITE_SCALING_PLAYER = 2


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

MOVEMENT_SPEED = 5


class MyGame(arcade.Window):
    """ This class represents the main window of the game. """

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Sprites With waters Example")
    # Sprite lists
        self.player_list = None
        self.water_list = None

        # Set up the player
        self.cake1 = None
        self.cake2 = None
        self.cake3 = None

        # This variable holds our simple "physics engine"
        self.physics_engine = None

    def setup(self):
        # Set the background color
        arcade.set_background_color(arcade.color.BLEU_DE_FRANCE)
        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.water_list = arcade.SpriteList()
        # Reset the score
        self.score = 0

        # Create the player
        self.cake1 = arcade.Sprite("kenney_watercraft-pack/Previews/ship-ocean-liner.png", SPRITE_SCALING_PLAYER)
        self.cake1.center_x = 50
        self.cake1.center_y = 64
        self.player_list.append(self.cake1)

        self.cake2 = arcade.Sprite("arcade/Previews/cake-birthday.png", SPRITE_SCALING_PLAYER)
        self.cake2.center_x = 250
        self.cake2.center_y = 500
        self.player_list.append(self.cake2)

        self.cake3 = arcade.Sprite("kenney_watercraft-pack/Previews/boat-sail-a.png", SPRITE_SCALING_PLAYER)
        self.cake3.center_x = 600
        self.cake3.center_y = 256
        self.player_list.append(self.cake3)


        for x in range(0, 800, 64):
            for y in range(0, 600, 64):
                water = arcade.Sprite("kenney_watercraft-pack/waterTop_high.png", SPRITE_SCALING_BOX)
                water.center_x = x + 32 # On décale de la moitié de la taille du sprite pour centrer
                water.center_y = y + 32
                self.water_list.append(water)


    def on_draw(self):
        # 1. On efface tout
        self.clear()

        # 2. On dessine simplement les listes
        # Arcade gère automatiquement le rendu optimal maintenant
        self.water_list.draw()
        self.player_list.draw()

    def on_update(self, delta_time):
        # --- Gestion du Joueur ---
        self.cake1.center_y += 1
        self.cake1.center_x += 1

        # Si le joueur sort par la droite, on le remet à gauche
        if self.cake1.left > SCREEN_WIDTH:
            self.cake1.right = 0
        # Si le joueur sort par le haut, on le remet en bas
        if self.cake1.bottom > SCREEN_HEIGHT:
            self.cake1.top = 0

        # --- Gestion du Bateau 2 (vers la droite) ---
        self.cake2.center_x += 2
        if self.cake2.left > SCREEN_WIDTH:
            self.cake2.right = 0

        # --- Gestion du Bateau 3 (diagonale haut-gauche) ---
        self.cake3.center_y += 1
        self.cake3.center_x -= 1

        # S'il sort par le haut
        if self.cake3.bottom > SCREEN_HEIGHT:
            self.cake3.top = 0
        # S'il sort par la gauche
        if self.cake3.right < 0:
            self.cake3.left = SCREEN_WIDTH




def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
