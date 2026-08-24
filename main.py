import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.popup import Popup


class FoundationApp(App):
    def build(self):
        Window.softinput_mode = "below_target"

        root = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(6))

        title = Label(
            text="Foundation Bearing Capacity",
            size_hint_y=None, height=dp(42),
            font_size="19sp"
        )
        root.add_widget(title)

        scroll = ScrollView()
        form = GridLayout(cols=2, spacing=dp(6), padding=dp(4),
                          size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))

        self.inputs = {}

        def add_label(text):
            form.add_widget(Label(text=text, size_hint_y=None, height=dp(40)))

        def add_input(key, default=""):
            w = TextInput(text=str(default), multiline=False,
                          size_hint_y=None, height=dp(40))
            self.inputs[key] = w
            form.add_widget(w)

        form.add_widget(Label(text="Foundation type", size_hint_y=None, height=dp(40)))
        self.tof = Spinner(text="1 - Single", values=("1 - Single", "2 - Strip", "3 - Mat"),
                           size_hint_y=None, height=dp(40))
        form.add_widget(self.tof)

        add_label("L/B ratio")
        add_input("LoB", "1.0")

        add_label("Footing depth D (m)")
        add_input("D")

        add_label("Soil cohesion Cu (kPa)")
        add_input("Cu")

        add_label("Friction angle φ (degrees)")
        add_input("phi")

        add_label("Soil unit weight γ (kN/m³)")
        add_input("Gama")

        form.add_widget(Label(text="Elastic modulus input", size_hint_y=None, height=dp(40)))
        self.fix = Spinner(text="1 - Average value",
                           values=("1 - Average value", "2 - Layer values"),
                           size_hint_y=None, height=dp(40))
        form.add_widget(self.fix)

        add_label("Elastic modulus Es (kPa)")
        add_input("Es")

        add_label("Number of layers")
        add_input("nol", "1")

        self.layer_box = GridLayout(cols=2, spacing=dp(4), size_hint_y=None)
        self.layer_box.bind(minimum_height=self.layer_box.setter("height"))

        # Layer fields (initially one layer; app adds more as requested)
        self.layer_lengths = []
        self.layer_moduli = []
        self.rebuild_layers(1)

        form.add_widget(Label(text="Layer inputs", size_hint_y=None, height=dp(40)))
        form.add_widget(self.layer_box)

        scroll.add_widget(form)
        root.add_widget(scroll)

        buttons = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        calc = Button(text="Calculate")
        calc.bind(on_press=self.calculate)
        layers = Button(text="Update layers")
        layers.bind(on_press=self.update_layer_count)
        buttons.add_widget(layers)
        buttons.add_widget(calc)
        root.add_widget(buttons)

        self.status = Label(text="Enter the parameters and press Calculate.",
                            size_hint_y=None, height=dp(40))
        root.add_widget(self.status)

        self.result_box = BoxLayout(orientation="vertical", size_hint_y=None)
        self.result_box.bind(minimum_height=self.result_box.setter("height"))
        result_scroll = ScrollView(size_hint_y=0.45)
        result_scroll.add_widget(self.result_box)
        root.add_widget(result_scroll)

        return root

    def rebuild_layers(self, n):
        self.layer_box.clear_widgets()
        self.layer_lengths = []
        self.layer_moduli = []
        for i in range(n):
            self.layer_box.add_widget(Label(text=f"Layer {i+1} length (m)",
                                            size_hint_y=None, height=dp(38)))
            a = TextInput(text="1.0", multiline=False,
                          size_hint_y=None, height=dp(38))
            self.layer_box.add_widget(a)
            self.layer_lengths.append(a)

            self.layer_box.add_widget(Label(text=f"Layer {i+1} Es (kPa)",
                                            size_hint_y=None, height=dp(38)))
            b = TextInput(text="10000", multiline=False,
                          size_hint_y=None, height=dp(38))
            self.layer_box.add_widget(b)
            self.layer_moduli.append(b)

    def update_layer_count(self, *_):
        try:
            n = max(1, int(self.inputs["nol"].text))
            self.rebuild_layers(n)
            self.status.text = f"{n} layer(s) ready."
        except Exception:
            self.status.text = "Enter a valid integer for number of layers."

    def calculate(self, *_):
        try:
            ToF = int(self.tof.text.split()[0])
            LoB = 1.0 if ToF == 1 else float(self.inputs["LoB"].text)

            delta = 0.03 if ToF <= 2 else 0.04
            D = float(self.inputs["D"].text)
            Cu = float(self.inputs["Cu"].text)
            phi_deg = float(self.inputs["phi"].text)
            Gama = float(self.inputs["Gama"].text)
            fix = int(self.fix.text.split()[0])

            if fix == 1:
                Es = float(self.inputs["Es"].text)
            else:
                lengths = [float(x.text) for x in self.layer_lengths]
                moduli = [float(x.text) for x in self.layer_moduli]
                Es = sum(np.array(lengths) * np.array(moduli)) / sum(lengths)

            mu = 0.3
            ss = 0.025 * Es
            FOS = 3.0
            qd = Gama * D
            phi = np.radians(phi_deg)

            # Preserve the equations from the uploaded program.
            if abs(np.tan(phi)) < 1e-12:
                Nq = 1.0
                Nc = 5.14
                Nr = 0.0
            else:
                Nq = np.exp(np.pi * np.tan(phi)) * (
                    np.tan(np.pi / 4 + phi / 2)
                ) ** 2
                Nc = (Nq - 1) * (1 / np.tan(phi))
                Nr = 2 * (Nq + 1) * np.tan(phi)

            if ToF < 2.5:
                nn, dd = 37, 5
            else:
                nn, dd = 370, 40

            B_values, qal_values, ksv_values = [], [], []

            for j in range(1, nn + 1):
                B = 0.3 + j / 10
                L = B * LoB

                if D / B <= 1.0:
                    dq = 1.0 + 2 * np.tan(phi) * (1 - np.sin(phi)) ** 2 * (D / B)
                    dc = dq - (1 - dq) / (Nc * np.tan(phi)) if abs(np.tan(phi)) > 1e-12 else 1.0
                    dr = 1.0
                else:
                    dq = 1.0 + 2 * np.tan(phi) * (1 - np.sin(phi)) ** 2 * np.arctan(D / B)
                    dc = dq - (1 - dq) / (Nc * np.tan(phi)) if abs(np.tan(phi)) > 1e-12 else 1.0
                    dr = 1.0

                Sc = 1.0 + (Nq / Nc) * (B / L)
                Sq = 1.0 + (B / L) * np.tan(phi)
                Sr = 1.0 - 0.4 * (B / L)

                if abs(phi) < 1e-12:
                    Sc = 0.2 * (B / L)
                if Sr < 0.6:
                    Sr = 0.6

                qu = Cu * Nc * dc * Sc + qd * Nq * dq * Sq + \
                     0.5 * Gama * B * Nr * dr * Sr
                qa = qu / FOS

                M = L / B
                N = 10
                m = 4
                a0 = M * np.log(
                    (1 + np.sqrt(M**2 + 1)) *
                    np.sqrt(M**2 + N**2) /
                    (M * (1 + np.sqrt(M**2 + N**2 + 1)))
                )
                a1 = np.log(
                    ((M + np.sqrt(M**2 + 1)) * np.sqrt(1 + N**2)) /
                    (M + np.sqrt(M**2 + N**2 + 1))
                )
                a2 = M / (N * np.sqrt(M**2 + N**2 + 1))
                I1 = (a0 + a1) / np.pi
                I2 = N * np.arctan(a2) / (2 * np.pi)
                Is = I1 + (1 - 2 * mu) / (1 - mu) * I2
                IF = (
                    1.001 + 1.194 * (D / B) + 0.842 * (L / B) + 7.63 * mu
                ) / (
                    1 + 3.738 * (D / B) + 0.839 * (L / B) + 7.3 * mu
                )
                q0 = delta / (m * B / 2 * (1 - mu**2) * Is * IF / Es)
                qal = min(qa, q0)

                B_values.append(B)
                qal_values.append(qal)
                ksv_values.append(Es / (B * (1 - mu)**2))

            self.show_results(Es, max(qal_values), B_values, qal_values,
                              ksv_values, dd)

        except Exception as exc:
            self.status.text = "Calculation error."
            Popup(title="Input error",
                  content=Label(text=str(exc)),
                  size_hint=(0.9, 0.4)).open()

    def show_results(self, Es, max_qal, B, qal, ksv, dd):
        self.result_box.clear_widgets()
        self.result_box.add_widget(Label(
            text=f"Equivalent Es: {Es:,.2f} kPa\n"
                 f"Maximum allowable bearing capacity: {max_qal:,.2f} kPa",
            size_hint_y=None, height=dp(65)
        ))

        for title, x, y, xlabel, ylabel, filename in [
            ("Allowable Bearing Capacity", B, qal,
             "Width of Foundation (m)", "Allowable Bearing Capacity (kPa)",
             "/tmp/bearing.png"),
            ("Modulus of Subgrade Reaction", B, ksv,
             "Width of Foundation (m)", "Modulus of Subgrade Reaction (kN/m³)",
             "/tmp/subgrade.png")
        ]:
            plt.figure(figsize=(7, 4))
            plt.plot(x, y, "--.")
            plt.grid(True)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            if title == "Allowable Bearing Capacity":
                plt.axis([0, dd, 0, 0.025 * Es])
            else:
                plt.xlim([0, dd] if dd == 5 else [5, dd])
            plt.tight_layout()
            plt.savefig(filename, dpi=130)
            plt.close()

            self.result_box.add_widget(Label(
                text=title, size_hint_y=None, height=dp(32)
            ))
            self.result_box.add_widget(Image(
                source=filename, size_hint_y=None, height=dp(240)
            ))

        self.status.text = "Calculation complete."


if __name__ == "__main__":
    FoundationApp().run()
