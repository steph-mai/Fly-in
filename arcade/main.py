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
        self.player_sprite = None
        self.boat2 = None
        self.boat3 = None

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
        self.player_sprite = arcade.Sprite("kenney_watercraft-pack/Previews/ship-ocean-liner.png", SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 64
        self.player_list.append(self.player_sprite)

        self.boat2 = arcade.Sprite("kenney_watercraft-pack/Previews/boat-tug-a.png", SPRITE_SCALING_PLAYER)
        self.boat2.center_x = 250
        self.boat2.center_y = 500
        self.player_list.append(self.boat2)

        self.boat3 = arcade.Sprite("kenney_watercraft-pack/Previews/boat-sail-a.png", SPRITE_SCALING_PLAYER)
        self.boat3.center_x = 600
        self.boat3.center_y = 256
        self.player_list.append(self.boat3)


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
        self.player_sprite.center_y += 1
        self.player_sprite.center_x += 1

        # Si le joueur sort par la droite, on le remet à gauche
        if self.player_sprite.left > SCREEN_WIDTH:
            self.player_sprite.right = 0
        # Si le joueur sort par le haut, on le remet en bas
        if self.player_sprite.bottom > SCREEN_HEIGHT:
            self.player_sprite.top = 0

        # --- Gestion du Bateau 2 (vers la droite) ---
        self.boat2.center_x += 2
        if self.boat2.left > SCREEN_WIDTH:
            self.boat2.right = 0

        # --- Gestion du Bateau 3 (diagonale haut-gauche) ---
        self.boat3.center_y += 1
        self.boat3.center_x -= 1

        # S'il sort par le haut
        if self.boat3.bottom > SCREEN_HEIGHT:
            self.boat3.top = 0
        # S'il sort par la gauche
        if self.boat3.right < 0:
            self.boat3.left = SCREEN_WIDTH




def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
