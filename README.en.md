[中文](README.md) · English

<p align="center">
  <img src="./assets/readme/hero.webp" width="100%" alt="oil-ui: push AI UI design to its limits. A person pins a yellow pushpin to the middle of three previews in different styles">
</p>

<p align="center">
  <a href="https://ui.oiloil.org"><img src="./assets/readme/showcase.webp" width="100%" alt="Gallery highlights: an English learning app, a music year in review, hardware and component library websites, a project management tool, a ride-hailing app, a voice assistant, a checkout flow, and a film camera"></a>
</p>

See more designs at [ui.oiloil.org](https://ui.oiloil.org).

## Method

1. **Identify the category and study its best examples.** Name the product category, find two or three peers with distinctive styles, and examine their choices and reasoning. Decide what to keep and what to change.
2. **Set the tone first.** Use the subject, audience, and brand voice to set five scales: energy, polish, density, visual weight, and seriousness. Turn words like “premium” or “clean” into visible choices: type, spacing, and how much of the page uses color.
3. **Start with something concrete.** Give each direction a specific starting point: a material in a setting, a scene, a character, or the visual language of another field. Draw from the product itself rather than adjectives like “minimal” or “bold.”
4. **Decide what the opening screen is for.** For browsing, shopping, or getting work done, lead with the content itself. For pages meant to persuade, choose the opening layout, wireframe it, then write the copy. Each direction needs a different layout; use a left/right split at most once per round.
5. **Check that the directions differ.** Any two directions may share at most one of four things: layout, typography, color, and key imagery. Place the previews side by side and squint at the opening screens. If their light and dark shapes look too similar, choose a different layout.
6. **Create a memorable moment.** Focus on one or two details: the response to a tap, a successful payment, AI at work, or a 404 page. Keep the rest quiet.
7. **You decide what looks right.** Compare previews on one page, choose a direction, and say exactly what you like and dislike.
8. **Judge the actual screens.** Open the page at desktop and mobile sizes and check screenshots. An independent reviewer who has not seen the work in progress can review it. Finish by simplifying: give each page one focal point and remove unnecessary copy, repeated lines, and extra containers.

Interactions, states, layout, existing project redesigns, and effects such as light trails and dot patterns are covered in [oil-ui-pro](https://ui.oiloil.org/pro/).

## Installation

Send this to an agent that can install skills:

```text
Install this skill for me: https://github.com/oil-oil/oil-ui
```

Or install it from your terminal:

```bash
npx skills add oil-oil/oil-ui
```

No extra setup or dependencies needed. If you already have oil-ui-pro, you don't need this one; installing both makes them compete for the same requests.

Updates are automatic. The agent checks before each task, going online at most once a day. It only reads the public version list on ui.oiloil.org and sends nothing about you. If it cannot update, for example because you are offline or Node.js is missing, it ends its reply with a reminder to run `npx github:oil-oil/oil-cli update oil-ui`. Set `OIL_NO_AUTO_UPDATE=1` for reminders without automatic updates, or `OIL_NO_UPDATE_CHECK=1` to disable checks entirely.

## Usage

Tell your agent what you need, for example:

- “Use oil-ui to explore a few design directions for this course booking product and build pages I can preview.”
- “Create three designs with different typography, colors, and compositions. Put them on a comparison page so I can choose.”
- “Polish this page using the project’s existing design guidelines.”
- “Review this homepage and explain what to change and how. Leave the files untouched.”
- “Recreate this page from the screenshot and add a mobile layout too.”

Share any brand assets, screenshots, or existing project you have. It can start without references and only asks questions when the deliverable is unclear.

## Built-in style comparison page

<p align="center">
  <img src="./assets/readme/proof-mona-lisa.webp" width="100%" alt="Style comparison page: three directions for the same Mona Lisa exhibition page, titled Thirty Centimeters, Extra! 1911, and Sfumato">
</p>

Compare designs side by side as HTML files, images, or running development pages. Put the current version first as a baseline. Switch between desktop and mobile sizes, open previews at actual size, and browse with arrow keys. Click “Select” on your choice, then paste the copied sentence into your agent to continue.

## Open-source and full versions

<p align="center">
  <img src="./assets/readme/proof-van-gogh.webp" width="100%" alt="Full version style comparison page: three directions for a Van Gogh exhibition page, titled To Theo, Brushstrokes, and East Window">
</p>

| | oil-ui | oil-ui-pro |
| --- | :---: | :---: |
| Set the tone, explore distinct directions, define layouts first, and check their differences | ✓ | ✓ |
| Style comparison page | ✓ | ✓ |
| Visual hierarchy, typography, color, and spacing | ✓ | ✓ |
| Memorable moments and scroll storytelling (parallax and continuous shots) | ✓ | ✓ |
| Imagery, assets, and motion | ✓ | ✓ |
| Screenshot recreation, icon library selection, and sample data | ✓ | ✓ |
| Review polished interfaces against the project’s design guidelines | ✓ | ✓ |
| Independent review | One round per stage | Revise and review until 9/10 |
| Check for overlapping directions and have the reviewer complete real tasks | | ✓ |
| Fix common first-draft issues, check AI design defaults, refine details, and simplify | | ✓ |
| Dashboard and tool layouts, with a consistent style throughout the page | | ✓ |
| Interactions, states, layout, and responsive behavior | | ✓ |
| SVG and shader effects: light trails, dot patterns, and flowing gradients | | ✓ |
| Existing project redesigns: audit the UI, capture baselines, and choose a workflow by scope | | ✓ |

The full version is a one-time ¥69 purchase with lifetime updates, available at [ui.oiloil.org/pro](https://ui.oiloil.org/pro/).

## Use with

- [draw-ui](https://github.com/oil-oil/draw-ui): Generate design images first, choose one, then build from it. Try this when code-based iterations keep falling short and your agent can generate images.
- [oil-motion](https://github.com/oil-oil/oil-motion): Turn generated videos or frame sequences into web animation controlled by scrolling or dragging, such as product teardowns or camera fly-throughs. Use it for a striking opening animation.

## License

[MIT](LICENSE)
