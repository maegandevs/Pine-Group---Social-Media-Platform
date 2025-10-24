import tkinter as tk
from tkinter import ttk

# scroll


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        canvas = tk.Canvas(self, borderwidth=0, highllightthickness=0)
        scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        # bind the frame resize to update scroll region
        self.scrollable_frame.bind(
            "<configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # create window inside canvas
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # layout
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Navigation Bar")
        self.geometry("800x600")

        # nav bar - fixed at the top
        navbar = tk.Frame(self, bg="#1944f1", height=50)
        navbar.grid(row=0, column=0, sticky="ew")
        navbar.grid_propagate(False)  # so it doesn't resize

        # create a container frame to hold the other frames
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Create frames for all pages
        self.frames = {}
        for F in (HomePage, ProfilePage, SearchPage, Settings):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Nav Buttons
        buttons = [
            ("Home", lambda: self.show_frame(HomePage)),
            ("Profile", lambda: self.show_frame(ProfilePage)),
            ("Search", lambda: self.show_frame(SearchPage)),
            ("Settings", lambda: self.show_frame(Settings)),
        ]
        for text, command in buttons:
            btn = tk.Button(
                navbar,
                text=text,
                command=command,
                bg="light gray",  # look for a pale gray
                fg="white",
                font=("Arial", 12, "bold"),
                relief="flat",
                activebackground="#1abc9c",
                activeforeground="white",
                padx=20,
                pady=10

            )
            btn.pack(side="left", padx=5, pady=5)

        self.show_frame(HomePage)

    def show_frame(self, page_class):
        """raise the selected frame to the top"""
        frame = self.frames[page_class]
        frame.tkraise()


# individual page classes
class HomePage(tk.Frame):
    def __init__(self, parent, controller):  # master: Misc | None = ..., cnf: dict[str, Any] | None = ..., *, background: _Color = ..., bd: _ScreenUnits = ..., bg: _Color = ..., border: _ScreenUnits = ..., borderwidth: _ScreenUnits = ..., class_: str = ..., colormap: Literal["new", ""] | Misc = ..., container: bool = ..., cursor: _Cursor = ..., height: _ScreenUnits = ..., highlightbackground: _Color = ..., highlightcolor: _Color = ..., highlightthickness: _ScreenUnits = ..., name: str = ..., padx: _ScreenUnits = ..., pady: _ScreenUnits = ..., relief: _Relief = ..., takefocus: _TakeFocusValue = ..., visual: str | tuple[str, int] = ..., width: _ScreenUnits = ...) -> None:
        super().__init__(parent)  # master, cnf, background=background, bd, bg, border, borderwidth, class_, colormap, container, cursor, height, highlightbackground, highlightcolor, highlightthickness, name, padx, pady, relief, takefocus, visual, width)
        label = tk.Label(self, text="Welcome to Dallas College's Social Media", font=(
            "Arial", 14)).pack(pady=20)
        label.pack(pady=10, padx=10)


class ProfilePage(tk.Frame):
    def __init__(self, parent, controller):  # master: Misc | None = ..., cnf: dict[str, Any] | None = ..., *, background: _Color = ..., bd: _ScreenUnits = ..., bg: _Color = ..., border: _ScreenUnits = ..., borderwidth: _ScreenUnits = ..., class_: str = ..., colormap: Literal["new", ""] | Misc = ..., container: bool = ..., cursor: _Cursor = ..., height: _ScreenUnits = ..., highlightbackground: _Color = ..., highlightcolor: _Color = ..., highlightthickness: _ScreenUnits = ..., name: str = ..., padx: _ScreenUnits = ..., pady: _ScreenUnits = ..., relief: _Relief = ..., takefocus: _TakeFocusValue = ..., visual: str | tuple[str, int] = ..., width: _ScreenUnits = ...) -> None:
        super().__init__(parent)  # master, cnf, background=background, bd, bg, border, borderwidth, class_, colormap, container, cursor, height, highlightbackground, highlightcolor, highlightthickness, name, padx, pady, relief, takefocus, visual, width)
        label = tk.Label(self, text="Welcome to the Profile page",
                         font=("Arial", 14)).pack(pady=20)
        label.pack(pady=10, padx=10)


class SearchPage(tk.Frame):
    def __init__(self, parent, controller):  # master: Misc | None = ..., cnf: dict[str, Any] | None = ..., *, background: _Color = ..., bd: _ScreenUnits = ..., bg: _Color = ..., border: _ScreenUnits = ..., borderwidth: _ScreenUnits = ..., class_: str = ..., colormap: Literal["new", ""] | Misc = ..., container: bool = ..., cursor: _Cursor = ..., height: _ScreenUnits = ..., highlightbackground: _Color = ..., highlightcolor: _Color = ..., highlightthickness: _ScreenUnits = ..., name: str = ..., padx: _ScreenUnits = ..., pady: _ScreenUnits = ..., relief: _Relief = ..., takefocus: _TakeFocusValue = ..., visual: str | tuple[str, int] = ..., width: _ScreenUnits = ...) -> None:
        super().__init__(parent)  # master, cnf, background=background, bd, bg, border, borderwidth, class_, colormap, container, cursor, height, highlightbackground, highlightcolor, highlightthickness, name, padx, pady, relief, takefocus, visual, width)
        label = tk.Label(self, text="Searching for Friends? Start here!", font=(
            "Arial", 14)).pack(pady=20)
        label.pack(pady=10, padx=10)


class Settings(tk.Frame):
    def __init__(self, parent, controller):  # master: Misc | None = ..., cnf: dict[str, Any] | None = ..., *, background: _Color = ..., bd: _ScreenUnits = ..., bg: _Color = ..., border: _ScreenUnits = ..., borderwidth: _ScreenUnits = ..., class_: str = ..., colormap: Literal["new", ""] | Misc = ..., container: bool = ..., cursor: _Cursor = ..., height: _ScreenUnits = ..., highlightbackground: _Color = ..., highlightcolor: _Color = ..., highlightthickness: _ScreenUnits = ..., name: str = ..., padx: _ScreenUnits = ..., pady: _ScreenUnits = ..., relief: _Relief = ..., takefocus: _TakeFocusValue = ..., visual: str | tuple[str, int] = ..., width: _ScreenUnits = ...) -> None:
        super().__init__(parent)  # master, cnf, background=background, bd, bg, border, borderwidth, class_, colormap, container, cursor, height, highlightbackground, highlightcolor, highlightthickness, name, padx, pady, relief, takefocus, visual, width)
        label = tk.Label(self, text="Settings",
                         font=("Arial", 14)).pack(pady=20)
        label.pack(pady=10, padx=10)
