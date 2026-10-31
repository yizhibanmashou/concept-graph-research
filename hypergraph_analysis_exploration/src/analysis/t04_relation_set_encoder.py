"""Shared nonlinear set encoder for unpooled T04 relation items."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import torch
from torch import nn


class SharedRelationItemEncoder(nn.Module):
    """Apply one shared nonlinear map per A/B/C/D relation item, then mean-pool."""

    def __init__(self, input_width: int, output_width: int | None = None) -> None:
        super().__init__()
        if input_width < 1 or (output_width is not None and output_width < 1):
            raise ValueError("encoder widths must be positive")
        output_width = output_width or input_width
        self.phi = nn.Sequential(
            nn.Linear(input_width, output_width),
            nn.GELU(),
            nn.Linear(output_width, output_width),
        )

    def forward(self, items: torch.Tensor) -> torch.Tensor:
        if not isinstance(items, torch.Tensor) or items.ndim != 2:
            raise ValueError("relation items must be a rank-2 tensor")
        if items.shape[0] < 1 or items.shape[1] != self.phi[0].in_features:
            raise ValueError("relation item shape is empty or incompatible")
        if not bool(torch.isfinite(items).all().item()):
            raise ValueError("relation items must be finite")
        return self.phi(items).mean(dim=0)


def encode_relation_item_views(
    item_views: Mapping[str, torch.Tensor],
    encoder: SharedRelationItemEncoder,
) -> dict[str, torch.Tensor]:
    """Encode A/B/C/D with the exact same module and parameter set."""
    missing = set("ABCD") - set(item_views)
    if missing:
        raise ValueError("missing A/B/C/D relation item views")
    return {condition: encoder(item_views[condition]) for condition in "ABCD"}
