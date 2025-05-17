import matplotlib
from matplotlib import font_manager, rcParams
import numpy as np
from io import BytesIO
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def create_dynamic_diagram(nicknames, values, parameter):
    font_path = "./fonts/CascadiaCode.ttf"
    font_prop = font_manager.FontProperties(fname=font_path)
    rcParams['font.family'] = font_prop.get_name()

    base_height = 4.5
    height_per_element = 0.6
    fig_height = max(base_height, len(nicknames) * height_per_element)
    max_value = max(values) if values else 0
    value_offset = max_value * 0.08

    plt.figure(facecolor='#1d2223', figsize=(10, fig_height))
    ax = plt.gca()
    ax.set_facecolor('#1d2223')

    y_spacing = 0.8
    y_positions = np.arange(len(nicknames)) * y_spacing
    bar_height = 0.35

    label_size = 14 if len(nicknames) < 15 else 10
    value_fontsize = label_size - 2

    bars = ax.barh(
        y=y_positions,
        width=values,
        height=bar_height,
        color="#fd630f",
        tick_label=nicknames
    )

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

    ax.set_xlim(right=max_value + value_offset)
    ax.tick_params(axis='both', colors='white', labelsize=label_size)

    for spine in ax.spines.values():
        spine.set_visible(False) if spine.spine_type in [
            'top', 'right'] else spine.set_color('white')

    plt.title(
        parameter.replace('_', ' ').title(),
        pad=20,
        color='white',
        fontsize=17,
        fontweight='bold'
    )

    plt.tight_layout(pad=2.5)

    buf = BytesIO()
    plt.savefig(
        buf,
        format='png',
        dpi=100 if len(nicknames) < 20 else 150,
        bbox_inches='tight'
    )
    plt.close()

    buf.seek(0)
    return buf.getvalue()


def info_diag(data):
    try:
        player_name = data.get("player", "Unknown Player")
        stats = data.get("stats", {}).get("player", {})

        if not stats:
            print("No player stats found in the data.")
            return None

        nicknames = list(stats.keys())
        values = [float(stats[key]) for key in nicknames]
        parameter = f"'{player_name}' player stats"

        return create_dynamic_diagram(nicknames, values, parameter)

    except (ValueError, TypeError) as e:
        print(f"Error processing data: {e}")
        return None

def compare_diag(data1, data2):
    try:
        player_name1 = data1.get("player", "Player 1")
        player_name2 = data2.get("player", "Player 2")
        stats1 = data1.get("stats", {}).get("player", {})
        stats2 = data2.get("stats", {}).get("player", {})

        if not stats1 or not stats2:
            print("Missing stats data for comparison.")
            return None

        nicknames = list(set(stats1.keys()) | set(stats2.keys()))
        values1 = [float(stats1.get(key, 0)) for key in nicknames]
        values2 = [float(stats2.get(key, 0)) for key in nicknames]

        return create_comparison_diagram(
            nicknames, 
            values1, 
            values2, 
            f"Comparison: '{player_name1}' vs '{player_name2}'"
        )

    except (ValueError, TypeError) as e:
        print(f"Error processing data: {e}")
        return None

def create_comparison_diagram(nicknames, values1, values2, parameter):
    font_path = "./fonts/CascadiaCode.ttf"
    font_prop = font_manager.FontProperties(fname=font_path)
    rcParams['font.family'] = font_prop.get_name()

    base_height = 5
    height_per_element = 0.8
    fig_height = max(base_height, len(nicknames) * height_per_element)
    max_value = max(max(values1), max(values2)) if values1 and values2 else 0
    value_offset = max_value * 0.12


    plt.figure(facecolor='#1d2223', figsize=(12, fig_height))
    ax = plt.gca()
    ax.set_facecolor('#1d2223')

    y_spacing = 1.0
    y_positions = np.arange(len(nicknames)) * y_spacing
    bar_height = 0.35 

    color1 = "#fd630f" 
    color2 = "#3498db"

    bars1 = ax.barh(
        y=y_positions - bar_height/2,
        width=values1,
        height=bar_height,
        color=color1,
        label=f"{parameter.split(':')[1].split('vs')[0].strip()}"
    )
    
    bars2 = ax.barh(
        y=y_positions + bar_height/2,
        width=values2,
        height=bar_height,
        color=color2,
        label=f"{parameter.split(':')[1].split('vs')[1].strip()}"
    )

    for bar in bars1:
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
            fontsize=10,
            fontweight='bold'
        )

    for bar in bars2:
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
            fontsize=10,
            fontweight='bold'
        )

    ax.set_xlim(right=max_value + value_offset)
    ax.tick_params(axis='both', colors='white', labelsize=12)
    
    ax.set_yticks(y_positions)
    ax.set_yticklabels(nicknames)

    for spine in ax.spines.values():
        spine.set_visible(False) if spine.spine_type in ['top', 'right'] else spine.set_color('white')

    plt.title(
        parameter.replace('_', ' ').title(),
        pad=20,
        color='white',
        fontsize=17,
        fontweight='bold'
    )

    plt.tight_layout(pad=2.5)

    buf = BytesIO()
    plt.savefig(
        buf,
        format='png',
        dpi=100 if len(nicknames) < 20 else 150,
        bbox_inches='tight'
    )
    plt.close()

    buf.seek(0)
    return buf.getvalue()