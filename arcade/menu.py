# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  menu.py                                           :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: stmaire <stmaire@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/05/19 16:14:52 by stmaire         #+#    #+#               #
#  Updated: 2026/05/19 17:03:11 by stmaire         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import arcade
import arcade.gui

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Fly-in Menu"


class MainView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()

        switch_menu_button = arcade.gui.UIFlatButton(text="Pause", width=250)

        # Initialise the button with an on_click event.
        @switch_menu_button.event("on_click")
        def on_click_switch_button(event):
            # Passing the main view into menu view as an argument.
            menu_view = MenuView(self)
            self.window.show_view(menu_view)

        # Use the anchor to position the button on the screen.
        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())

        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=switch_menu_button,
        )

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLUE_SAPPHIRE)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()


class MenuView(arcade.View):
    """Main menu view class."""

    def __init__(self, main_view):
        super().__init__()

        self.manager = arcade.gui.UIManager()

        resume = arcade.gui.UIFlatButton(text="Resume", width=150)
        start_new_game = arcade.gui.UIFlatButton(text="Start New Game", width=150)
        volume = arcade.gui.UIFlatButton(text="Volume", width=150)
        options = arcade.gui.UIFlatButton(text="Options", width=150)

        exit = arcade.gui.UIFlatButton(text="Exit", width=320)

        # Initialise a grid in which widgets can be arranged.
        self.grid = arcade.gui.UIGridLayout(
            column_count=2, row_count=3, horizontal_spacing=20, vertical_spacing=20
        )

        # Adding the buttons to the layout.
        self.grid.add(resume, column=0, row=0)
        self.grid.add(start_new_game, column=1, row=0)
        self.grid.add(volume, column=0, row=1)
        self.grid.add(options, column=1, row=1)
        self.grid.add(exit, column=0, row=2, column_span=2)

        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())

        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.grid,
        )

        self.main_view = main_view
        

    def on_hide_view(self):
        # Disable the UIManager when the view is hidden.
        self.manager.disable()

    def on_show_view(self):
        """This is run once when we switch to this view"""

        arcade.set_background_color([rgb - 50 for rgb in arcade.color.BLIZZARD_BLUE])

        self.manager.enable()

    def on_draw(self):
        """Render the screen."""

        # Clear the screen
        self.clear()
        self.manager.draw()


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
    main_view = MainView()
    window.show_view(main_view)
    arcade.run()


if __name__ == "__main__":
    main()
