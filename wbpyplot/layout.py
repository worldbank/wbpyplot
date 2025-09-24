import textwrap


def px_to_fig_frac(px, fig, axis="y"):
    dpi = fig.dpi
    size_in = fig.get_size_inches()
    return px / (size_in[1] * dpi) if axis == "y" else px / (size_in[0] * dpi)


def wrap_text(text, max_chars=80):
    return textwrap.fill(text, width=max_chars)


def render_title_subtitle_note(fig, title, subtitle, note, wb_font_sizes, wb_spacing):
    spacing_frac = {k: px_to_fig_frac(v, fig, "y") for k, v in wb_spacing.items()}
    margin_x_frac = px_to_fig_frac(wb_spacing["m"], fig, "x")
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    y_pos = 1.0 - spacing_frac["xl"]

    if title:
        title_text = fig.text(
            margin_x_frac,
            y_pos,
            wrap_text(title, 80),
            fontsize=wb_font_sizes["l"],
            fontweight="bold",
            color="#111111",
            ha="left",
            va="top",
            linespacing=1.2,
        )
        fig.canvas.draw()
        bbox = title_text.get_window_extent(renderer=renderer)
        title_height_frac = bbox.height / (fig.get_size_inches()[1] * fig.dpi)
        y_pos -= title_height_frac + spacing_frac["xxs"]

    if subtitle:
        subtitle_text = fig.text(
            margin_x_frac,
            y_pos,
            wrap_text(subtitle, 100),
            fontsize=wb_font_sizes["m"],
            fontweight="normal",
            color="#666666",
            ha="left",
            va="top",
            linespacing=1.2,
        )
        fig.canvas.draw()
        bbox = subtitle_text.get_window_extent(renderer=renderer)
        subtitle_height_frac = bbox.height / (fig.get_size_inches()[1] * fig.dpi)
        y_pos -= subtitle_height_frac + spacing_frac["xl"]

    notes_to_render = []
    if note:
        if isinstance(note, str):
            notes_to_render = [("", note)]
        elif isinstance(note, tuple):
            notes_to_render = [note]
        elif isinstance(note, list):
            notes_to_render = note

    y_note = spacing_frac["xl"]
    line_spacing_frac = spacing_frac["xl"]

    for label, text in notes_to_render:
        x_start = margin_x_frac
        label_artist = fig.text(
            x_start,
            y_note,
            label + " ",
            fontsize=wb_font_sizes["s"],
            fontweight="bold",
            color="#111111",
            ha="left",
            va="bottom",
        )
        fig.canvas.draw()
        bbox_label = label_artist.get_window_extent(renderer=renderer)
        label_width_frac = bbox_label.width / (fig.get_size_inches()[0] * fig.dpi)

        note_artist = fig.text(
            x_start + label_width_frac,
            y_note,
            wrap_text(text, 120),
            fontsize=wb_font_sizes["s"],
            fontweight="normal",
            color="#666666",
            ha="left",
            va="bottom",
        )
        fig.canvas.draw()
        bbox_note = note_artist.get_window_extent(renderer=renderer)
        note_height_frac = bbox_note.height / (fig.get_size_inches()[1] * fig.dpi)

        y_note += note_height_frac + line_spacing_frac

    bottom_space = y_note + spacing_frac["xl"]
    return y_pos, bottom_space, margin_x_frac


def compute_total_bottom_margin(fig, axs, handles, note, note_margin_frac, spacing):
    has_xlabel = any(ax.get_xlabel() for ax in axs)
    xlabel_spacing = (
        px_to_fig_frac(spacing["xl"], fig, axis="y") * 4
        if has_xlabel
        else px_to_fig_frac(spacing["xl"], fig, axis="y") * 2
    )
    legend_spacing_frac = px_to_fig_frac(spacing["xl"], fig, axis="y")

    if handles and not note:
        return (
            legend_spacing_frac
            + px_to_fig_frac(spacing["xl"] * 4, fig, axis="y")
            + xlabel_spacing
        )
    elif handles and note:
        return (
            note_margin_frac
            + legend_spacing_frac
            + px_to_fig_frac(spacing["xl"] * 4, fig, axis="y")
            + xlabel_spacing
        )
    elif note:
        return note_margin_frac + xlabel_spacing
    else:
        return xlabel_spacing
