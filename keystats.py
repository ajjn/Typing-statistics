import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
import time

matplotlib.use('TkAgg')


class KeyStats(tk.Tk):
    def __init__(self):
        def next_row():
            if not hasattr(self, 'row'):
                self.row = 0
            else:
                self.row += 1
            return self.row

        super().__init__()
        self.title("Key stats")
        tk.Label(self, text="Click button to start and Enter to stop recording").grid(
            row=next_row(),
            columnspan=2,
            padx=10,
            pady=10
        )
        self.status_text = tk.Label(self, foreground="red", text="")
        self.status_text.grid(row=next_row(), columnspan=2, padx=10, pady=10)
        self.stats_text = tk.Label(self, text="")
        self.stats_text.grid(row=next_row(), columnspan=2, padx=10, pady=10)
        tk.Button(self, text="Start recording", command=self.toggle_status).grid(
            row=next_row(),
            column=0,
            padx=10,
            pady=10
        )
        tk.Button(self, text="Start simulation", command=self.simulate).grid(
            row=self.row,
            column=1,
            padx=10,
            pady=10
        )
        self.textbox = tk.Text(self)
        self.textbox.grid(row=next_row(), columnspan=2, padx=10, pady=10)

        self.bind("<Key>", self.key)
        self.times = []
        self.chars = []
        self.recording_status = False
        self.after(500, self.update_status)

    def update_status(self):
        if self.recording_status:
            self.status_text['text'] = 'Recording'
        else:
            self.status_text['text'] = ''

        self.update()
        self.after(500, self.update_status)

    def initialize(self):
        self.textbox.delete(1.0, tk.END)
        self.chars = []
        self.times = []

    def toggle_status(self):
        self.recording_status = not self.recording_status
        if not self.recording_status:
            self.times.append(time.time())
            self.plot_histogram()
            self.plot_char_stats()
            plt.show()

        else:
            print("Started recording")
            self.initialize()
            self.textbox.focus_set()

    def plot_char_stats(self):
        if len(self.chars) < 2:
            return
        # Generate char dictionary
        intervals = self.times[1:] - self.times[:-1]
        char_dict = {}
        for i in range(len(self.chars)):
            char = self.chars[i]
            if repr(char) in char_dict:
                char_dict[repr(char)].add_interval(intervals[i])
            else:
                char_dict[repr(char)] = Char(repr(char), intervals[i])

        # Build bar plot of chars
        means = []
        stds = []
        labels = []
        for k, v in char_dict.items():
            labels.append(v.get_symbol())
            means.append(v.get_mean())
            stds.append(v.get_std())

        ind = np.arange(len(labels))  # the x locations for the bars
        width = 0.7
        fig, ax = plt.subplots()
        ax.bar(ind, means, width, color='r', yerr=stds)

        ax.set_ylabel('Mean interval [ms]')
        ax.set_title('Key specific interval lengths')
        plt.xticks(ind + 0.5*width, labels, rotation=60)

    def plot_histogram(self):
        if len(self.chars) < 2:
            self.initialize()
            print("Press keys at least twice")
            return
        self.times = np.array(self.times)
        intervals = self.times[1:] - self.times[:-1]
        print("Mean key press interval: {}".format(np.mean(intervals)))
        print("Standard deviation of key press interval: {}".format(np.std(intervals)))
        orig_mu = np.mean(intervals)
        orig_sigma = np.std(intervals)
        intervals = np.log(intervals)
        mu = np.mean(intervals)
        sigma = np.std(intervals)
        print("You typed {} characters.".format(len(intervals)+1))
        print("Mean of log of key press interval: {}".format(mu))
        print("Standard deviation of log of key press interval: {}".format(sigma))
        n, bins, patches = plt.hist(
            np.exp(intervals),
            facecolor='green',
            alpha=0.75
        )
        plt.plot(bins, self.lognorm_pdf(bins, mu, sigma), 'r--', linewidth=1)
        plt.xlabel('Key press interval [s]')
        plt.ylabel('Normalized frequency')
        plt.title("Key press interval stats: mean = {:.2f} s, std = {:.2f} s".format(
            orig_mu,
            orig_sigma
        ))
        plt.grid(True)

    def lognorm_pdf(self, x, mu, sigma):
        y = 1 / (x * sigma * np.sqrt(2 * np.pi)) * np.exp(-(np.log(x) - mu) ** 2 / (2 * sigma ** 2))
        return y

    def update_stats_text(self):
        if len(self.times) < 2:
            return
        times = np.array(self.times)
        intervals = times[1:] - times[:-1]
        orig_mu = np.mean(intervals)
        orig_sigma = np.std(intervals)
        self.stats_text['text'] = "Chars: {:d}, Mean: {:d} ms, Std: {:d} ms".format(
            len(self.times),
            int(1000 * orig_mu),
            int(1000 * orig_sigma)
        )

    def simulate(self):
        times = np.array(self.times)
        intervals = times[1:] - times[:-1]
        intervals = np.log(intervals)
        mu = np.mean(intervals)
        sigma = np.std(intervals)
        intervals = np.exp(sigma * np.random.randn(len(self.chars) - 1) + mu)
        self.textbox.delete(1.0, tk.END)
        self.textbox.insert(tk.END, self.chars[0])
        self.update()
        for i in range(len(intervals)):
            time.sleep(intervals[i])
            # Backspace
            if self.chars[i+1] == chr(8):
                self.textbox.delete('%s-2c' % tk.END, tk.END)
            else:
                self.textbox.insert(tk.END, self.chars[i+1])
            self.update()

    def key(self, event):
        if event.char == '\r':
            self.toggle_status()
        elif self.recording_status:
            self.record(event.char)

    def record(self, key):
        self.times.append(time.time())
        self.chars.append(key)
        self.update_stats_text()


class Char:
    def __init__(self, symbol, interval):
        self.intervals = [interval]
        self.symbol = symbol

    def get_symbol(self):
        return str(self.symbol) + ' ' + str(len(self.get_intervals()))

    def get_intervals(self):
        return self.intervals

    def add_interval(self, interval):
        self.intervals.append(interval)

    def get_mean(self):
        # Value in milliseconds
        return 1000 * np.mean(np.array(self.get_intervals()))

    def get_std(self):
        # Value in milliseconds
        return 1000 * np.std(np.array(self.get_intervals()))


app = KeyStats()
app.mainloop()
