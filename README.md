[![make.fun](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/c/news-image-20261126)
[![Rank](https://make.fun/badge/news-image-20261126/mrmasudhafej-tech/news-image-20261126/rank.svg)](https://make.fun/c/news-image-20261126)
[![Reward](https://make.fun/badge/news-image-20261126/mrmasudhafej-tech/news-image-20261126/reward.svg)](https://make.fun/c/news-image-20261126)

# The World Today — 26 November 2026

A deterministic newspaper front page summing up the world news of
Thursday 26 November 2026 in a single 1024x1024 image.

`main.py` (Python 3, standard library only) rasterises the page into an RGB
buffer with a hand-authored bitmap font and writes it as a PNG. It reads no
files, uses no network, and takes no input except the output directory, so
two runs write byte-identical bytes.

Run it with:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The output is `out/entry.png`.

## Stories on the page

- **Lead:** the Thanksgiving storm and the postponement of New York's 100th
  Macy's Thanksgiving Day Parade to Saturday, its first postponement ever,
  as a nor'easter brought gusts of up to 65 mph.
- **North Korea:** Kim Jong Un urged wider deployment of tactical nuclear
  weapons, as reported by state media KCNA.
- **Ukraine war:** Ukraine said it struck the Savasleyka airbase east of
  Moscow, damaging five warplanes; Libya said two naval officers died of
  wounds from a Ukrainian drone attack on a Russian warship in Libya.
- **Egypt:** at least 31 people killed and 21 injured in a fuel tanker fire
  on Cairo's Ring Road in Warraq.
- **Trade:** the United States proposed new tariffs on 14 trading partners,
  including China and the EU.
- **Briefs:** the Bank of Korea raised its rate to 3.25%; rescuers searched
  for 13 workers trapped in an illegal gold mine in West Java, Indonesia,
  where 13 bodies were found; ESA's Hera mission revealed a stadium-sized
  crater on the asteroid Dimorphos.

Sources for the stories: Reuters, AP, BBC, Al Jazeera and ESA, as reported
on 26 November 2026. Figures are stated as reported.

## License

MIT — see `LICENSE`.
