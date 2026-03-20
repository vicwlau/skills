---
name: refactoring-ui
description: Use this skill when designing or refactoring user interfaces, styling components, or generating CSS. It applies specific principles to improve visual hierarchy, spacing, typography, color, and depth.
---

# Refactoring UI

## When to use this skill

Use this skill when refactoring frontend components, adjusting layout and spacing, or building a color and typography system.

## 1. Hierarchy and Emphasis

- **Size isn't everything**: Rely on font weight and color to establish hierarchy instead of just font size.
- **De-emphasize secondary content**: Use softer colors (lighter greys) and normal font weights for supporting text.
- **Labels are a last resort**: Present data without labels using formatting when possible. If labels are needed, treat them as supporting content and de-emphasize them.
- **Semantics are secondary**: Style actions based on importance. Use solid backgrounds for primary actions, outlines for secondary, and links for tertiary.

## 2. Layout and Spacing

- **Start with too much white space**: Give elements ample room to breathe, then reduce space if necessary.
- **Establish a spacing system**: Limit yourself to a constrained set of values defined in advance (e.g., base 16px multiples) rather than arbitrary pixel values.
- **Avoid ambiguous spacing**: Ensure there is more space _between_ groups of elements than _within_ a group.

## 3. Typography

- **Use a type scale**: Define a restricted set of handcrafted font sizes in advance (e.g., 12px, 14px, 16px, 18px, 20px, 24px).
- **Avoid em units**: Use `px` or `rem` to guarantee strict adherence to the type scale.
- **Line length and height**: Keep paragraphs between 45 and 75 characters per line. Adjust line-height proportionally—narrow content can use 1.5, wide content up to 2.

## 4. Color

- **Use HSL**: Define colors using Hue, Saturation, and Lightness.
- **Define shades up front**: Create a scale of 5-10 shades for primary colors and greys.
- **Saturate extreme lightness**: As a color approaches 0% or 100% lightness, increase the saturation to prevent it from washing out.
- **Warm up greys**: Saturate greys with a bit of a base color (like yellow or blue) to adjust the temperature.

## 5. Depth

- **Emulate a light source**: Use shadows cast directly downwards. For raised elements, lighten the top edge and cast a shadow on the bottom.
- **Use two-part shadows**: Combine a large, soft shadow (direct light) with a tight, dark shadow (ambient light).
- **Overlap elements**: Create depth by overlapping components across background transitions.

## Implementation Example

```tsx
import React from "react";

interface UserProfileProps {
  user_name: string;
  user_email: string;
  is_active: boolean;
}

export const UserProfile: React.FC<UserProfileProps> = ({
  user_name,
  user_email,
  is_active,
}) => {
  return (
    <div className="p-6 max-w-sm mx-auto bg-white rounded-xl shadow-[0_10px_15px_-3px_rgba(0,0,0,0.1),0_4px_6px_-2px_rgba(0,0,0,0.05)] flex items-center space-x-4">
      <div className="flex-shrink-0">
        <div className="h-12 w-12 rounded-full bg-slate-200 border border-slate-300" />
      </div>
      <div>
        <div className="text-xl font-medium text-slate-900">{user_name}</div>
        {/* De-emphasizing labels and secondary content */}
        <p className="text-slate-500">{user_email}</p>
        {is_active && (
          <span className="mt-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
            Active
          </span>
        )}
      </div>
    </div>
  );
};
```
