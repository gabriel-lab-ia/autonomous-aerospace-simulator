import matplotlib.image as mpimg
import matplotlib.pyplot as plt

from aerospace_sim.visualization.dark_style import save_dark_figure, style_axis


def test_dark_style_saves_black_background(tmp_path) -> None:
    output_path = tmp_path / "dark_plot.png"
    figure, axis = plt.subplots(figsize=(3, 2))
    axis.plot([0.0, 1.0], [0.0, 1.0])

    style_axis(axis)
    save_dark_figure(figure, output_path)
    plt.close(figure)

    image = mpimg.imread(output_path)
    red, green, blue = image[0, 0, :3]
    assert red < 0.05
    assert green < 0.05
    assert blue < 0.05
