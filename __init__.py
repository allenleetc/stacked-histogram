"""
Example panels.

| Copyright 2017-2024, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
import os

import fiftyone.operators as foo
import fiftyone.operators.types as types
from fiftyone import ViewField as F


class StackedHistogramExample(foo.Panel):
    @property
    def config(self):
        return foo.PanelConfig(
            name="example_stacked_histogram",
            label="Example: Stacked Histogram",
        )

    def on_load(self, ctx):
        # Get target field
        target_field = (
            ctx.panel.state.target_field or "ground_truth.detections.label"
        )
        ctx.panel.state.target_field = target_field

        # Compute target histogram for current dataset
        counts = ctx.dataset.count_values(target_field)
        keys, values = zip(*sorted(counts.items(), key=lambda x: x[0]))

        # Store as panel data for efficiency
        ctx.panel.data.histogram = [{"x": keys, "y": values, "type": "bar"},
                                    {"x": keys, "y": 2*values, "type": "bar"}]
        #ctx.panel.data.histogram = [hdata, {"x": keys, "y": values, "type": "bar"}]

        # Launch panel in a horizontal split view
        ctx.ops.split_panel("example_interactive_plot", layout="horizontal")

    def on_change_view(self, ctx):
        # Update histogram when current view changes
        self.on_load(ctx)

    def on_histogram_click(self, ctx):
        # The histogram bar that the user clicked
        x = ctx.params.get("x")

        # Create a view that matches the selected histogram bar
        field = ctx.panel.state.target_field
        view = _make_matching_view(ctx.dataset, field, x)

        # Load view in App
        if view:
            ctx.ops.set_view(view)

    def reset(self, ctx):
        ctx.ops.clear_view()
        self.on_load(ctx)

    def render(self, ctx):
        panel = types.Object()

        panel.plot(
            "histogram",
            layout={
                "title": {
                    "text": "Interactive Histogram Stacked",
                    "xanchor": "center",
                    "yanchor": "top",
                    "automargin": True,
                },
                "xaxis": {"title": "Labels"},
                "yaxis": {"title": "Count"},
                "barmode": "stack"
            },
            on_click=self.on_histogram_click,
            width=100,
        )

        panel.btn(
            "reset",
            label="Reset Chart",
            on_click=self.reset,
            variant="contained",
        )

        return types.Property(
            panel,
            view=types.GridView(
                align_x="center",
                align_y="center",
                orientation="vertical",
                height=100,
                width=100,
                gap=2,
                padding=0,
            ),
        )


def _make_matching_view(dataset, field, value):
    if field.endswith(".label"):
        root_field = field.split(".")[0]
        return dataset.filter_labels(root_field, F("label") == value)
    elif field == "tags":
        return dataset.match_tags(value)
    else:
        return dataset.match(F(field) == value)




def register(p):
    p.register(StackedHistogramExample)
