# CIS450-demo

## Introduction

This repo illustrates best practice README file generation.

## Projects

OpenCV image processing demos.

### Edge Detection

This project demonstrates edge detection using OpenCV. Edge detection converts a color image into a line drawing by finding locations where the brightness changes rapidly.

The program first converts each color image to grayscale. It then uses Gaussian blur to reduce noise and Sobel operators to calculate the changes in the image in the X and Y directions. The gradient magnitude is then thresholded to create the edges.

The edge image is then blended with the original color image. The `blend` setting controls how much of the edge image is mixed with the original image. The `thresh` setting controls which edges are included, and the `blur` setting controls how much the image is smoothed before edge detection.

### Images

The original images are stored in the `W5A-Images` directory. The resulting edge images are saved in the `edges` directory using the `.edges.jpg` suffix.

## Edge Detection Settings

| Image       | Blend | Threshold | Blur |
| ----------- | ----: | --------: | ---: |
| art.png     |    46 |        79 |   15 |
| frog.png    |    41 |        76 |    7 |
| map.png     |    18 |         2 |    7 |
| pokemon.png |    48 |        75 |    9 |
| sunset.png  |    25 |        57 |    3 |

## Matplotlib Copilot Evaluation

This project demonstrates using GitHub Copilot and the Matplotlib source code to trace what happens when `plt.plot(x, y)` is called.

### What This Plot Does

In `matplotlib-copilot-eval/plotter.py`, the code sets:

* `x` to `[0, 1, 2, 3, 4]`
* `y` to `[0, 1, 4, 9, 16]`

It then calls `plt.plot(x, y)` to create a line plot using the points:

* `(0, 0)`
* `(1, 1)`
* `(2, 4)`
* `(3, 9)`
* `(4, 16)`

These points follow the equation `y = x²`, so the resulting graph forms an upward-curving parabola. The `plt.show()` function displays the graph.

### Matplotlib Function Call Trace

By following the function definitions in Matplotlib with GitHub Copilot and Shift-clicking through the source code, I traced the main path of `plt.plot(x, y)`:

```text
plt.plot(x, y)
      ↓
gca().plot(...)
      ↓
Axes.plot(...)
      ↓
_get_lines(...)
      ↓
add_line(line)
```

### `plt.plot`

`plt.plot` is the pyplot interface used to create a line plot. It accepts the x and y data along with optional formatting and other keyword arguments.

The function gets the current Axes and calls the Axes object's `plot` method. This means that `plt.plot` provides a convenient interface while the actual plotting work is handled by the Axes object.

### `gca().plot`

`gca()` means "get current Axes." It obtains the current Axes object where the data will be plotted.

The `plot` method of that Axes object is then called with the x and y data. This passes the plotting request from the pyplot interface to the underlying Axes implementation.

### `Axes.plot`

`Axes.plot` is the main plotting implementation. It accepts x and y data, optional format strings, and additional properties such as color, marker, and line style.

The function processes the plotting arguments and uses:

```python
lines = [*self._get_lines(self, *args, data=data, **kwargs)]
```

`_get_lines` converts the plotting arguments into one or more `Line2D` objects. A `Line2D` object represents the line and contains information needed to display it, such as its coordinates and visual properties.

The function then adds each created line to the Axes:

```python
for line in lines:
    self.add_line(line)
```

Finally, `Axes.plot` can autoscale the x and y axes and returns the created list of `Line2D` objects.

### `add_line`

`add_line` receives a `Line2D` object created by `Axes.plot` and adds it to the Axes.

First, it checks that the object is a `Line2D`:

```python
_api.check_isinstance(mlines.Line2D, line=line)
```

It then sets the artist properties and clipping path and updates the Axes' data limits.

The line is added to the Axes' collection of child artists with:

```python
self._children.append(line)
```

The function also marks the Axes as needing to be redrawn and enables autoscaling for the line. Finally, it returns the `Line2D` object.

In simple terms, `add_line` takes the line object created by `Axes.plot` and makes it part of the Axes so Matplotlib can include it when the figure is rendered.

### What I Learned

Tracing `plt.plot(x, y)` showed me that a simple plotting command involves several layers of Matplotlib code. The `pyplot` interface provides an easy way to create a graph, but the request is eventually passed to an `Axes` object.

`Axes.plot` processes the data and creates `Line2D` objects. The `add_line` function then adds those objects to the Axes. Matplotlib can later use these artist objects when rendering the figure.

Using GitHub Copilot and following the actual Matplotlib source code helped me understand what happens behind a simple `plt.plot(x, y)` command instead of treating it as a single operation.

## Resources

<img src="opencv-logo.png" alt="OpenCV logo" width="150" />

[OpenCV](https://opencv.org/)
