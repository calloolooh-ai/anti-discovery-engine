import * as d3 from "d3";

export const communityColors = d3.schemeTableau10 as readonly string[];
export const gapColor = "#f59e0b";
export const regularEdgeColor = "#374151";
export const backgroundColor = "#0f0f0f";
export const surfaceColor = "#1a1a1a";
export const textColor = "#e5e7eb";
export const mutedTextColor = "#6b7280";
export const borderColor = "#2d2d2d";
export const accentHover = "#fbbf24";

export function getCommunityColor(communityId: number): string {
  return communityColors[communityId % communityColors.length];
}
