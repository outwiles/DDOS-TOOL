"""
DDOS-TOOL — AASHU banner

Author / Developer / Admin / Owner: Aashu
GitHub:  @outwiles
Telegram: @outwiles
Email:   outwiles@proton.me

License: MIT
"""

try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init()
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False


def render():
    title = "AASHU"
    tagline = "DDOS-TOOL"
    author = "Author / Developer / Admin / Owner: Aashu"
    contact = "Telegram: @outwiles | GitHub: @outwiles | Email: outwiles@proton.me"

    if HAS_COLOR:
        print()
        print(Fore.CYAN + Style.BRIGHT + f"  {title}" + Style.RESET_ALL)
        print(Fore.CYAN + f"  {tagline}" + Style.RESET_ALL)
        print()
        print(Fore.GREEN + f"  {author}" + Style.RESET_ALL)
        print(Fore.YELLOW + f"  {contact}" + Style.RESET_ALL)
        print()
    else:
        print()
        print(f"  {title}")
        print(f"  {tagline}")
        print()
        print(f"  {author}")
        print(f"  {contact}")
        print()


if __name__ == "__main__":
    render()
