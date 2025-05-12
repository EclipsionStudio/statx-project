import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams
import numpy as np
from io import BytesIO


def create_dynamic_diagram(nicknames, values, parameter):
    font_path = "./fonts/CascadiaCode.ttf"
    font_prop = font_manager.FontProperties(fname=font_path)
    rcParams['font.family'] = font_prop.get_name()

    # динамические размеры
    base_height = 4.5
    height_per_element = 0.6
    fig_height = max(base_height, len(nicknames) * height_per_element)
    max_value = max(values) if values else 0
    value_offset = max_value * 0.08

    plt.figure(facecolor='#1d2223', figsize=(10, fig_height))
    ax = plt.gca()
    ax.set_facecolor('#1d2223')

    # расположение элементов
    y_spacing = 0.8
    y_positions = np.arange(len(nicknames)) * y_spacing
    bar_height = 0.35

    # автонастройки
    label_size = 14 if len(nicknames) < 15 else 10
    value_fontsize = label_size - 2

    # создание столбцов
    bars = ax.barh(
        y=y_positions,
        width=values,
        height=bar_height,
        color="#fd630f",
        tick_label=nicknames
    )

    # добавление линий и значений
    for bar in bars:
        x_val = bar.get_width()
        y_center = bar.get_y() + bar.get_height()/2

        ax.plot(
            [x_val, x_val + value_offset*0.3],
            [y_center, y_center],
            color='white',
            linewidth=1.5,
            solid_capstyle='round'
        )

        ax.text(
            x_val + value_offset*0.5,
            y_center,
            f'{x_val:.0f}',
            color='white',
            va='center',
            ha='left',
            fontsize=value_fontsize,
            fontweight='bold'
        )

    # настройка осей
    ax.set_xlim(right=max_value + value_offset)
    ax.tick_params(axis='both', colors='white', labelsize=label_size)

    for spine in ax.spines.values():
        spine.set_visible(False) if spine.spine_type in [
            'top', 'right'] else spine.set_color('white')

    # заголовок
    plt.title(
        parameter.replace('_', ' ').title(),
        pad=20,
        color='white',
        fontsize=17,
        fontweight='bold'
    )

    plt.tight_layout(pad=2.5)

    # сохранение в байтовый буфер
    buf = BytesIO()
    plt.savefig(
        buf,
        format='png',
        dpi=100 if len(nicknames) < 20 else 150,
        bbox_inches='tight'
    )
    plt.close()

    # возврат байтов
    buf.seek(0)
    return buf.getvalue()


if __name__ == "__main__":
    # дебаг
    create_dynamic_diagram(
        ['m0nesy', 'donk666'],
        [87, 92],
        'Headhots Percents'
    )
