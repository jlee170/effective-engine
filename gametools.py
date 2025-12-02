"""
GAMETOOLS.PY

A set of functions to make AIST2110's games AWESOME!!
"""

from typing import Literal
import sys
from time import sleep
from textwrap import fill, dedent
from collections.abc import Iterable
from shutil import get_terminal_size
from beaupy import Config, select, prompt
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel


Config.raise_on_interrupt = True

_console = None

MAX_REASONABLE_WIDTH = 120


def _get_terminal_width(max_term_width: int = MAX_REASONABLE_WIDTH):
    try:
        term_width = get_terminal_size().columns
    except:
        return max_term_width
    if max_term_width == 0:
        max_term_width = 9999
    return min(max_term_width, term_width)


def set_terminal_width(width=None):
    """Change the maximum width of a line of text.

    Gametools will automatically manage wrapping of long paragraphs for you. By
    default, wrapping occurs at the full width of the terminal up to a max of
    120 characters. Generally anything wider than this is more difficult to
    read, but if needed you can pass a value to this function to change this
    default width. Calling it with no arguments will reset it to the default.
    """
    if not width:
        width = _get_terminal_width()
    global _console
    _console = Console(width=width)


set_terminal_width()


def write(
    content="",
    prefix="",
    indent="",
    style="",
    justify="left",
    bulleted=False,
    numbered=False,
    boxed=False,
    end="\n",
):
    """Display a passage of text or a list of items to the screen.

    This is similar to python's built-in print() function, but with a lot of
    extra bells and whistles.

    In addition to allowing for colored and formatted text, it will
    automatically wrap long passages of text to fit properly in the terminal
    window.

    It will also behave differently depending on whether it is displaying a
    single string of text or if the content is a list of strings.

    Most of the time you will call this method with a passage of text to be
    printed to the screen. Text can contain markup to alter the color and
    display characteristics, but is otherwise just a string.

    However, if you pass a list of strings, write() will process each item in
    the list as though it was passed individually to the write function.
    Additionally, if you set either the bulleted or numbered arguments to True
    write() will prefixing each item with a bullet or an automatically
    incremented number.

    You can pass an optional, named argument to specify the display style of the
    passage (described elsewhere).

    You can pass an optional named arguments to set a `prefix` string to prepend
    to the first line in the text passage and an `indent` string to prepend to
    all following lines. This is a more flexible alternative to setting bulleted
    = True, which just sets prefix to `" • "` and indent to `"    "`.

    Additionally, you can pass an optional, named argument to specify whether to
    justify the text in the passage. Valid values are "left" (default),
    "center", "right" and "full".

    Finally, you can pass a boolean argument specifying that you wish to draw a
    box around the content.
    """
    if bulleted:
        prefix = " • "
        indent = "   "
    if numbered:
        prefix = " 1 "
        indent = "   "

    line_width = _console.width
    if boxed:
        line_width -= 4

    to_print = " "

    if not isinstance(content, str) and isinstance(content, Iterable):
        lines = []
        line_count = 1
        for item in content:
            item_text = str(item)
            if numbered:
                prefix = f"{line_count:>2} "
            formatted_item = fill(
                dedent(item_text).strip(),
                width=line_width,
                initial_indent=prefix,
                subsequent_indent=indent,
            )
            lines.append(formatted_item)
            line_count += 1
        to_print = "\n".join(lines)
    else:
        text = str(content)
        to_print = fill(
            dedent(text).strip(),
            width=line_width,
            initial_indent=prefix,
            subsequent_indent=indent,
        )
        if not to_print:
            to_print = " "

    if boxed:
        to_print = Panel(to_print, width=_console.width, box=box.ROUNDED)

    _console.print(to_print, style=style, justify=justify, end=end)


def write_md(content, style="", boxed=False):
    """Format and print a passage of markdown formatted text.

    This is a special version of the write() function that accepts a string of
    markdown-formatted text. It uses a pre-defined set of styles to display the
    text to the screen in a consistent format.

    The optional named style argument can be passed to set the foreground and
    background colors.

    Setting boxed=True will display the content inside of a box.
    """
    to_print = Markdown(dedent(content).strip())

    if boxed:
        to_print = Panel(to_print, width=_console.width, box=box.ROUNDED)
    elif " on " in style:
        to_print = Panel(
            to_print, width=_console.width, box=box.SIMPLE, padding=0, expand=True
        )

    _console.print(to_print, style=style)


def get_input(
    prompt_text: str = "Enter Choice",
    choices: Iterable[str] = None,
    show_choices: bool = True,
    min_length: int = 0,
) -> str:
    """Prompt a user for input and optionally validate it.

    If a list of choices is provided, a user's input will be validated to insure
    it is one of the members of the list.

    By default, if the list of choices is provided, these are displayed to the
    user. This behavior can be altered by setting the show_choices named
    argument to False.

    If no choices are provided, by default any text, including an empty string,
    are allowed. To require the user to enter something, you can specify a
    min_length using the optional named argument.
    """
    if choices and show_choices:
        prompt_text += " \[" + ",".join(choices) + "]"

    lower_choices = []
    if choices:
        lower_choices = [choice.lower() for choice in choices]

    def _valid(val):
        if choices:
            return val.lower() in lower_choices
        else:
            return len(val) >= min_length

    user_text = ""
    prompt_prefix = ""
    while not _valid(user_text):
        try:
            user_text = prompt(
                prompt_prefix + prompt_text, initial_value=user_text
            ).strip()
            prompt_prefix = "[b white on red]INVALID INPUT | TRY AGAIN[/]\n"
        except KeyboardInterrupt:
            sys.exit(1)

    write(f"{prompt_text}: {user_text}")
    return user_text


def get_choice(all_choices: Iterable[str], hidden_choices: Iterable[int] = None) -> int:
    """Allow the user to select from a list of choices.

    The user is presented with a navigable list of choices. Using the up/down
    arrow keys, the user selects an item and presses Enter to select.

    The _index_ of the selected item is returned.

    If desired, specific indexes can be hidden from a user. This may be useful
    if you wish to use the same get_choice() and if/elif/else logic, but you
    need to alter the available choices for a user based on some game state
    change.
    """
    # Hide hidden indexes
    if hidden_choices:
        for idx in hidden_choices:
            if not isinstance(idx, int):
                raise ValueError("All hidden choices must be integers")
        if max(hidden_choices) >= len(all_choices):
            raise ValueError(
                "At least one hidden choice is out of range of all_choices"
            )
        hidden_choices = sorted(set(hidden_choices))
        choices = [
            str(all_choices[idx])
            for idx in range(len(all_choices))
            if idx not in hidden_choices
        ]
    else:
        choices = [str(all_choices[idx]) for idx in range(len(all_choices))]

    choice = None
    while choice is None:
        try:
            choice = select(options=choices, return_index=True)
        except KeyboardInterrupt:
            sys.exit(1)

    # Adjust choice to account for hidden indexes
    if hidden_choices:
        for idx in hidden_choices:
            if idx <= choice:
                choice += 1

    write(f"[i]choice:[/] [b]{all_choices[choice]}[/]")
    return choice


def clear():
    """Clears the terminal window."""
    _console.clear()
    

def pause(message="Press any key to continue...", style="", justify="left"):
    """Displays a message and waits for a user to press any key.

    You can customize the message displayed to the user. By default it is "Press
    any key to continue...".

    This function takes optional, named arguments for style and justify that are
    identical to those used in write().
    """
    _console.print(message, style=style, justify=justify)

    import platform

    if platform.system() == "Windows":
        import msvcrt

        code = ord(msvcrt.getwch())
        if code in (3, 26):
            exit(0)
        print()
    else:
        import os

        code = os.system(f"/bin/bash -c 'read -s -n 1'")
        if code != 0:
            exit(0)
        print()


SpinnerNames = Literal[
    "aesthetic",
    "arc",
    "arrow",
    "arrow2",
    "arrow3",
    "balloon",
    "balloon2",
    "betaWave",
    "bounce",
    "bouncingBall",
    "bouncingBar",
    "boxBounce",
    "boxBounce2",
    "christmas",
    "circle",
    "circleHalves",
    "circleQuarters",
    "clock",
    "dots",
    "dots10",
    "dots11",
    "dots12",
    "dots2",
    "dots3",
    "dots4",
    "dots5",
    "dots6",
    "dots7",
    "dots8",
    "dots8Bit",
    "dots9",
    "dqpb",
    "earth",
    "flip",
    "grenade",
    "growHorizontal",
    "growVertical",
    "hamburger",
    "hearts",
    "layer",
    "line",
    "line2",
    "material",
    "monkey",
    "moon",
    "noise",
    "pipe",
    "point",
    "pong",
    "runner",
    "shark",
    "simpleDots",
    "simpleDotsScrolling",
    "smiley",
    "squareCorners",
    "squish",
    "star",
    "star2",
    "toggle",
    "toggle10",
    "toggle11",
    "toggle12",
    "toggle13",
    "toggle2",
    "toggle3",
    "toggle4",
    "toggle5",
    "toggle6",
    "toggle7",
    "toggle8",
    "toggle9",
    "triangle",
    "weather",
]


def spin(seconds: float, message: str = "", spinner: SpinnerNames = None):
    """Sleep for a specified period, optionally showing a message and animation.

    Neither the message nor the spinner arguments is required. If both are
    omitted, this behaves identically to time.sleep().

    If a message argument is supplied, then the message will be displayed until
    the timer expires, at which time it will disappear.

    If a spinner argument is supplied, it must be one of the valid spinner
    values enumerated elsewhere. The spinner animation will display to the left
    of any message and will also disappear once the timer expires.
    """
    with _console.status(message, spinner=spinner):
        sleep(seconds)
