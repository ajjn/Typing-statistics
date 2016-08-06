import tkinter as tk
from numpy import sqrt
from numpy import log as ln
from numpy import pi
from numpy import exp
import numpy as np
import time

class TypingSimulator(tk.Tk):
    def __init__(self):
        super().__init__()

        # Build interface
        row = 0
        tk.Button(self,
                  text="Start simulation",
                  command=self.simulate).grid(row=row,
                                              padx=10,
                                              pady=10)

        self.textbox = tk.Text(self)
        row += 1
        self.textbox.grid(row=row,
                          padx=10,
                          pady=10)

        # Build the texts
        self.texts = []
        self.texts.append(SimulationText("""Typing of text is individual. """,
                                         0.277, 0.23))
        self.texts.append(SimulationText("""Some people type faster, """,
                                         0.06, 0.04))
        self.texts.append(SimulationText("""whereas some quite sloowwly...""",
                                         0.4, 0.3))
        self.texts.append(SimulationText(""" The interval between ket\by presses by human being can be consideeed \b\b\b\bred as a random variable. The interval can be simulated as a variable, whose logarithm is normally distributed. However, I don't know whether this is really true... One should study it... or maybe someone knows it already? Anyway, if you want to find out your typing statistics, you can try this little app. Have fun!""",
                                         0.15, 0.17))
        
    def simulate(self):
        # Clear the text box
        self.textbox.delete(1.0, tk.END)

        # set text and intervals
        whole = ""
        intervals = np.array([])
        for text in self.texts:
            whole += text.get_text()
            intervals = np.concatenate((intervals, self.random_lognormal_delay(text.get_mu(),
                                                                               text.get_sigma(),
                                                                               len(text.get_text()))))


        # Run the simulation
        for i in range(len(whole)):
            # Backspace
            if whole[i] == chr(8):
                self.textbox.delete('%s-2c' % tk.END, tk.END)
            else:
                self.textbox.insert(tk.END, whole[i])
            self.update()
            time.sleep(intervals[i])
            
                

    def random_lognormal_delay(self, m, sd, n):
        # calculate mu and sigma
        mu = ln(m/sqrt(1+sd**2/m**2))
        sigma = sqrt(ln(1+sd**2/m**2))
        return exp(sigma * np.random.randn(n) + mu)
        
class SimulationText:
    def __init__(self, text, mu, sigma):
        self.text = text
        self.mu = mu
        self.sigma = sigma

    def get_text(self):
        return self.text

    def get_mu(self):
        return self.mu

    def get_sigma(self):
        return self.sigma

app = TypingSimulator()
app.mainloop()
